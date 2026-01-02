from __future__ import annotations

import argparse
import time
from typing import Iterable

from app.ingestion.rss import FeedConfig, ingest_sources

DEFAULT_FEEDS = [
    FeedConfig("reuters", "https://feeds.reuters.com/reuters/topNews"),
    FeedConfig("ap", "https://rss.ap.org/apf-topnews"),
    FeedConfig(
        "google_news",
        "https://news.google.com/rss/search?q=macro+economy&hl=en-US&gl=US&ceid=US:en",
    ),
]


def resolve_feeds(source: str | None, url: str | None) -> Iterable[FeedConfig]:
    if source or url:
        if not source or not url:
            raise ValueError("Both --source and --url must be provided together.")
        return [FeedConfig(source, url)]
    return DEFAULT_FEEDS


def run(interval: int, feeds: Iterable[FeedConfig]) -> None:
    while True:
        results = ingest_sources(feeds)
        summary = ", ".join(f"{name}={count}" for name, count in results.items())
        print(f"RSS poll results: {summary}")
        if interval <= 0:
            return
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll RSS feeds and store macro events")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Poll interval in seconds (0 runs once)",
    )
    parser.add_argument("--source", help="Override feed source name")
    parser.add_argument("--url", help="Override feed URL")
    args = parser.parse_args()

    feeds = resolve_feeds(args.source, args.url)
    run(args.interval, feeds)


if __name__ == "__main__":
    main()
