from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import difflib
from html.parser import HTMLParser
import re
from typing import Callable, Iterable
import urllib.error
from urllib.parse import urljoin

import psycopg

from app.core.settings import get_settings, normalize_database_url

FED_BANK = "federal_reserve"
FED_COMM_TYPE_STATEMENT = "statement"
FED_BASE_URL = "https://www.federalreserve.gov"
FED_PRESS_RELEASES_INDEX_URL = f"{FED_BASE_URL}/newsevents/pressreleases.htm"
_FOMC_YEAR_PAGE_PATTERN = re.compile(r"/newsevents/pressreleases/\d{4}-press-fomc\.htm")
_USER_AGENT = "MeridianBot/0.1"


@dataclass(frozen=True)
class StatementLink:
    url: str
    published_at: datetime


@dataclass(frozen=True)
class CentralBankComm:
    bank: str
    comm_type: str
    published_at: datetime
    full_text: str


class _IndexParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href")
        if not href:
            return
        self._current_href = href
        self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._current_href is None:
            return
        self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return
        text = normalize_whitespace("".join(self._buffer))
        if text:
            self.links.append((self._current_href, text))
        self._current_href = None
        self._buffer = []


class _ParagraphCollector(HTMLParser):
    def __init__(self, container_id: str | None) -> None:
        super().__init__()
        self._container_id = container_id
        self._container_depth = 0
        self._in_paragraph = False
        self._buffer: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "div" and self._container_id and attrs_dict.get("id") == self._container_id:
            self._container_depth = 1
            return

        if self._container_id is None or self._container_depth > 0:
            if tag == "div" and self._container_id:
                self._container_depth += 1
            if tag in {"p", "li"}:
                self._in_paragraph = True
                self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if self._container_id is None or self._container_depth > 0:
            if tag in {"p", "li"} and self._in_paragraph:
                text = normalize_whitespace("".join(self._buffer))
                if text:
                    self.paragraphs.append(text)
                self._in_paragraph = False
                self._buffer = []
            if tag == "div" and self._container_id and self._container_depth > 0:
                self._container_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._container_id is None or self._container_depth > 0:
            if self._in_paragraph:
                self._buffer.append(data)


def normalize_whitespace(value: str) -> str:
    return " ".join(value.strip().split())


def parse_statement_index(html: str, base_url: str = FED_BASE_URL) -> list[StatementLink]:
    parser = _IndexParser()
    parser.feed(html)
    links: list[StatementLink] = []
    for href, text in parser.links:
        if "pressreleases/monetary" not in href:
            continue
        published_at = _parse_statement_date(text)
        if published_at is None:
            if not _looks_like_statement_title(text):
                continue
            published_at = _parse_statement_date_from_url(href)
            if published_at is None:
                continue
        links.append(
            StatementLink(url=urljoin(base_url, href), published_at=published_at),
        )
    return links


def parse_fomc_year_pages(html: str, base_url: str = FED_BASE_URL) -> list[str]:
    parser = _IndexParser()
    parser.feed(html)
    urls: list[str] = []
    for href, _text in parser.links:
        if _FOMC_YEAR_PAGE_PATTERN.search(href):
            urls.append(urljoin(base_url, href))
    return list(dict.fromkeys(urls))


def _parse_statement_date(text: str) -> datetime | None:
    cleaned = text.split("(")[0].strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
        return parsed.replace(tzinfo=timezone.utc)
    return None


def _parse_statement_date_from_url(url: str) -> datetime | None:
    match = re.search(r"monetary(\d{8})[a-z]?\.(htm|html)$", url.lower())
    if not match:
        return None
    try:
        parsed = datetime.strptime(match.group(1), "%Y%m%d")
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc)


def _looks_like_statement_title(text: str) -> bool:
    lowered = text.lower()
    if "statement" not in lowered:
        return False
    return "minutes" not in lowered


def parse_statement_text(html: str) -> str:
    paragraphs = _collect_paragraphs(html, container_id="article")
    if not paragraphs:
        paragraphs = _collect_paragraphs(html, container_id=None)
    return "\n".join(paragraphs).strip()


def _collect_paragraphs(html: str, container_id: str | None) -> list[str]:
    parser = _ParagraphCollector(container_id)
    parser.feed(html)
    return parser.paragraphs


def change_vs_previous(previous: str | None, current: str) -> str | None:
    if previous is None:
        return None
    diff = list(
        difflib.unified_diff(
            previous.splitlines(),
            current.splitlines(),
            fromfile="previous",
            tofile="current",
            lineterm="",
        )
    )
    if not diff:
        return ""
    return "\n".join(diff)


def fetch_url(url: str) -> str:
    import urllib.request

    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="ignore")


