"""Market context poller - CLI for daily market context ingestion.

Usage:
    # Run once (e.g., at market close)
    python -m app.ingestion.market_context_poller

    # Poll every hour
    python -m app.ingestion.market_context_poller --interval 3600

    # Dry run (fetch data but don't store)
    python -m app.ingestion.market_context_poller --dry-run
"""

from __future__ import annotations

import argparse
import logging
import time

from app.analysis.market_context import (
    build_market_context_record,
    classify_regimes,
    format_context_for_llm,
    upsert_market_context,
)
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.ingestion.market_context import fetch_market_snapshot

logger = logging.getLogger(__name__)


def run_once(dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Run a single market context ingestion cycle.

    Args:
        dry_run: If True, fetch and display but don't store
        verbose: If True, print detailed output

    Returns:
        True if successful, False otherwise
    """
    print("Fetching market snapshot...")
    try:
        snapshot = fetch_market_snapshot()
    except Exception as e:
        logger.exception("Failed to fetch market snapshot")
        print(f"ERROR: Failed to fetch snapshot: {e}")
        return False

    print(
        f"Fetched {len(snapshot.yahoo_prices)} Yahoo symbols, {len(snapshot.fred_values)} FRED series"
    )

    if snapshot.errors:
        print(f"Warnings: {len(snapshot.errors)} errors during fetch")
        if verbose:
            for error in snapshot.errors[:10]:
                print(f"  - {error}")
            if len(snapshot.errors) > 10:
                print(f"  ... and {len(snapshot.errors) - 10} more")

    # Classify regimes
    regimes = classify_regimes(snapshot)
    print(
        f"\nRegimes: volatility={regimes.volatility_regime}, "
        f"dollar={regimes.dollar_regime}, curve={regimes.curve_regime}, "
        f"credit={regimes.credit_regime}"
    )

    # Build record
    record = build_market_context_record(snapshot, regimes)
    print(f"Position sizing multiplier: {record.suggested_size_multiplier:.0%}")

    if verbose:
        print("\n" + format_context_for_llm(record))

    if dry_run:
        print("\n[DRY RUN] Skipping database insert")
        return True

    # Store to database
    print("\nStoring to database...")
    success = upsert_market_context(record)

    if success:
        print(f"SUCCESS: Market context stored for {record.context_date}")
    else:
        print("ERROR: Failed to store market context")

    return success


def run(interval: int, dry_run: bool = False, verbose: bool = False) -> None:
    """
    Run the market context ingestion loop.

    Args:
        interval: Seconds between runs (0 = run once)
        dry_run: If True, fetch and display but don't store
        verbose: If True, print detailed output
    """
    while True:
        success = run_once(dry_run=dry_run, verbose=verbose)

        if interval <= 0:
            return

        status = "OK" if success else "FAILED"
        print(f"\n[{status}] Sleeping for {interval} seconds...")
        time.sleep(interval)
        print("\n" + "=" * 50 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest market context (prices, regimes, ratios)")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Poll interval in seconds (0 runs once)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and display but don't store to database",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed output including LLM context format",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    run(args.interval, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
