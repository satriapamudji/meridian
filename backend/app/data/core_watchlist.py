"""Core watchlist definitions for the Meridian macro trading dashboard.

This module defines the instruments that form the "market context" dashboard -
the vital signs you check before analyzing any macro event. The philosophy:

1. VITAL SIGNS: Check these first, every day (VIX, DXY, 10Y, Gold, Oil, SPX, BTC, 2s10s)
2. VOLATILITY REGIME: Are we in calm, elevated, fear, or crisis mode?
3. RATES & CURVE: What's the Fed pricing? Curve shape?
4. DOLLAR & FX: Global liquidity conditions, carry trade signals
5. CREDIT: Early warning system for stress
6. COMMODITIES: Growth/inflation signals beyond core metals
7. BREADTH: Are rallies broad-based or narrow?

Usage:
    from app.data.core_watchlist import (
        get_yahoo_symbols,
        get_fred_series,
        get_all_by_category,
        ALL_INSTRUMENTS,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DataSource(Enum):
    """Where to fetch the instrument data from."""

    YAHOO = "yahoo"
    FRED = "fred"
    CALCULATED = "calculated"


class Category(Enum):
    """Instrument categories for grouping and display."""

    VITAL_SIGNS = "vital_signs"
    VOLATILITY = "volatility"
    RATES = "rates"
    FX = "fx"
    CREDIT = "credit"
    COMMODITIES = "commodities"
    BREADTH = "breadth"


@dataclass(frozen=True)
class AlertThresholds:
    """Thresholds for alerting on instrument levels."""

    levels: dict[str, float] = field(default_factory=dict)

    def get_alert_level(self, value: float) -> str | None:
        """Return the highest threshold breached, or None."""
        breached = None
        breached_value = float("-inf")
        for level_name, threshold in self.levels.items():
            if value >= threshold and threshold > breached_value:
                breached = level_name
                breached_value = threshold
        return breached


@dataclass(frozen=True)
class WatchlistInstrument:
    """Definition of a core watchlist instrument."""

    name: str
    symbol: str
    source: DataSource
    category: Category
    interpretation: str
    alert_thresholds: AlertThresholds | None = None
    invert_for_alert: bool = False  # True if lower values trigger alerts (e.g., curve)


# =============================================================================
# TIER 1: VITAL SIGNS (check first, every day)
# These 8 instruments give you 80% of the context in 30 seconds.
# =============================================================================

VITAL_SIGNS: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="VIX",
        symbol="^VIX",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Fear gauge. <15=complacent, 15-20=normal, 20-30=elevated, "
            ">30=fear, >40=crisis. Drives position sizing."
        ),
        alert_thresholds=AlertThresholds({"normal": 15, "elevated": 20, "fear": 30, "crisis": 40}),
    ),
    WatchlistInstrument(
        name="DXY",
        symbol="DX=F",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Dollar strength proxy. Rising=global tightening, headwind for risk assets "
            "and commodities. Falling=loosening, tailwind for EM/commodities/crypto."
        ),
    ),
    WatchlistInstrument(
        name="US10Y",
        symbol="^TNX",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "10-year Treasury yield (x10). Rising=hawkish/growth expectations. "
            "Falling=dovish/flight to safety. Direction matters more than level."
        ),
    ),
    WatchlistInstrument(
        name="2s10s_Spread",
        symbol="T10Y2Y",
        source=DataSource.FRED,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Yield curve shape. Negative=inverted (recession signal, 6-18mo lead). "
            "Steepening after inversion=recession imminent. Normal >100bps."
        ),
        alert_thresholds=AlertThresholds({"flat": 0.25, "inverted": 0}),
        invert_for_alert=True,
    ),
    WatchlistInstrument(
        name="Gold",
        symbol="GC=F",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Safe haven + real rates. Up+yields down=flight to safety. "
            "Up+yields up=inflation fear. Up+DXY down=dollar debasement."
        ),
    ),
    WatchlistInstrument(
        name="Oil_WTI",
        symbol="CL=F",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Growth + supply signal. Up+equities up=growth optimism. "
            "Up+equities down=supply shock (stagflation). Crashing=demand destruction."
        ),
    ),
    WatchlistInstrument(
        name="SPX",
        symbol="^GSPC",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Risk appetite benchmark. The reference for relative performance. "
            "Everything else is compared to this."
        ),
    ),
    WatchlistInstrument(
        name="Bitcoin",
        symbol="BTC-USD",
        source=DataSource.YAHOO,
        category=Category.VITAL_SIGNS,
        interpretation=(
            "Speculative liquidity barometer. Weak while SPX strong=liquidity "
            "tightening at the margin. Leading indicator for risk appetite."
        ),
    ),
)


# =============================================================================
# TIER 2: VOLATILITY REGIME
# Tells you whether you're in normal market or regime shift.
# =============================================================================

VOLATILITY: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="VVIX",
        symbol="^VVIX",
        source=DataSource.YAHOO,
        category=Category.VOLATILITY,
        interpretation=(
            "Volatility of volatility. >120=extreme fear, potential exhaustion. "
            "<80=complacent, vol is cheap to buy."
        ),
        alert_thresholds=AlertThresholds({"elevated": 100, "extreme": 120}),
    ),
    WatchlistInstrument(
        name="VIX_Front",
        symbol="VX=F",
        source=DataSource.YAHOO,
        category=Category.VOLATILITY,
        interpretation=(
            "VIX futures front month. Compare to spot VIX for term structure. "
            "VX > VIX = contango (normal). VX < VIX = backwardation (panic)."
        ),
    ),
    WatchlistInstrument(
        name="MOVE",
        symbol="^MOVE",
        source=DataSource.YAHOO,
        category=Category.VOLATILITY,
        interpretation=(
            "Bond market volatility (ICE BofA). >100=elevated, >120=stress, "
            ">140=crisis. Rate vol often leads equity vol."
        ),
        alert_thresholds=AlertThresholds({"elevated": 100, "stress": 120, "crisis": 140}),
    ),
    WatchlistInstrument(
        name="VIX3M",
        symbol="^VIX3M",
        source=DataSource.YAHOO,
        category=Category.VOLATILITY,
        interpretation=(
            "3-month VIX. Used for VIX/VIX3M ratio. Ratio >1 = near-term panic "
            "(backwardation). Ratio <0.85 = complacent."
        ),
    ),
)


# =============================================================================
# TIER 3: RATES & CURVE
# Fed expectations and economic signals from the bond market.
# =============================================================================

RATES: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="US2Y",
        symbol="DGS2",
        source=DataSource.FRED,
        category=Category.RATES,
        interpretation=(
            "2-year Treasury yield. Most sensitive to Fed policy expectations. "
            "Big moves here = policy repricing."
        ),
    ),
    WatchlistInstrument(
        name="US10Y_FRED",
        symbol="DGS10",
        source=DataSource.FRED,
        category=Category.RATES,
        interpretation=(
            "10-year Treasury yield from FRED. Growth + inflation expectations "
            "over the decade. Mortgage rates key off this."
        ),
    ),
    WatchlistInstrument(
        name="US30Y",
        symbol="DGS30",
        source=DataSource.FRED,
        category=Category.RATES,
        interpretation=(
            "30-year Treasury yield. Long-term inflation expectations. "
            "If rising faster than 10Y = inflation expectations unanchoring."
        ),
    ),
    WatchlistInstrument(
        name="5Y_Breakeven",
        symbol="T5YIE",
        source=DataSource.FRED,
        category=Category.RATES,
        interpretation=(
            "Market-implied 5Y inflation expectation. Fed watches this closely. "
            ">3% = inflation fears elevated. <2% = deflation concerns."
        ),
        alert_thresholds=AlertThresholds({"elevated": 2.75, "high": 3.0}),
    ),
    WatchlistInstrument(
        name="Fed_Funds_Futures",
        symbol="ZQ=F",
        source=DataSource.YAHOO,
        category=Category.RATES,
        interpretation=(
            "30-day Fed Funds futures. Price = 100 - implied rate. "
            "Shows market expectations for Fed policy path."
        ),
    ),
)


# =============================================================================
# TIER 4: DOLLAR & FX
# Global liquidity conditions and carry trade signals.
# =============================================================================

FX: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="EURUSD",
        symbol="EURUSD=X",
        source=DataSource.YAHOO,
        category=Category.FX,
        interpretation=(
            "EUR vs USD. 57% of DXY weight. ECB policy, EU growth expectations. "
            "Rising = EUR strengthening = USD weakening."
        ),
    ),
    WatchlistInstrument(
        name="USDJPY",
        symbol="USDJPY=X",
        source=DataSource.YAHOO,
        category=Category.FX,
        interpretation=(
            "Carry trade barometer. Rising (weak yen) = carry trade ON, risk-on. "
            "Falling sharply = carry unwind, can cascade (see Aug 2024)."
        ),
    ),
    WatchlistInstrument(
        name="USDCNH",
        symbol="CNH=X",
        source=DataSource.YAHOO,
        category=Category.FX,
        interpretation=(
            "Offshore yuan. Rising = CNH weakening = China policy easing or stress. "
            "PBOC letting CNH weaken = exporting deflation, trade tension risk."
        ),
    ),
    WatchlistInstrument(
        name="USDCHF",
        symbol="USDCHF=X",
        source=DataSource.YAHOO,
        category=Category.FX,
        interpretation=(
            "Pure safe haven signal. Falling (CHF strengthening) = European stress "
            "specifically. Swiss franc as flight-to-safety destination."
        ),
    ),
)


# =============================================================================
# TIER 5: CREDIT
# Early warning system for systemic stress.
# =============================================================================

CREDIT: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="HYG",
        symbol="HYG",
        source=DataSource.YAHOO,
        category=Category.CREDIT,
        interpretation=(
            "High yield bond ETF. HYG weak + SPX strong = divergence warning. "
            "Credit often leads equity. When they disagree, credit is usually right."
        ),
    ),
    WatchlistInstrument(
        name="LQD",
        symbol="LQD",
        source=DataSource.YAHOO,
        category=Category.CREDIT,
        interpretation=(
            "Investment grade bond ETF. LQD/HYG ratio rising = flight to quality. "
            "Duration + credit risk in one instrument."
        ),
    ),
    WatchlistInstrument(
        name="HY_Spread",
        symbol="BAMLH0A0HYM2",
        source=DataSource.FRED,
        category=Category.CREDIT,
        interpretation=(
            "ICE BofA HY Option-Adjusted Spread. >400bps=elevated, >500bps=recession "
            "priced, >800bps=crisis. Key credit stress indicator."
        ),
        alert_thresholds=AlertThresholds({"elevated": 400, "recession": 500, "crisis": 800}),
    ),
)


# =============================================================================
# TIER 6: COMMODITIES
# Growth and inflation signals beyond core metals.
# =============================================================================

COMMODITIES: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="Silver",
        symbol="SI=F",
        source=DataSource.YAHOO,
        category=Category.COMMODITIES,
        interpretation=(
            "Industrial + precious hybrid. More volatile than gold. "
            "Outperforms gold in late-cycle precious rallies."
        ),
    ),
    WatchlistInstrument(
        name="Copper",
        symbol="HG=F",
        source=DataSource.YAHOO,
        category=Category.COMMODITIES,
        interpretation=(
            "Dr. Copper - global growth proxy. China construction, EV demand. "
            "Copper/Gold ratio rising = growth optimism."
        ),
    ),
    WatchlistInstrument(
        name="Natural_Gas",
        symbol="NG=F",
        source=DataSource.YAHOO,
        category=Category.COMMODITIES,
        interpretation=(
            "Energy/weather sensitive. Europe energy security concerns. "
            "Highly seasonal. Utility cost driver."
        ),
    ),
)


# =============================================================================
# TIER 7: BREADTH
# Confirms or denies headline index moves.
# =============================================================================

BREADTH: tuple[WatchlistInstrument, ...] = (
    WatchlistInstrument(
        name="Russell_2000",
        symbol="^RUT",
        source=DataSource.YAHOO,
        category=Category.BREADTH,
        interpretation=(
            "Small cap health. Small caps lead at cycle turns. "
            "Weak RUT + strong SPX = narrowing leadership, fragile rally."
        ),
    ),
    WatchlistInstrument(
        name="Equal_Weight_SP500",
        symbol="RSP",
        source=DataSource.YAHOO,
        category=Category.BREADTH,
        interpretation=(
            "Average stock performance. RSP underperforming SPY = mega-cap driven "
            "rally, fewer stocks participating. Bad breadth precedes corrections."
        ),
    ),
    WatchlistInstrument(
        name="SPY",
        symbol="SPY",
        source=DataSource.YAHOO,
        category=Category.BREADTH,
        interpretation=(
            "S&P 500 ETF. Used for SPY/RSP ratio calculation. "
            "Cap-weighted benchmark for comparison with equal-weight."
        ),
    ),
)


# =============================================================================
# CALCULATED RATIOS
# Derived from raw instrument data during ingestion.
# =============================================================================


@dataclass(frozen=True)
class CalculatedRatio:
    """Definition of a ratio calculated from two instruments."""

    name: str
    numerator_symbol: str
    denominator_symbol: str
    interpretation: str


CALCULATED_RATIOS: tuple[CalculatedRatio, ...] = (
    CalculatedRatio(
        name="gold_silver_ratio",
        numerator_symbol="GC=F",
        denominator_symbol="SI=F",
        interpretation=(
            "Gold/Silver ratio. Rising = risk-off, defensive positioning. "
            "Falling = risk-on, silver catching up. Historical avg ~60."
        ),
    ),
    CalculatedRatio(
        name="copper_gold_ratio",
        numerator_symbol="HG=F",
        denominator_symbol="GC=F",
        interpretation=(
            "Copper/Gold ratio. Rising = growth optimism, industrial > safe haven. "
            "Falling = defensive, bonds/utilities outperform."
        ),
    ),
    CalculatedRatio(
        name="vix_term_structure",
        numerator_symbol="^VIX",
        denominator_symbol="VX=F",
        interpretation=(
            "VIX/VIX Futures ratio. <1 = contango (normal, calm). "
            ">1 = backwardation (panic, near-term hedging demand)."
        ),
    ),
    CalculatedRatio(
        name="vix_vix3m_ratio",
        numerator_symbol="^VIX",
        denominator_symbol="^VIX3M",
        interpretation=(
            "VIX/VIX3M ratio. >1 = near-term panic, backwardation. "
            "<0.85 = complacent, potential top warning."
        ),
    ),
    CalculatedRatio(
        name="spy_rsp_ratio",
        numerator_symbol="SPY",
        denominator_symbol="RSP",
        interpretation=(
            "SPY/RSP (cap-weight vs equal-weight). Rising = mega-cap outperformance, "
            "narrow leadership. Falling = broadening, healthier rally."
        ),
    ),
    CalculatedRatio(
        name="hyg_lqd_ratio",
        numerator_symbol="HYG",
        denominator_symbol="LQD",
        interpretation=(
            "HYG/LQD (high yield vs investment grade). Rising = risk appetite "
            "for credit. Falling = flight to quality."
        ),
    ),
)


# =============================================================================
# AGGREGATED EXPORTS
# =============================================================================

ALL_INSTRUMENTS: tuple[WatchlistInstrument, ...] = (
    VITAL_SIGNS + VOLATILITY + RATES + FX + CREDIT + COMMODITIES + BREADTH
)


def get_yahoo_symbols() -> list[str]:
    """Get all symbols that need to be fetched from Yahoo Finance."""
    symbols = [i.symbol for i in ALL_INSTRUMENTS if i.source == DataSource.YAHOO]
    # Add any ratio components not already included
    ratio_symbols = set()
    for ratio in CALCULATED_RATIOS:
        ratio_symbols.add(ratio.numerator_symbol)
        ratio_symbols.add(ratio.denominator_symbol)
    for sym in ratio_symbols:
        if sym not in symbols and not sym.startswith("DGS") and not sym.startswith("T"):
            # Exclude FRED series
            if sym not in [i.symbol for i in ALL_INSTRUMENTS if i.source == DataSource.FRED]:
                symbols.append(sym)
    return sorted(set(symbols))


def get_fred_series() -> list[str]:
    """Get all series IDs that need to be fetched from FRED."""
    return sorted({i.symbol for i in ALL_INSTRUMENTS if i.source == DataSource.FRED})


def get_all_by_category() -> dict[Category, list[WatchlistInstrument]]:
    """Get instruments grouped by category."""
    result: dict[Category, list[WatchlistInstrument]] = {}
    for instrument in ALL_INSTRUMENTS:
        if instrument.category not in result:
            result[instrument.category] = []
        result[instrument.category].append(instrument)
    return result


def get_instrument_by_symbol(symbol: str) -> WatchlistInstrument | None:
    """Look up an instrument by its symbol."""
    for instrument in ALL_INSTRUMENTS:
        if instrument.symbol == symbol:
            return instrument
    return None


def get_instrument_by_name(name: str) -> WatchlistInstrument | None:
    """Look up an instrument by its name."""
    for instrument in ALL_INSTRUMENTS:
        if instrument.name == name:
            return instrument
    return None


# =============================================================================
# REGIME THRESHOLDS
# Used by market_context.py for classification.
# =============================================================================

VOLATILITY_REGIME_THRESHOLDS: dict[str, dict[str, float]] = {
    "crisis": {"vix_min": 40},
    "fear": {"vix_min": 30},
    "elevated": {"vix_min": 20},
    "normal": {"vix_min": 15},
    "calm": {"vix_min": 0},
}

DOLLAR_REGIME_THRESHOLDS: dict[str, dict[str, float]] = {
    # Based on DXY 1-day change percentage
    "strong": {"change_min": 0.3},
    "neutral": {"change_min": -0.3},
    "weak": {"change_min": float("-inf")},
}

CURVE_REGIME_THRESHOLDS: dict[str, dict[str, float]] = {
    # Based on 2s10s spread in percentage points
    "steep": {"spread_min": 1.0},
    "normal": {"spread_min": 0.25},
    "flat": {"spread_min": 0.0},
    "inverted": {"spread_min": float("-inf")},
}

CREDIT_REGIME_THRESHOLDS: dict[str, dict[str, float]] = {
    # Based on HY spread in basis points
    "crisis": {"spread_min": 800},
    "stressed": {"spread_min": 500},
    "wide": {"spread_min": 400},
    "normal": {"spread_min": 300},
    "tight": {"spread_min": 0},
}


# =============================================================================
# POSITION SIZING MULTIPLIERS
# Used to suggest position size adjustments based on regime.
# =============================================================================

POSITION_SIZE_MULTIPLIERS = {
    "volatility": {
        "crisis": 0.25,
        "fear": 0.50,
        "elevated": 0.75,
        "normal": 1.0,
        "calm": 1.0,
    },
    "credit": {
        "crisis": 0.25,
        "stressed": 0.50,
        "wide": 0.75,
        "normal": 1.0,
        "tight": 1.0,
    },
}
