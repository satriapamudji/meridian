"""Meridian Scheduler Module.

This module provides APScheduler-based job scheduling for:
- RSS feed ingestion (every N minutes)
- Economic calendar sync (every N hours)
- Fed communications ingestion (every N minutes)
- Price data ingestion (daily)
- Digest generation (daily at configured time)
"""

from app.scheduler.scheduler import create_scheduler, run_scheduler

__all__ = ["create_scheduler", "run_scheduler"]
