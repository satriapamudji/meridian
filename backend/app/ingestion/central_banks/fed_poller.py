from __future__ import annotations

import argparse
import time

from app.ingestion.central_banks.fed import ingest_fomc_statements


def run(interval: int, index_url: str | None) -> None:
    while True:
        inserted = ingest_fomc_statements(index_url=index_url)
        print(f"Fed poll results: inserted={inserted}")
        if interval <= 0:
            return
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll FOMC statements and store comms")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Poll interval in seconds (0 runs once)",
    )
    parser.add_argument(
        "--index-url",
        default=None,
        help="Override index URL (press releases index or specific year FOMC page)",
    )
    args = parser.parse_args()

    run(args.interval, args.index_url)


if __name__ == "__main__":
    main()
