"""Market context analysis - regime classification and position sizing.

This module takes a MarketSnapshot and classifies the current market regime:
1. Volatility Regime: calm, normal, elevated, fear, crisis
2. Dollar Regime: weak, neutral, strong
3. Curve Regime: steep, normal, flat, inverted
4. Credit Regime: tight, normal, wide, stressed, crisis

Based on regime classification, it calculates a suggested position sizing multiplier.

Usage:
    from app.analysis.market_context import (
        classify_regimes,
        calculate_position_multiplier,
        build_market_context_record,
    )

    snapshot = fetch_market_snapshot()
    regimes = classify_regimes(snapshot)
    multiplier = calculate_position_multiplier(regimes)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
import logging
from typing import Any

import psycopg

from app.core.settings import get_settings, normalize_database_url
from app.data.core_watchlist import (
    CREDIT_REGIME_THRESHOLDS,
    CURVE_REGIME_THRESHOLDS,
    POSITION_SIZE_MULTIPLIERS,
    VOLATILITY_REGIME_THRESHOLDS,
)
from app.ingestion.market_context import (
    MarketSnapshot,
    extract_key_levels,
    fetch_market_snapshot,
    snapshot_to_raw_json,
)

logger = logging.getLogger(__name__)


@dataclass
class RegimeClassification:
    """Classification of current market regimes."""

    volatility_regime: str  # calm, normal, elevated, fear, crisis
    dollar_regime: str  # weak, neutral, strong
    curve_regime: str  # steep, normal, flat, inverted
    credit_regime: str  # tight, normal, wide, stressed, crisis

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "volatility_regime": self.volatility_regime,
            "dollar_regime": self.dollar_regime,
            "curve_regime": self.curve_regime,
            "credit_regime": self.credit_regime,
        }


def classify_volatility_regime(vix_level: float | None) -> str:
    """
    Classify volatility regime based on VIX level.

    Returns: crisis, fear, elevated, normal, or calm
    """
    if vix_level is None:
        return "unknown"

    # Check thresholds from highest to lowest
    for regime in ("crisis", "fear", "elevated", "normal", "calm"):
        threshold = VOLATILITY_REGIME_THRESHOLDS[regime]["vix_min"]
        if vix_level >= threshold:
            return regime

    return "calm"


def classify_dollar_regime(
    dxy_level: float | None,
    dxy_previous: float | None = None,
) -> str:
    """
    Classify dollar regime based on DXY level or change.

    For now, we use absolute level thresholds as a simple heuristic.
    In production, you'd track daily changes or moving averages.

    Returns: strong, neutral, or weak
    """
    if dxy_level is None:
        return "unknown"

    # Simple absolute level heuristic
    # DXY historical range roughly 70-120, typical around 90-105
    if dxy_level >= 105:
        return "strong"
    elif dxy_level <= 95:
        return "weak"
    else:
        return "neutral"


def classify_curve_regime(spread_2s10s: float | None) -> str:
    """
    Classify yield curve regime based on 2s10s spread.

    The spread is in percentage points (e.g., -0.5 = 50bps inverted).

    Returns: steep, normal, flat, or inverted
    """
    if spread_2s10s is None:
        return "unknown"

    # Check thresholds from highest to lowest
    for regime in ("steep", "normal", "flat", "inverted"):
        threshold = CURVE_REGIME_THRESHOLDS[regime]["spread_min"]
        if spread_2s10s >= threshold:
            return regime

    return "inverted"


def classify_credit_regime(hy_spread: float | None) -> str:
    """
    Classify credit regime based on high-yield spread.

    The spread is in basis points (e.g., 400 = 4%).

    Returns: crisis, stressed, wide, normal, or tight
    """
    if hy_spread is None:
        return "unknown"

    # Check thresholds from highest to lowest
    for regime in ("crisis", "stressed", "wide", "normal", "tight"):
        threshold = CREDIT_REGIME_THRESHOLDS[regime]["spread_min"]
        if hy_spread >= threshold:
            return regime

    return "tight"


def classify_regimes(snapshot: MarketSnapshot) -> RegimeClassification:
    """
    Classify all market regimes from a snapshot.

    Args:
        snapshot: A MarketSnapshot with all instrument values

    Returns:
        RegimeClassification with all four regime types
    """
    key_levels = extract_key_levels(snapshot)

    return RegimeClassification(
        volatility_regime=classify_volatility_regime(key_levels.get("vix_level")),
        dollar_regime=classify_dollar_regime(key_levels.get("dxy_level")),
        curve_regime=classify_curve_regime(key_levels.get("spread_2s10s")),
        credit_regime=classify_credit_regime(key_levels.get("hy_spread")),
    )


def calculate_position_multiplier(regimes: RegimeClassification) -> float:
    """
    Calculate suggested position sizing multiplier based on regimes.

    The multiplier is the minimum of volatility and credit adjustments.
    This is conservative - if either regime suggests caution, we reduce size.

    Returns: Float between 0.25 and 1.0
    """
    vol_multiplier = POSITION_SIZE_MULTIPLIERS["volatility"].get(regimes.volatility_regime, 1.0)
    credit_multiplier = POSITION_SIZE_MULTIPLIERS["credit"].get(regimes.credit_regime, 1.0)

    # Take the minimum (most conservative)
    return min(vol_multiplier, credit_multiplier)


@dataclass
class MarketContextRecord:
    """A complete market context record ready for database insertion."""

    context_date: date
    volatility_regime: str
    dollar_regime: str
    curve_regime: str
    credit_regime: str
    vix_level: float | None
    dxy_level: float | None
    us10y_level: float | None
    us2y_level: float | None
    gold_level: float | None
    oil_level: float | None
    spx_level: float | None
    btc_level: float | None
    spread_2s10s: float | None
    hy_spread: float | None
    gold_silver_ratio: float | None
    copper_gold_ratio: float | None
    vix_term_structure: float | None
    spy_rsp_ratio: float | None
    suggested_size_multiplier: float
    raw_prices: dict[str, Any]
    raw_fred: dict[str, Any]


def build_market_context_record(
    snapshot: MarketSnapshot,
    regimes: RegimeClassification | None = None,
) -> MarketContextRecord:
    """
    Build a complete market context record from a snapshot.

    Args:
        snapshot: The fetched market snapshot
        regimes: Optional pre-computed regimes (computed if not provided)

    Returns:
        MarketContextRecord ready for database insertion
    """
    if regimes is None:
        regimes = classify_regimes(snapshot)

    key_levels = extract_key_levels(snapshot)
    multiplier = calculate_position_multiplier(regimes)
    raw_prices, raw_fred = snapshot_to_raw_json(snapshot)

    return MarketContextRecord(
        context_date=snapshot.snapshot_date,
        volatility_regime=regimes.volatility_regime,
        dollar_regime=regimes.dollar_regime,
        curve_regime=regimes.curve_regime,
        credit_regime=regimes.credit_regime,
        vix_level=key_levels.get("vix_level"),
        dxy_level=key_levels.get("dxy_level"),
        us10y_level=key_levels.get("us10y_level"),
        us2y_level=key_levels.get("us2y_level"),
        gold_level=key_levels.get("gold_level"),
        oil_level=key_levels.get("oil_level"),
        spx_level=key_levels.get("spx_level"),
        btc_level=key_levels.get("btc_level"),
        spread_2s10s=key_levels.get("spread_2s10s"),
        hy_spread=key_levels.get("hy_spread"),
        gold_silver_ratio=key_levels.get("gold_silver_ratio"),
        copper_gold_ratio=key_levels.get("copper_gold_ratio"),
        vix_term_structure=key_levels.get("vix_term_structure"),
        spy_rsp_ratio=key_levels.get("spy_rsp_ratio"),
        suggested_size_multiplier=multiplier,
        raw_prices=raw_prices,
        raw_fred=raw_fred,
    )


def upsert_market_context(record: MarketContextRecord) -> bool:
    """
    Insert or update a market context record in the database.

    Returns:
        True if successful, False otherwise
    """
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)

    query = """
        INSERT INTO market_context (
            id,
            context_date,
            volatility_regime,
            dollar_regime,
            curve_regime,
            credit_regime,
            vix_level,
            dxy_level,
            us10y_level,
            us2y_level,
            gold_level,
            oil_level,
            spx_level,
            btc_level,
            spread_2s10s,
            hy_spread,
            gold_silver_ratio,
            copper_gold_ratio,
            vix_term_structure,
            spy_rsp_ratio,
            suggested_size_multiplier,
            raw_prices,
            raw_fred,
            created_at
        )
        VALUES (
            gen_random_uuid(),
            %(context_date)s,
            %(volatility_regime)s,
            %(dollar_regime)s,
            %(curve_regime)s,
            %(credit_regime)s,
            %(vix_level)s,
            %(dxy_level)s,
            %(us10y_level)s,
            %(us2y_level)s,
            %(gold_level)s,
            %(oil_level)s,
            %(spx_level)s,
            %(btc_level)s,
            %(spread_2s10s)s,
            %(hy_spread)s,
            %(gold_silver_ratio)s,
            %(copper_gold_ratio)s,
            %(vix_term_structure)s,
            %(spy_rsp_ratio)s,
            %(suggested_size_multiplier)s,
            %(raw_prices)s,
            %(raw_fred)s,
            now()
        )
        ON CONFLICT (context_date)
        DO UPDATE SET
            volatility_regime = EXCLUDED.volatility_regime,
            dollar_regime = EXCLUDED.dollar_regime,
            curve_regime = EXCLUDED.curve_regime,
            credit_regime = EXCLUDED.credit_regime,
            vix_level = EXCLUDED.vix_level,
            dxy_level = EXCLUDED.dxy_level,
            us10y_level = EXCLUDED.us10y_level,
            us2y_level = EXCLUDED.us2y_level,
            gold_level = EXCLUDED.gold_level,
            oil_level = EXCLUDED.oil_level,
            spx_level = EXCLUDED.spx_level,
            btc_level = EXCLUDED.btc_level,
            spread_2s10s = EXCLUDED.spread_2s10s,
            hy_spread = EXCLUDED.hy_spread,
            gold_silver_ratio = EXCLUDED.gold_silver_ratio,
            copper_gold_ratio = EXCLUDED.copper_gold_ratio,
            vix_term_structure = EXCLUDED.vix_term_structure,
            spy_rsp_ratio = EXCLUDED.spy_rsp_ratio,
            suggested_size_multiplier = EXCLUDED.suggested_size_multiplier,
            raw_prices = EXCLUDED.raw_prices,
            raw_fred = EXCLUDED.raw_fred
    """

    try:
        with psycopg.connect(database_url) as conn:
            conn.execute(
                query,
                {
                    "context_date": record.context_date,
                    "volatility_regime": record.volatility_regime,
                    "dollar_regime": record.dollar_regime,
                    "curve_regime": record.curve_regime,
                    "credit_regime": record.credit_regime,
                    "vix_level": record.vix_level,
                    "dxy_level": record.dxy_level,
                    "us10y_level": record.us10y_level,
                    "us2y_level": record.us2y_level,
                    "gold_level": record.gold_level,
                    "oil_level": record.oil_level,
                    "spx_level": record.spx_level,
                    "btc_level": record.btc_level,
                    "spread_2s10s": record.spread_2s10s,
                    "hy_spread": record.hy_spread,
                    "gold_silver_ratio": record.gold_silver_ratio,
                    "copper_gold_ratio": record.copper_gold_ratio,
                    "vix_term_structure": record.vix_term_structure,
                    "spy_rsp_ratio": record.spy_rsp_ratio,
                    "suggested_size_multiplier": record.suggested_size_multiplier,
                    "raw_prices": json.dumps(record.raw_prices),
                    "raw_fred": json.dumps(record.raw_fred),
                },
            )
        logger.info("Market context upserted for %s", record.context_date)
        return True
    except Exception:
        logger.exception("Failed to upsert market context for %s", record.context_date)
        return False


def fetch_latest_market_context() -> MarketContextRecord | None:
    """
    Fetch the most recent market context from the database.

    Returns:
        MarketContextRecord or None if not found
    """
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)

    query = """
        SELECT
            context_date,
            volatility_regime,
            dollar_regime,
            curve_regime,
            credit_regime,
            vix_level,
            dxy_level,
            us10y_level,
            us2y_level,
            gold_level,
            oil_level,
            spx_level,
            btc_level,
            spread_2s10s,
            hy_spread,
            gold_silver_ratio,
            copper_gold_ratio,
            vix_term_structure,
            spy_rsp_ratio,
            suggested_size_multiplier,
            raw_prices,
            raw_fred
        FROM market_context
        ORDER BY context_date DESC
        LIMIT 1
    """

    try:
        with psycopg.connect(database_url) as conn:
            row = conn.execute(query).fetchone()

        if row is None:
            return None

        return MarketContextRecord(
            context_date=row[0],
            volatility_regime=row[1],
            dollar_regime=row[2],
            curve_regime=row[3],
            credit_regime=row[4],
            vix_level=row[5],
            dxy_level=row[6],
            us10y_level=row[7],
            us2y_level=row[8],
            gold_level=row[9],
            oil_level=row[10],
            spx_level=row[11],
            btc_level=row[12],
            spread_2s10s=row[13],
            hy_spread=row[14],
            gold_silver_ratio=row[15],
            copper_gold_ratio=row[16],
            vix_term_structure=row[17],
            spy_rsp_ratio=row[18],
            suggested_size_multiplier=row[19],
            raw_prices=row[20] or {},
            raw_fred=row[21] or {},
        )
    except Exception:
        logger.exception("Failed to fetch latest market context")
        return None


def ingest_market_context(snapshot_date: date | None = None) -> MarketContextRecord | None:
    """
    Full pipeline: fetch snapshot, classify regimes, store to database.

    Args:
        snapshot_date: The date for the snapshot (defaults to today)

    Returns:
        The stored MarketContextRecord, or None if failed
    """
    snapshot = fetch_market_snapshot(snapshot_date)
    regimes = classify_regimes(snapshot)
    record = build_market_context_record(snapshot, regimes)

    if upsert_market_context(record):
        return record
    return None


def format_context_for_llm(record: MarketContextRecord) -> str:
    """
    Format market context as a human-readable string for LLM prompts.

    This is injected into event analysis prompts to give the model
    awareness of current market conditions.
    """
    lines = [
        "=== CURRENT MARKET CONTEXT ===",
        f"Date: {record.context_date}",
        "",
        "REGIME CLASSIFICATION:",
        f"  Volatility: {record.volatility_regime.upper()}",
        f"  Dollar: {record.dollar_regime.upper()}",
        f"  Yield Curve: {record.curve_regime.upper()}",
        f"  Credit: {record.credit_regime.upper()}",
        f"  Suggested Position Size: {record.suggested_size_multiplier:.0%}",
        "",
        "KEY LEVELS:",
    ]

    if record.vix_level is not None:
        lines.append(f"  VIX: {record.vix_level:.2f}")
    if record.dxy_level is not None:
        lines.append(f"  DXY: {record.dxy_level:.2f}")
    if record.us10y_level is not None:
        lines.append(f"  US10Y: {record.us10y_level:.2f}")
    if record.spread_2s10s is not None:
        lines.append(f"  2s10s Spread: {record.spread_2s10s:.2f}")
    if record.gold_level is not None:
        lines.append(f"  Gold: ${record.gold_level:.2f}")
    if record.oil_level is not None:
        lines.append(f"  Oil: ${record.oil_level:.2f}")
    if record.spx_level is not None:
        lines.append(f"  S&P 500: {record.spx_level:.2f}")
    if record.btc_level is not None:
        lines.append(f"  Bitcoin: ${record.btc_level:,.2f}")
    if record.hy_spread is not None:
        lines.append(f"  HY Spread: {record.hy_spread:.0f}bps")

    lines.append("")
    lines.append("KEY RATIOS:")

    if record.gold_silver_ratio is not None:
        lines.append(f"  Gold/Silver: {record.gold_silver_ratio:.1f}")
    if record.copper_gold_ratio is not None:
        lines.append(f"  Copper/Gold: {record.copper_gold_ratio:.4f}")
    if record.vix_term_structure is not None:
        term = "backwardation (panic)" if record.vix_term_structure > 1 else "contango (normal)"
        lines.append(f"  VIX Term Structure: {record.vix_term_structure:.2f} ({term})")
    if record.spy_rsp_ratio is not None:
        breadth = "narrow (mega-cap led)" if record.spy_rsp_ratio > 1.05 else "healthy"
        lines.append(f"  SPY/RSP: {record.spy_rsp_ratio:.3f} ({breadth})")

    lines.append("")
    lines.append("=" * 30)

    return "\n".join(lines)
