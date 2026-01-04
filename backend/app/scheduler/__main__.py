"""Entry point for running the Meridian scheduler.

Usage:
    python -m app.scheduler [OPTIONS]

Options:
    --no-initial    Skip running jobs immediately on startup
    --list-jobs     List configured jobs and exit
"""

from __future__ import annotations

import argparse


def list_jobs() -> None:
    """Print configured jobs and their schedules."""
    from app.core.settings import get_settings

    settings = get_settings()

    print("Meridian Scheduler - Configured Jobs")
    print("=" * 50)
    print(f"Timezone: {settings.scheduler_timezone}")
    print()
    print("INTERVAL JOBS:")
    print(f"  RSS ingestion:          every {settings.scheduler_rss_interval_minutes} minutes")
    print(f"  Calendar sync:          every {settings.scheduler_calendar_interval_minutes} minutes")
    print(f"  Fed communications:     every {settings.scheduler_fed_interval_minutes} minutes")
    print(f"  Price ingestion:        every {settings.scheduler_prices_interval_minutes} minutes")
    print("  Market context sync:    every 60 minutes")
    print()
    print("CRON JOBS:")
    digest_time = f"{settings.scheduler_digest_hour:02d}:{settings.scheduler_digest_minute:02d}"
    print(f"  Daily digest:           daily at {digest_time} {settings.scheduler_timezone}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Meridian background scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m app.scheduler                 # Run scheduler with initial job execution
    python -m app.scheduler --no-initial   # Run scheduler without initial jobs
    python -m app.scheduler --list-jobs    # Show configured jobs
        """,
    )
    parser.add_argument(
        "--no-initial",
        action="store_true",
        help="Skip running jobs immediately on startup",
    )
    parser.add_argument(
        "--list-jobs",
        action="store_true",
        help="List configured jobs and exit",
    )
    args = parser.parse_args()

    if args.list_jobs:
        list_jobs()
        return

    from app.scheduler.scheduler import run_scheduler

    run_scheduler(run_initial=not args.no_initial)


if __name__ == "__main__":
    main()
