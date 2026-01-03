from __future__ import annotations

import argparse
import logging
import random
import time
from typing import Iterable

from app.ingestion.rss import FeedConfig, ingest_sources

logger = logging.getLogger(__name__)

# Google News RSS feeds filtered by source and topic
# These replace the deprecated feeds.reuters.com and rss.ap.org endpoints
DEFAULT_FEEDS = [
    # Wire services via Google News (last 24h filter)
    FeedConfig(
        "reuters",
        "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&ceid=US:en&hl=en-US&gl=US",
    ),
    FeedConfig(
        "ap",
        "https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com&ceid=US:en&hl=en-US&gl=US",
    ),
    FeedConfig(
        "bloomberg",
        "https://news.google.com/rss/search?q=when:24h+allinurl:bloomberg.com&ceid=US:en&hl=en-US&gl=US",
    ),
    # Macro-focused topic feeds for comprehensive coverage
    FeedConfig(
        "central_banks",
        "https://news.google.com/rss/search?q=federal+reserve+OR+FOMC+OR+ECB+OR+central+bank+interest+rate&hl=en-US&gl=US&ceid=US:en",
    ),
    FeedConfig(
        "commodities",
        "https://news.google.com/rss/search?q=gold+price+OR+silver+price+OR+copper+price+commodities+metals&hl=en-US&gl=US&ceid=US:en",
    ),
    FeedConfig(
        "geopolitical",
        "https://news.google.com/rss/search?q=sanctions+OR+tariffs+OR+trade+war+geopolitical+conflict&hl=en-US&gl=US&ceid=US:en",
    ),
    FeedConfig(
        "inflation",
        "https://news.google.com/rss/search?q=inflation+CPI+OR+PPI+economic+data&hl=en-US&gl=US&ceid=US:en",
    ),
]

# Rate limiting configuration
MIN_DELAY_BETWEEN_FEEDS = 1.0  # seconds between feed fetches
MAX_DELAY_BETWEEN_FEEDS = 3.0  # jitter upper bound
BACKOFF_BASE_DELAY = 5.0  # initial backoff delay on rate limit
BACKOFF_MAX_DELAY = 300.0  # max backoff (5 minutes)
BACKOFF_MULTIPLIER = 2.0  # exponential backoff factor


def resolve_feeds(source: str | None, url: str | None) -> Iterable[FeedConfig]:
    if source or url:
        if not source or not url:
            raise ValueError("Both --source and --url must be provided together.")
        return [FeedConfig(source, url)]
    return DEFAULT_FEEDS


def run(interval: int, feeds: Iterable[FeedConfig]) -> None:
    """
    Run the RSS ingestion loop with rate limiting awareness.

    Args:
        interval: Seconds between poll cycles (0 = run once)
        feeds: Feed configurations to poll
    """
    consecutive_failures = 0
    current_backoff = 0.0

    while True:
        try:
            results = ingest_sources(
                feeds,
                delay_between_feeds=MIN_DELAY_BETWEEN_FEEDS,
                delay_jitter=MAX_DELAY_BETWEEN_FEEDS - MIN_DELAY_BETWEEN_FEEDS,
            )

            total_events = sum(results.values())
            failed_feeds = sum(1 for count in results.values() if count == 0)
            summary = ", ".join(f"{name}={count}" for name, count in results.items())

            if failed_feeds == 0:
                logger.info("RSS poll complete: %s (total: %d events)", summary, total_events)
                consecutive_failures = 0
                current_backoff = 0.0
            elif failed_feeds < len(results):
                logger.warning(
                    "RSS poll partial: %s (%d/%d feeds failed)",
                    summary,
                    failed_feeds,
                    len(results),
                )
                consecutive_failures = 0
            else:
                logger.error("RSS poll failed: all %d feeds returned 0 events", len(results))
                consecutive_failures += 1

        except Exception as exc:
            logger.exception("RSS poll cycle failed: %s", exc)
            consecutive_failures += 1

        if interval <= 0:
            return

        # Apply exponential backoff if experiencing repeated failures
        if consecutive_failures > 0:
            current_backoff = min(
                BACKOFF_BASE_DELAY * (BACKOFF_MULTIPLIER ** (consecutive_failures - 1)),
                BACKOFF_MAX_DELAY,
            )
            # Add jitter
            current_backoff += random.random() * (current_backoff * 0.2)
            logger.warning(
                "Applying backoff: sleeping %.1fs before next poll (failures: %d)",
                current_backoff,
                consecutive_failures,
            )
            time.sleep(current_backoff)

        time.sleep(interval)


def main() -> None:
    from app.core.logging import configure_logging
    from app.core.settings import get_settings

    parser = argparse.ArgumentParser(description="Poll RSS feeds and store macro events")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Poll interval in seconds (0 runs once)",
    )
    parser.add_argument("--source", help="Override feed source name")
    parser.add_argument("--url", help="Override feed URL")
    parser.add_argument(
        "--list-feeds",
        action="store_true",
        help="List configured feeds and exit",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    if args.list_feeds:
        print("Configured RSS feeds:")
        for feed in DEFAULT_FEEDS:
            print(f"  - {feed.source}: {feed.url}")
        return

    feeds = resolve_feeds(args.source, args.url)
    logger.info("Starting RSS poller with %d feeds", len(list(feeds)))
    feeds = resolve_feeds(args.source, args.url)  # Re-resolve since we consumed the iterator
    run(args.interval, feeds)


if __name__ == "__main__":
    main()
