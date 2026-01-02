from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Iterable
import xml.etree.ElementTree as ET

import psycopg

from app.core.settings import get_settings, normalize_database_url


@dataclass(frozen=True)
class RssEntry:
    source: str
    headline: str
    url: str
    published_at: datetime


@dataclass(frozen=True)
class FeedConfig:
    source: str
    url: str


def parse_rss(feed_xml: str, source: str) -> list[RssEntry]:
    root = ET.fromstring(feed_xml)
    entries: list[RssEntry] = []
    for item in root.findall(".//item"):
        title = _text(item, "title")
        link = _text(item, "link")
        pub_date = _text(item, "pubDate")
        if not title or not link or not pub_date:
            continue
        published_at = _parse_pub_date(pub_date)
        if published_at is None:
            continue
        entries.append(
            RssEntry(
                source=source,
                headline=normalize_headline(title),
                url=link.strip(),
                published_at=published_at,
            )
        )
    return entries


def normalize_headline(headline: str) -> str:
    return " ".join(headline.strip().split())


def canonical_key(source: str, headline: str, published_at: datetime) -> str:
    normalized = normalize_headline(headline).lower()
    published = published_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{source}:{normalized}:{published}"


def _parse_pub_date(pub_date: str) -> datetime | None:
    try:
        parsed = parsedate_to_datetime(pub_date)
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _text(item: ET.Element, tag: str) -> str:
    element = item.find(tag)
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def insert_events(entries: Iterable[RssEntry]) -> int:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        INSERT INTO macro_events (
            id,
            created_at,
            source,
            headline,
            url,
            published_at,
            status
        )
        VALUES (
            gen_random_uuid(),
            now(),
            %(source)s,
            %(headline)s,
            %(url)s,
            %(published_at)s,
            'new'
        )
        ON CONFLICT (source, headline, published_at) DO NOTHING
    """

    inserted = 0
    with psycopg.connect(database_url) as conn:
        for entry in entries:
            result = conn.execute(
                query,
                {
                    "source": entry.source,
                    "headline": entry.headline,
                    "url": entry.url,
                    "published_at": entry.published_at,
                },
            )
            inserted += result.rowcount or 0
    return inserted


def load_feed_file(path: str) -> str:
    return open(path, "r", encoding="utf-8").read()


def fetch_feed(url: str) -> str:
    import urllib.request

    request = urllib.request.Request(url, headers={"User-Agent": "MeridianBot/0.1"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


def ingest_feed(feed_xml: str, source: str) -> int:
    entries = parse_rss(feed_xml, source)
    if not entries:
        return 0
    return insert_events(entries)


def ingest_sources(sources: Iterable[FeedConfig]) -> dict[str, int]:
    results: dict[str, int] = {}
    for feed in sources:
        try:
            feed_xml = fetch_feed(feed.url)
            results[feed.source] = ingest_feed(feed_xml, feed.source)
        except Exception:
            results[feed.source] = 0
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest RSS feed into macro_events")
    parser.add_argument("--source", required=True)
    parser.add_argument("--feed-file", required=True, help="Path to RSS XML file")
    args = parser.parse_args()

    feed_xml = load_feed_file(args.feed_file)
    inserted = ingest_feed(feed_xml, args.source)
    print(f"Inserted {inserted} entries for {args.source}")


if __name__ == "__main__":
    main()
