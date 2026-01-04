"""Dashboard API - Market context and regime status endpoints.

Provides the "at a glance" market context that should be checked before
analyzing any macro event.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from app.analysis.market_context import (
    MarketContextRecord,
    fetch_latest_market_context,
    ingest_market_context,
)
from app.data.core_watchlist import (
    ALL_INSTRUMENTS,
    CALCULATED_RATIOS,
    Category,
    get_all_by_category,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _format_record(record: MarketContextRecord) -> dict[str, Any]:
    """Format a MarketContextRecord for API response."""
    return {
        "context_date": record.context_date.isoformat(),
        "regimes": {
            "volatility": record.volatility_regime,
            "dollar": record.dollar_regime,
            "curve": record.curve_regime,
            "credit": record.credit_regime,
        },
        "position_sizing": {
            "suggested_multiplier": record.suggested_size_multiplier,
            "description": _describe_multiplier(record.suggested_size_multiplier),
        },
        "key_levels": {
            "vix": record.vix_level,
            "dxy": record.dxy_level,
            "us10y": record.us10y_level,
            "us2y": record.us2y_level,
            "gold": record.gold_level,
            "oil": record.oil_level,
            "spx": record.spx_level,
            "btc": record.btc_level,
            "spread_2s10s": record.spread_2s10s,
            "hy_spread": record.hy_spread,
        },
        "ratios": {
            "gold_silver": record.gold_silver_ratio,
            "copper_gold": record.copper_gold_ratio,
            "vix_term_structure": record.vix_term_structure,
            "spy_rsp": record.spy_rsp_ratio,
        },
        "raw_prices": record.raw_prices,
        "raw_fred": record.raw_fred,
    }


def _describe_multiplier(multiplier: float) -> str:
    """Human-readable description of position sizing multiplier."""
    if multiplier <= 0.25:
        return "Crisis mode - minimal position sizes recommended"
    elif multiplier <= 0.50:
        return "High stress - reduce position sizes by half"
    elif multiplier <= 0.75:
        return "Elevated caution - reduce position sizes by 25%"
    else:
        return "Normal conditions - standard position sizing"


@router.get("")
def get_dashboard() -> dict[str, Any]:
    """
    Get the current market context dashboard.

    Returns the latest market context from the database, including:
    - Regime classifications (volatility, dollar, curve, credit)
    - Key price levels (VIX, DXY, yields, gold, oil, SPX, BTC)
    - Calculated ratios (gold/silver, copper/gold, VIX term structure)
    - Suggested position sizing multiplier

    If no context exists yet, returns a 404.
    """
    record = fetch_latest_market_context()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="No market context available. Run market context ingestion first.",
        )

    return _format_record(record)


@router.get("/today")
def get_dashboard_today() -> dict[str, Any]:
    """
    Get the market context for today.

    Same as GET /dashboard but validates that the context is from today.
    If the latest context is stale (not from today), returns a warning.
    """
    record = fetch_latest_market_context()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="No market context available. Run market context ingestion first.",
        )

    today = datetime.now(timezone.utc).date()
    is_stale = record.context_date < today

    response = _format_record(record)
    response["is_stale"] = is_stale

    if is_stale:
        response["stale_warning"] = (
            f"Context is from {record.context_date}, not today ({today}). "
            "Consider running market context ingestion."
        )

    return response


@router.post("/refresh")
def refresh_dashboard() -> dict[str, Any]:
    """
    Trigger a fresh market context ingestion.

    Fetches current prices from Yahoo Finance and FRED, classifies regimes,
    and stores the result. Returns the new context.

    Note: This makes external API calls and may take 10-30 seconds.
    """
    try:
        record = ingest_market_context()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to refresh market context: {str(exc)}",
        ) from exc

    if record is None:
        raise HTTPException(
            status_code=503,
            detail="Market context ingestion failed. Check logs for details.",
        )

    response = _format_record(record)
    response["refreshed"] = True
    return response


@router.get("/instruments")
def get_instruments() -> dict[str, Any]:
    """
    Get all watched instruments with their metadata.

    Returns instruments grouped by category, including:
    - Symbol, data source, interpretation
    - Alert thresholds where defined
    """
    result: dict[str, list[dict[str, Any]]] = {}

    by_category = get_all_by_category()
    for category, instruments in by_category.items():
        category_name = category.value
        result[category_name] = [
            {
                "name": inst.name,
                "symbol": inst.symbol,
                "source": inst.source.value,
                "interpretation": inst.interpretation,
                "alert_thresholds": (
                    inst.alert_thresholds.levels if inst.alert_thresholds else None
                ),
            }
            for inst in instruments
        ]

    return {
        "instruments": result,
        "total_count": len(ALL_INSTRUMENTS),
        "categories": [c.value for c in Category],
    }


@router.get("/ratios")
def get_ratios() -> dict[str, Any]:
    """
    Get all calculated ratio definitions.

    Returns the ratios that are derived from raw instrument data,
    including their components and interpretations.
    """
    return {
        "ratios": [
            {
                "name": ratio.name,
                "numerator": ratio.numerator_symbol,
                "denominator": ratio.denominator_symbol,
                "interpretation": ratio.interpretation,
            }
            for ratio in CALCULATED_RATIOS
        ],
        "count": len(CALCULATED_RATIOS),
    }
