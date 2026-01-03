from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import logging
import random
import time
from typing import Iterable
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET

import psycopg

from app.core.settings import get_settings, normalize_database_url

logger = logging.getLogger(__name__)

# Retry/backoff configuration
MAX_RETRIES = 3
BACKOFF_BASE_DELAY = 2.0  # seconds
BACKOFF_MAX_DELAY = 60.0  # seconds
BACKOFF_MULTIPLIER = 2.0
JITTER_RANGE = 0.5  # +/- 50% jitter
REQUEST_TIMEOUT = 15  # seconds

# Rate limit detection
RATE_LIMIT_CODES = {429, 403, 503}


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


class RateLimitError(Exception):
    """Raised when a feed returns a rate limit response."""

    def __init__(self, url: str, status_code: int, retry_after: float | None = None):
        self.url = url
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(f"Rate limited ({status_code}) for {url}")


def fetch_feed(url: str) -> str:
    """Fetch RSS feed with retry and exponential backoff."""
    import urllib.request

    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; MeridianBot/0.1)",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                },
            )
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                return response.read().decode("utf-8", errors="ignore")

        except HTTPError as exc:
            last_error = exc
            if exc.code in RATE_LIMIT_CODES:
                # Parse Retry-After header if present
                retry_after = _parse_retry_after(exc.headers.get("Retry-After"))
                if attempt < MAX_RETRIES - 1:
                    delay = _calculate_backoff(attempt, retry_after)
                    logger.warning(
                        "Rate limited (%s) fetching %s, retrying in %.1fs (attempt %d/%d)",
                        exc.code,
                        url,
                        delay,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    time.sleep(delay)
                    continue
                raise RateLimitError(url, exc.code, retry_after) from exc
            elif exc.code >= 500:
                # Server error - retry with backoff
                if attempt < MAX_RETRIES - 1:
                    delay = _calculate_backoff(attempt)
                    logger.warning(
                        "Server error (%s) fetching %s, retrying in %.1fs (attempt %d/%d)",
                        exc.code,
                        url,
                        delay,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    time.sleep(delay)
                    continue
            raise

        except URLError as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                delay = _calculate_backoff(attempt)
                logger.warning(
                    "Network error fetching %s: %s, retrying in %.1fs (attempt %d/%d)",
                    url,
                    exc.reason,
                    delay,
                    attempt + 1,
                    MAX_RETRIES,
                )
                time.sleep(delay)
                continue
            raise

        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                delay = _calculate_backoff(attempt)
                logger.warning(
                    "Error fetching %s: %s, retrying in %.1fs (attempt %d/%d)",
                    url,
                    exc,
                    delay,
                    attempt + 1,
                    MAX_RETRIES,
                )
                time.sleep(delay)
                continue
            raise

    # Should not reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts")


def _calculate_backoff(attempt: int, retry_after: float | None = None) -> float:
    """Calculate backoff delay with exponential increase and jitter."""
    if retry_after is not None and retry_after > 0:
        # Use server-provided retry-after, but cap it
        base_delay = min(retry_after, BACKOFF_MAX_DELAY)
    else:
        # Exponential backoff: 2s, 4s, 8s, ...
        base_delay = min(BACKOFF_BASE_DELAY * (BACKOFF_MULTIPLIER**attempt), BACKOFF_MAX_DELAY)

    # Add jitter (+/- 50%)
    jitter = base_delay * JITTER_RANGE * (2 * random.random() - 1)
    return max(0.1, base_delay + jitter)


def _parse_retry_after(header: str | None) -> float | None:
    """Parse Retry-After header (seconds or HTTP date)."""
    if not header:
        return None
    try:
        return float(header)
    except ValueError:
        pass
    try:
        retry_date = parsedate_to_datetime(header)
        delta = retry_date - datetime.now(timezone.utc)
        return max(0, delta.total_seconds())
    except (TypeError, ValueError):
        return None


def ingest_feed(feed_xml: str, source: str) -> int:
    entries = parse_rss(feed_xml, source)
    if not entries:
        return 0
    return insert_events(entries)


def ingest_sources(
    sources: Iterable[FeedConfig],
    delay_between_feeds: float = 1.0,
    delay_jitter: float = 1.0,
) -> dict[str, int]:
    """
    Ingest multiple RSS feeds with rate limiting awareness.

    Args:
        sources: Feed configurations to ingest
        delay_between_feeds: Base delay between feed fetches (seconds)
        delay_jitter: Random jitter added to delay (0 to jitter seconds)

    Returns:
        Dict mapping source name to number of events inserted
    """
    results: dict[str, int] = {}
    sources_list = list(sources)

    for idx, feed in enumerate(sources_list):
        try:
            feed_xml = fetch_feed(feed.url)
            count = ingest_feed(feed_xml, feed.source)
            results[feed.source] = count
            logger.info("Ingested %d events from %s", count, feed.source)

        except RateLimitError as exc:
            logger.warning(
                "Rate limited fetching %s (status %d), skipping",
                feed.source,
                exc.status_code,
            )
            results[feed.source] = 0
            # If rate limited, increase delay for remaining feeds
            delay_between_feeds = min(delay_between_feeds * 2, 30.0)

        except Exception as exc:
            logger.exception("Failed to ingest %s: %s", feed.source, exc)
            results[feed.source] = 0

        # Add delay between feeds to avoid rate limiting (except after last feed)
        if idx < len(sources_list) - 1:
            delay = delay_between_feeds + random.random() * delay_jitter
            time.sleep(delay)

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
