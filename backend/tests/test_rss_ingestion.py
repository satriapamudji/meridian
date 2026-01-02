from __future__ import annotations

from datetime import datetime, timezone

from app.ingestion.rss import canonical_key, parse_rss

SAMPLE_RSS = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>  Fed   signals  pause </title>
      <link>http://example.com/article1</link>
      <pubDate>Tue, 01 Feb 2026 12:34:56 GMT</pubDate>
    </item>
    <item>
      <title>Missing link</title>
      <pubDate>Tue, 01 Feb 2026 13:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Bad date</title>
      <link>http://example.com/article2</link>
      <pubDate>not-a-date</pubDate>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_filters_and_normalizes() -> None:
    entries = parse_rss(SAMPLE_RSS, "reuters")

    assert len(entries) == 1
    entry = entries[0]
    assert entry.headline == "Fed signals pause"
    assert entry.url == "http://example.com/article1"
    assert entry.published_at.tzinfo is not None


def test_canonical_key_normalizes_headline() -> None:
    published_at = datetime(2026, 2, 1, 12, 34, 56, tzinfo=timezone.utc)
    key = canonical_key("reuters", "  Fed   signals  pause ", published_at)

    assert key == "reuters:fed signals pause:2026-02-01T12:34:56Z"
