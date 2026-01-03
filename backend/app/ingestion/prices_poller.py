from __future__ import annotations

import argparse
from datetime import date, timedelta
import time
from typing import Iterable

from app.ingestion.prices import (
    CORE_SYMBOLS,
    DEFAULT_LOOKBACK_DAYS,
    OPTIONAL_SYMBOLS,
    ingest_prices,
)


def resolve_symbols(symbols: str | None, include_optional: bool) -> Iterable[str]:
    if symbols:
        return [symbol.strip() for symbol in symbols.split(",") if symbol.strip()]
    resolved = list(CORE_SYMBOLS)
    if include_optional:
        resolved.extend(OPTIONAL_SYMBOLS)
    return resolved


def run(interval: int, lookback_days: int, symbols: Iterable[str]) -> None:
    while True:
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        results = ingest_prices(symbols, start_date, end_date)
        summary = ", ".join(f"{name}={count}" for name, count in results.items())
        print(f"Price ingestion results: {summary}")
        if interval <= 0:
            return
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll daily prices from Yahoo Finance")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Poll interval in seconds (0 runs once)",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help="Days of history to fetch per symbol",
    )
    parser.add_argument(
        "--symbols",
        help="Comma-separated list of symbols to ingest (overrides defaults)",
    )
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="Include optional ETF/miner symbols",
    )
    args = parser.parse_args()

    symbols = resolve_symbols(args.symbols, args.include_optional)
    run(args.interval, args.lookback_days, symbols)


if __name__ == "__main__":
    main()
