"""Scheduled job wrapper functions.

Each job function is designed to be:
- Idempotent: Safe to re-run without side effects
- Observable: Logs start/end/errors for monitoring
- Self-contained: Handles its own exceptions to not crash the scheduler
"""

from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Any


logger = logging.getLogger(__name__)


def job_ingest_rss() -> dict[str, Any]:
    """
    Poll RSS feeds and store new macro events.

    Returns summary of ingestion results.
    """
    logger.info("Starting RSS ingestion job")
    try:
        from app.ingestion.rss import ingest_sources
        from app.ingestion.rss_poller import DEFAULT_FEEDS, MIN_DELAY_BETWEEN_FEEDS

        results = ingest_sources(
            DEFAULT_FEEDS,
            delay_between_feeds=MIN_DELAY_BETWEEN_FEEDS,
            delay_jitter=2.0,
        )
        total_events = sum(results.values())
        summary = {feed: count for feed, count in results.items()}
        logger.info("RSS ingestion complete: total=%d events", total_events)
        return {"status": "success", "total_events": total_events, "feeds": summary}
    except Exception as exc:
        logger.exception("RSS ingestion failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def job_sync_calendar() -> dict[str, Any]:
    """
    Sync economic calendar events from Forex Factory.

    Returns count of events synced.
    """
    logger.info("Starting calendar sync job")
    try:
        from app.ingestion.economic_calendar import ForexFactoryAdapter, sync_calendar

        adapter = ForexFactoryAdapter()
        inserted = sync_calendar(adapter, days=7)
        logger.info("Calendar sync complete: inserted=%d events", inserted)
        return {"status": "success", "inserted": inserted}
    except Exception as exc:
        logger.exception("Calendar sync failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def job_sync_fed() -> dict[str, Any]:
    """
    Poll and ingest FOMC statements and Fed communications.

    Returns count of items ingested.
    """
    logger.info("Starting Fed communications sync job")
    try:
        from app.ingestion.central_banks.fed import ingest_fomc_statements

        inserted = ingest_fomc_statements()
        logger.info("Fed sync complete: inserted=%d items", inserted)
        return {"status": "success", "inserted": inserted}
    except Exception as exc:
        logger.exception("Fed sync failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def job_ingest_prices() -> dict[str, Any]:
    """
    Pull daily prices for core metal symbols.

    Returns count of prices ingested per symbol.
    """
    logger.info("Starting price ingestion job")
    try:
        from app.ingestion.prices import CORE_SYMBOLS, DEFAULT_LOOKBACK_DAYS, ingest_prices

        end_date = date.today()
        start_date = end_date - timedelta(days=DEFAULT_LOOKBACK_DAYS)
        results = ingest_prices(CORE_SYMBOLS, start_date, end_date)
        total = sum(results.values())
        logger.info("Price ingestion complete: total=%d prices", total)
        return {"status": "success", "total_prices": total, "symbols": dict(results)}
    except Exception as exc:
        logger.exception("Price ingestion failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def job_generate_digest() -> dict[str, Any]:
    """
    Generate daily digest for today.

    The digest service is idempotent - if a digest already exists for today,
    it returns the cached version.

    Returns digest generation status.
    """
    logger.info("Starting daily digest generation job")
    try:
        from app.services.digests import get_or_create_digest

        today = date.today()
        digest = get_or_create_digest(today)
        logger.info(
            "Digest generation complete: date=%s events=%d theses=%d",
            today.isoformat(),
            len(digest.priority_events),
            len(digest.active_theses),
        )
        return {
            "status": "success",
            "digest_date": today.isoformat(),
            "priority_events": len(digest.priority_events),
            "active_theses": len(digest.active_theses),
        }
    except Exception as exc:
        logger.exception("Digest generation failed: %s", exc)
        return {"status": "error", "error": str(exc)}


def job_sync_market_context() -> dict[str, Any]:
    """
    Fetch and store current market context (VIX, DXY, yields, etc.).

    Returns ingestion status.
    """
    logger.info("Starting market context sync job")
    try:
        from app.analysis.market_context import ingest_market_context

        result = ingest_market_context()
        logger.info(
            "Market context sync complete: date=%s vix=%s dxy=%s",
            result.context_date.isoformat() if result else "n/a",
            result.vix_level if result else "n/a",
            result.dxy_level if result else "n/a",
        )
        return {
            "status": "success",
            "context_date": result.context_date.isoformat() if result else None,
        }
    except Exception as exc:
        logger.exception("Market context sync failed: %s", exc)
        return {"status": "error", "error": str(exc)}
