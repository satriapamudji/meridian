"""Market context ingestion - fetches all core watchlist instruments and builds daily snapshot.

This module orchestrates the data fetching for the entire core watchlist:
1. Batch fetch all Yahoo Finance symbols (equities, futures, FX, ETFs)
2. Batch fetch all FRED series (yields, spreads, breakevens)
3. Calculate derived ratios (gold/silver, copper/gold, VIX term structure, etc.)
4. Return a unified MarketSnapshot for storage and analysis

Usage:
    from app.ingestion.market_context import fetch_market_snapshot, ingest_market_context

    # Fetch current snapshot
    snapshot = fetch_market_snapshot()

    # Ingest and store
    ingest_market_context()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
import logging
from typing import Any

from app.data.core_watchlist import (
    CALCULATED_RATIOS,
    get_fred_series,
    get_yahoo_symbols,
)
from app.ingestion.prices import (
    PriceBar,
    fetch_yahoo_chart,
    get_latest_fred_values,
    parse_yahoo_chart,
)

logger = logging.getLogger(__name__)


@dataclass
class MarketSnapshot:
    """A point-in-time snapshot of all market context data."""

    snapshot_date: date
    yahoo_prices: dict[str, Decimal]  # symbol -> close price
    fred_values: dict[str, Decimal]  # series_id -> value
    calculated_ratios: dict[str, Decimal]  # ratio_name -> value
    raw_yahoo_bars: dict[str, list[PriceBar]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def get_value(self, symbol: str) -> Decimal | None:
        """Get a value by symbol, checking Yahoo then FRED."""
        if symbol in self.yahoo_prices:
            return self.yahoo_prices[symbol]
        if symbol in self.fred_values:
            return self.fred_values[symbol]
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "snapshot_date": self.snapshot_date.isoformat(),
            "yahoo_prices": {k: float(v) for k, v in self.yahoo_prices.items()},
            "fred_values": {k: float(v) for k, v in self.fred_values.items()},
            "calculated_ratios": {k: float(v) for k, v in self.calculated_ratios.items()},
            "errors": self.errors,
        }


def fetch_yahoo_batch(
    symbols: list[str],
    lookback_days: int = 5,
) -> tuple[dict[str, Decimal], dict[str, list[PriceBar]], list[str]]:
    """
    Fetch current prices for multiple Yahoo Finance symbols.

    Returns:
        Tuple of (symbol -> latest close, symbol -> all bars, list of errors)
    """
    today = date.today()
    start_date = today - timedelta(days=lookback_days)

    latest_prices: dict[str, Decimal] = {}
    all_bars: dict[str, list[PriceBar]] = {}
    errors: list[str] = []

    for symbol in symbols:
        try:
            payload = fetch_yahoo_chart(symbol, start_date, today)
            bars = parse_yahoo_chart(payload, symbol)

            if not bars:
                errors.append(f"No data for {symbol}")
                continue

            all_bars[symbol] = bars

            # Get latest close
            latest_bar = max(bars, key=lambda b: b.price_date)
            if latest_bar.close is not None:
                latest_prices[symbol] = latest_bar.close
            else:
                errors.append(f"No close price for {symbol}")

        except Exception as e:
            logger.exception("Failed to fetch %s from Yahoo", symbol)
            errors.append(f"Yahoo fetch failed for {symbol}: {str(e)}")

    logger.info(
        "Yahoo batch fetch complete: %d/%d symbols successful",
        len(latest_prices),
        len(symbols),
    )
    return latest_prices, all_bars, errors


def fetch_fred_batch(series_ids: list[str]) -> tuple[dict[str, Decimal], list[str]]:
    """
    Fetch current values for multiple FRED series.

    Returns:
        Tuple of (series_id -> latest value, list of errors)
    """
    errors: list[str] = []

    try:
        values = get_latest_fred_values(series_ids)
    except Exception as e:
        logger.exception("FRED batch fetch failed")
        errors.append(f"FRED batch fetch failed: {str(e)}")
        return {}, errors

    # Filter out None values and convert
    result: dict[str, Decimal] = {}
    for series_id, value in values.items():
        if value is not None:
            result[series_id] = value
        else:
            errors.append(f"No FRED data for {series_id}")

    logger.info(
        "FRED batch fetch complete: %d/%d series successful",
        len(result),
        len(series_ids),
    )
    return result, errors


def calculate_ratios(
    yahoo_prices: dict[str, Decimal],
    fred_values: dict[str, Decimal],
) -> tuple[dict[str, Decimal], list[str]]:
    """
    Calculate derived ratios from raw prices.

    Returns:
        Tuple of (ratio_name -> value, list of errors)
    """
    ratios: dict[str, Decimal] = {}
    errors: list[str] = []

    def get_value(symbol: str) -> Decimal | None:
        if symbol in yahoo_prices:
            return yahoo_prices[symbol]
        if symbol in fred_values:
            return fred_values[symbol]
        return None

    for ratio in CALCULATED_RATIOS:
        numerator = get_value(ratio.numerator_symbol)
        denominator = get_value(ratio.denominator_symbol)

        if numerator is None:
            errors.append(f"Missing numerator {ratio.numerator_symbol} for {ratio.name}")
            continue
        if denominator is None:
            errors.append(f"Missing denominator {ratio.denominator_symbol} for {ratio.name}")
            continue
        if denominator == 0:
            errors.append(f"Zero denominator for {ratio.name}")
            continue

        ratios[ratio.name] = numerator / denominator

    logger.info(
        "Ratio calculation complete: %d/%d ratios calculated",
        len(ratios),
        len(CALCULATED_RATIOS),
    )
    return ratios, errors


def fetch_market_snapshot(snapshot_date: date | None = None) -> MarketSnapshot:
    """
    Fetch a complete market snapshot with all core watchlist instruments.

    Args:
        snapshot_date: The date for the snapshot (defaults to today)

    Returns:
        MarketSnapshot with all prices, values, and calculated ratios
    """
    if snapshot_date is None:
        snapshot_date = date.today()

    all_errors: list[str] = []

    # 1. Fetch Yahoo symbols
    yahoo_symbols = get_yahoo_symbols()
    yahoo_prices, yahoo_bars, yahoo_errors = fetch_yahoo_batch(yahoo_symbols)
    all_errors.extend(yahoo_errors)

    # 2. Fetch FRED series
    fred_series = get_fred_series()
    fred_values, fred_errors = fetch_fred_batch(fred_series)
    all_errors.extend(fred_errors)

    # 3. Calculate ratios
    ratios, ratio_errors = calculate_ratios(yahoo_prices, fred_values)
    all_errors.extend(ratio_errors)

    snapshot = MarketSnapshot(
        snapshot_date=snapshot_date,
        yahoo_prices=yahoo_prices,
        fred_values=fred_values,
        calculated_ratios=ratios,
        raw_yahoo_bars=yahoo_bars,
        errors=all_errors,
    )

    logger.info(
        "Market snapshot complete for %s: %d yahoo, %d fred, %d ratios, %d errors",
        snapshot_date,
        len(yahoo_prices),
        len(fred_values),
        len(ratios),
        len(all_errors),
    )

    return snapshot


def extract_key_levels(snapshot: MarketSnapshot) -> dict[str, float | None]:
    """
    Extract key levels from snapshot for the market_context table.

    Returns dict with keys matching the DB columns:
    - vix_level, dxy_level, us10y_level, us2y_level
    - gold_level, oil_level, spx_level, btc_level
    - spread_2s10s, hy_spread
    """

    def to_float(value: Decimal | None) -> float | None:
        return float(value) if value is not None else None

    # Direct mappings from symbols to column names
    return {
        "vix_level": to_float(snapshot.get_value("^VIX")),
        "dxy_level": to_float(snapshot.get_value("DX=F")),
        "us10y_level": to_float(snapshot.get_value("^TNX")),  # Yahoo (x10)
        "us2y_level": to_float(snapshot.get_value("DGS2")),  # FRED
        "gold_level": to_float(snapshot.get_value("GC=F")),
        "oil_level": to_float(snapshot.get_value("CL=F")),
        "spx_level": to_float(snapshot.get_value("^GSPC")),
        "btc_level": to_float(snapshot.get_value("BTC-USD")),
        "spread_2s10s": to_float(snapshot.get_value("T10Y2Y")),
        "hy_spread": to_float(snapshot.get_value("BAMLH0A0HYM2")),
        # Ratios
        "gold_silver_ratio": to_float(snapshot.calculated_ratios.get("gold_silver_ratio")),
        "copper_gold_ratio": to_float(snapshot.calculated_ratios.get("copper_gold_ratio")),
        "vix_term_structure": to_float(snapshot.calculated_ratios.get("vix_term_structure")),
        "spy_rsp_ratio": to_float(snapshot.calculated_ratios.get("spy_rsp_ratio")),
    }


def snapshot_to_raw_json(snapshot: MarketSnapshot) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Convert snapshot to raw JSON for storage in JSONB columns.

    Returns:
        Tuple of (raw_prices dict, raw_fred dict)
    """
    raw_prices = {k: float(v) for k, v in snapshot.yahoo_prices.items()}
    raw_fred = {k: float(v) for k, v in snapshot.fred_values.items()}
    return raw_prices, raw_fred
