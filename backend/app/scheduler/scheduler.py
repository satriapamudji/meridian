"""APScheduler 3.x configuration and runner.

This module sets up the background scheduler with all Meridian jobs:
- RSS ingestion (every N minutes)
- Calendar sync (every N hours)
- Fed communications sync (every N minutes)
- Price ingestion (daily)
- Market context sync (hourly)
- Digest generation (daily at configured time)
"""

from __future__ import annotations

import logging
import signal
import sys
from typing import TYPE_CHECKING

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.scheduler.jobs import (
    job_generate_digest,
    job_ingest_prices,
    job_ingest_rss,
    job_sync_calendar,
    job_sync_fed,
    job_sync_market_context,
)

if TYPE_CHECKING:
    from app.core.settings import Settings

logger = logging.getLogger(__name__)

# Job identifiers for management/inspection
JOB_RSS = "rss_ingestion"
JOB_CALENDAR = "calendar_sync"
JOB_FED = "fed_sync"
JOB_PRICES = "price_ingestion"
JOB_MARKET_CONTEXT = "market_context_sync"
JOB_DIGEST = "digest_generation"


def create_scheduler(settings: Settings | None = None) -> BackgroundScheduler:
    """
    Create and configure the APScheduler with all Meridian jobs.

    Args:
        settings: Optional Settings override (uses get_settings() if None)

    Returns:
        Configured BackgroundScheduler instance (not yet started)
    """
    if settings is None:
        settings = get_settings()

    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)

    # RSS ingestion - frequent polling
    if settings.scheduler_rss_interval_minutes > 0:
        scheduler.add_job(
            job_ingest_rss,
            IntervalTrigger(minutes=settings.scheduler_rss_interval_minutes),
            id=JOB_RSS,
            name="RSS Feed Ingestion",
            replace_existing=True,
        )
        logger.info(
            "Scheduled %s: every %d minutes", JOB_RSS, settings.scheduler_rss_interval_minutes
        )

    # Economic calendar sync - less frequent
    if settings.scheduler_calendar_interval_minutes > 0:
        scheduler.add_job(
            job_sync_calendar,
            IntervalTrigger(minutes=settings.scheduler_calendar_interval_minutes),
            id=JOB_CALENDAR,
            name="Economic Calendar Sync",
            replace_existing=True,
        )
        logger.info(
            "Scheduled %s: every %d minutes",
            JOB_CALENDAR,
            settings.scheduler_calendar_interval_minutes,
        )

    # Fed communications sync
    if settings.scheduler_fed_interval_minutes > 0:
        scheduler.add_job(
            job_sync_fed,
            IntervalTrigger(minutes=settings.scheduler_fed_interval_minutes),
            id=JOB_FED,
            name="Fed Communications Sync",
            replace_existing=True,
        )
        logger.info(
            "Scheduled %s: every %d minutes", JOB_FED, settings.scheduler_fed_interval_minutes
        )

    # Price ingestion - daily
    if settings.scheduler_prices_interval_minutes > 0:
        scheduler.add_job(
            job_ingest_prices,
            IntervalTrigger(minutes=settings.scheduler_prices_interval_minutes),
            id=JOB_PRICES,
            name="Price Ingestion",
            replace_existing=True,
        )
        logger.info(
            "Scheduled %s: every %d minutes",
            JOB_PRICES,
            settings.scheduler_prices_interval_minutes,
        )

    # Market context sync - hourly
    scheduler.add_job(
        job_sync_market_context,
        IntervalTrigger(hours=1),
        id=JOB_MARKET_CONTEXT,
        name="Market Context Sync",
        replace_existing=True,
    )
    logger.info("Scheduled %s: every 1 hour", JOB_MARKET_CONTEXT)

    # Daily digest generation - at specific time
    scheduler.add_job(
        job_generate_digest,
        CronTrigger(
            hour=settings.scheduler_digest_hour,
            minute=settings.scheduler_digest_minute,
            timezone=settings.scheduler_timezone,
        ),
        id=JOB_DIGEST,
        name="Daily Digest Generation",
        replace_existing=True,
    )
    logger.info(
        "Scheduled %s: daily at %02d:%02d %s",
        JOB_DIGEST,
        settings.scheduler_digest_hour,
        settings.scheduler_digest_minute,
        settings.scheduler_timezone,
    )

    return scheduler


def run_scheduler(run_initial: bool = True) -> None:
    """
    Run the scheduler in the foreground.

    Args:
        run_initial: If True, run all jobs once immediately before starting the schedule
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    logger.info("Initializing Meridian scheduler...")
    scheduler = create_scheduler(settings)

    # Run initial jobs immediately if requested
    if run_initial:
        logger.info("Running initial job execution...")
        _run_initial_jobs()

    # Handle graceful shutdown
    def handle_shutdown(signum: int, frame: object) -> None:
        logger.info("Received shutdown signal, stopping scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    logger.info("Scheduler starting, press Ctrl+C to stop")
    scheduler.start()

    # Block main thread
    try:
        while True:
            import time

            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)


def _run_initial_jobs() -> None:
    """Run all jobs once immediately on startup."""
    jobs = [
        ("RSS ingestion", job_ingest_rss),
        ("Calendar sync", job_sync_calendar),
        ("Fed sync", job_sync_fed),
        ("Price ingestion", job_ingest_prices),
        ("Market context sync", job_sync_market_context),
        ("Digest generation", job_generate_digest),
    ]

    for name, job_func in jobs:
        logger.info("Running initial %s...", name)
        try:
            result = job_func()
            if result.get("status") == "success":
                logger.info("Initial %s completed successfully", name)
            else:
                logger.warning("Initial %s completed with status: %s", name, result.get("status"))
        except Exception as exc:
            logger.exception("Initial %s failed: %s", name, exc)