def _fetch_press_releases_html(index_url: str | None) -> str:
    return fetch_url(index_url or FED_PRESS_RELEASES_INDEX_URL)


def _resolve_statement_index_urls(index_url: str | None) -> list[str]:
    try:
        html = _fetch_press_releases_html(index_url)
    except urllib.error.URLError as exc:
        if index_url:
            raise RuntimeError(f"Fed index URL failed: {index_url} -> {exc}") from exc
        raise RuntimeError(
            "Fed press release index failed. Provide --index-url or --index-file."
        ) from exc

    year_urls = parse_fomc_year_pages(html)
    if year_urls:
        return year_urls
    if index_url:
        return [index_url]
    raise RuntimeError(
        "No FOMC year pages found on the Fed press releases index. "
        "Provide --index-url or --index-file."
    )


def load_html_file(path: str) -> str:
    return open(path, "r", encoding="utf-8").read()


def fetch_statement_entries(
    index_html: str, fetcher: Callable[[str], str] = fetch_url
) -> list[CentralBankComm]:
    entries: list[CentralBankComm] = []
    for link in parse_statement_index(index_html):
        statement_html = fetcher(link.url)
        full_text = parse_statement_text(statement_html)
        if not full_text:
            continue
        entries.append(
            CentralBankComm(
                bank=FED_BANK,
                comm_type=FED_COMM_TYPE_STATEMENT,
                published_at=link.published_at,
                full_text=full_text,
            )
        )
    return entries


def _existing_comm_text(
    conn: psycopg.Connection, bank: str, comm_type: str, published_at: datetime
) -> str | None:
    row = conn.execute(
        """
        SELECT full_text
        FROM central_bank_comms
        WHERE bank = %(bank)s
          AND comm_type = %(comm_type)s
          AND published_at = %(published_at)s
        LIMIT 1
        """,
        {"bank": bank, "comm_type": comm_type, "published_at": published_at},
    ).fetchone()
    if row is None:
        return None
    return row[0]


def _previous_comm_text(
    conn: psycopg.Connection, bank: str, comm_type: str, published_at: datetime
) -> str | None:
    row = conn.execute(
        """
        SELECT full_text
        FROM central_bank_comms
        WHERE bank = %(bank)s
          AND comm_type = %(comm_type)s
          AND published_at < %(published_at)s
        ORDER BY published_at DESC
        LIMIT 1
        """,
        {"bank": bank, "comm_type": comm_type, "published_at": published_at},
    ).fetchone()
    if row is None:
        return None
    return row[0]


def insert_comms(entries: Iterable[CentralBankComm]) -> int:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    insert_query = """
        INSERT INTO central_bank_comms (
            id,
            bank,
            comm_type,
            published_at,
            full_text,
            change_vs_previous
        )
        VALUES (
            gen_random_uuid(),
            %(bank)s,
            %(comm_type)s,
            %(published_at)s,
            %(full_text)s,
            %(change_vs_previous)s
        )
    """

    inserted = 0
    sorted_entries = sorted(entries, key=lambda entry: entry.published_at)
    with psycopg.connect(database_url) as conn:
        for entry in sorted_entries:
            if _existing_comm_text(conn, entry.bank, entry.comm_type, entry.published_at):
                continue
            previous_text = _previous_comm_text(
                conn, entry.bank, entry.comm_type, entry.published_at
            )
            change_text = change_vs_previous(previous_text, entry.full_text)
            result = conn.execute(
                insert_query,
                {
                    "bank": entry.bank,
                    "comm_type": entry.comm_type,
                    "published_at": entry.published_at,
                    "full_text": entry.full_text,
                    "change_vs_previous": change_text,
                },
            )
            inserted += result.rowcount or 0
    return inserted


def ingest_fomc_statements(index_url: str | None = None) -> int:
    inserted = 0
    for page_url in _resolve_statement_index_urls(index_url):
        index_html = fetch_url(page_url)
        entries = fetch_statement_entries(index_html)
        if not entries:
            continue
        inserted += insert_comms(entries)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest FOMC statements into central_bank_comms")
    parser.add_argument(
        "--index-url",
        help="Override index URL (press releases index or specific year FOMC page)",
    )
    parser.add_argument("--index-file", help="Path to a saved FOMC statement index HTML file")
    args = parser.parse_args()

    if args.index_file:
        index_html = load_html_file(args.index_file)
        entries = fetch_statement_entries(index_html)
        inserted = insert_comms(entries)
    else:
        inserted = ingest_fomc_statements(index_url=args.index_url)
    print(f"Inserted {inserted} Fed statements")


if __name__ == "__main__":
    main()
