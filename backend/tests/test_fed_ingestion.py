from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.ingestion.central_banks.fed import (
    change_vs_previous,
    parse_fomc_year_pages,
    parse_statement_index,
    parse_statement_text,
)


def _load_fixture(name: str) -> str:
    fixtures_dir = Path(__file__).resolve().parent / "fixtures" / "fed"
    return (fixtures_dir / name).read_text(encoding="utf-8")


def test_parse_statement_index_filters_and_parses_dates() -> None:
    html = _load_fixture("statement_index.html")
    links = parse_statement_index(html)

    assert len(links) == 2
    assert links[0].url.endswith("monetary20240131a.htm")
    assert links[0].published_at == datetime(2024, 1, 31, tzinfo=timezone.utc)


def test_parse_statement_text_extracts_paragraphs() -> None:
    html = _load_fixture("statement_page.html")
    text = parse_statement_text(html)

    assert "Federal Open Market Committee decided" in text
    assert "continue to monitor incoming information." in text
    assert "\n" in text


def test_change_vs_previous_generates_diff() -> None:
    previous = "Line one.\nLine two."
    current = "Line one.\nLine two updated."
    diff = change_vs_previous(previous, current)

    assert diff is not None
    assert "-Line two." in diff
    assert "+Line two updated." in diff


def test_parse_statement_index_falls_back_to_url_date() -> None:
    html = """
    <html>
      <body>
        <a href="/newsevents/pressreleases/monetary20231213a.htm">FOMC statement</a>
        <a href="/newsevents/pressreleases/monetary20231101a.htm">
          Minutes of the Federal Open Market Committee
        </a>
      </body>
    </html>
    """
    links = parse_statement_index(html)

    assert len(links) == 1
    assert links[0].published_at == datetime(2023, 12, 13, tzinfo=timezone.utc)


def test_parse_fomc_year_pages_extracts_year_links() -> None:
    html = """
    <html>
      <body>
        <a href="/newsevents/pressreleases/2025-press-fomc.htm">2025 FOMC</a>
        <a href="/newsevents/pressreleases/2024-press-fomc.htm">2024 FOMC</a>
        <a href="/newsevents/pressreleases/2024-press.htm">2024 general</a>
      </body>
    </html>
    """
    urls = parse_fomc_year_pages(html)

    assert len(urls) == 2
    assert urls[0].endswith("2025-press-fomc.htm")
    assert urls[1].endswith("2024-press-fomc.htm")
