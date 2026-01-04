"""Time horizon-specific recommendation engine for trading theses.

This module provides horizon-aware recommendations that match instruments
to appropriate time frames:

1. SHORT_TERM (1-5 days): Futures, high-liquidity ETFs, spot instruments
2. MEDIUM_TERM (2-8 weeks): Sector ETFs, individual stocks, options spreads
3. LONG_TERM (6+ months): Equity accumulation, miners, long-dated options

Each horizon has different risk/reward characteristics and appropriate
instruments for execution.

Usage:
    from app.analysis.time_horizons import (
        analyze_time_horizons,
        HorizonAnalysis,
        format_horizons_for_prompt,
    )

    analysis = analyze_time_horizons(
        event_headline="Russia threatens oil pipeline cutoff",
        channels=["oil_supply_disruption"],
        historical_cases=[case1, case2],
        quantitative_impacts={"production_drop_pct": 50},
    )
    print(analysis.short_term.instruments)  # ['CL=F', 'BZ=F', 'USO']
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.analysis.conviction import ConvictionLevel


class TradeHorizon(Enum):
    """Time horizons for trading recommendations."""

    SHORT_TERM = "short_term"  # 1-5 days
    MEDIUM_TERM = "medium_term"  # 2-8 weeks
    LONG_TERM = "long_term"  # 6+ months


class TradeDirection(Enum):
    """Direction of the recommended trade."""

    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"  # e.g., straddle, pairs trade


@dataclass
class HorizonRecommendation:
    """A trading recommendation for a specific time horizon."""

    horizon: TradeHorizon
    instruments: list[str] = field(default_factory=list)
    direction: TradeDirection = TradeDirection.NEUTRAL
    rationale: str = ""
    conviction: ConvictionLevel = ConvictionLevel.INSUFFICIENT
    entry_approach: str = ""  # e.g., "scale in", "await pullback", "immediate"
    risk_management: str = ""  # e.g., "stop at -5%", "hedge with puts"
    expected_magnitude: str = ""  # e.g., "5-15% move"
    key_levels: dict[str, float] = field(default_factory=dict)  # support/resistance

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "horizon": self.horizon.value,
            "horizon_label": HORIZON_LABELS[self.horizon],
            "instruments": self.instruments,
            "direction": self.direction.value,
            "rationale": self.rationale,
            "conviction": self.conviction.value,
            "entry_approach": self.entry_approach,
            "risk_management": self.risk_management,
            "expected_magnitude": self.expected_magnitude,
            "key_levels": self.key_levels,
        }


@dataclass
class HorizonAnalysis:
    """Complete horizon analysis with recommendations for all timeframes."""

    short_term: HorizonRecommendation | None = None
    medium_term: HorizonRecommendation | None = None
    long_term: HorizonRecommendation | None = None
    event_summary: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_summary": self.event_summary,
            "short_term": self.short_term.to_dict() if self.short_term else None,
            "medium_term": self.medium_term.to_dict() if self.medium_term else None,
            "long_term": self.long_term.to_dict() if self.long_term else None,
            "warnings": self.warnings,
        }

    def all_recommendations(self) -> list[HorizonRecommendation]:
        """Return all non-None recommendations."""
        recs = [self.short_term, self.medium_term, self.long_term]
        return [r for r in recs if r is not None]


# Horizon metadata
HORIZON_LABELS: dict[TradeHorizon, str] = {
    TradeHorizon.SHORT_TERM: "Short-Term (1-5 days)",
    TradeHorizon.MEDIUM_TERM: "Medium-Term (2-8 weeks)",
    TradeHorizon.LONG_TERM: "Long-Term (6+ months)",
}

HORIZON_DESCRIPTIONS: dict[TradeHorizon, str] = {
    TradeHorizon.SHORT_TERM: (
        "Immediate reaction trades. Focus on high-liquidity instruments with "
        "tight spreads. Use futures and spot ETFs for quick execution."
    ),
    TradeHorizon.MEDIUM_TERM: (
        "Trend-following positions. Use sector ETFs and individual stocks for "
        "larger moves. Consider options spreads for defined risk."
    ),
    TradeHorizon.LONG_TERM: (
        "Structural positioning. Accumulate equity positions in quality names. "
        "Use miners and producers for leveraged commodity exposure."
    ),
}

# =============================================================================
# INSTRUMENT MAPPING BY HORIZON AND CHANNEL TYPE
# =============================================================================

# Short-term: Futures, high-volume ETFs, spot instruments
SHORT_TERM_INSTRUMENTS: dict[str, list[str]] = {
    # Commodity channels
    "oil_supply_disruption": ["CL=F", "BZ=F", "USO", "XLE"],
    "oil_demand_shock": ["CL=F", "BZ=F", "USO", "XLE"],
    "natural_gas_supply": ["NG=F", "UNG", "BOIL"],
    "metals_supply": ["GC=F", "SI=F", "HG=F", "GLD", "SLV"],
    "agricultural_supply": ["ZW=F", "ZC=F", "ZS=F", "DBA"],
    # Currency channels
    "dollar_strength": ["DX=F", "UUP", "EURUSD=X", "GLD"],
    "dollar_weakness": ["DX=F", "UDN", "GLD", "EEM"],
    "em_currency_stress": ["EEM", "EMB", "UUP"],
    "carry_trade_unwind": ["USDJPY=X", "FXY", "^VIX", "VIXY"],
    "yuan_devaluation": ["CNH=X", "FXI", "EEM"],
    # Rates channels
    "fed_hawkish": ["TLT", "IEF", "SHY", "^TNX"],
    "fed_dovish": ["TLT", "GLD", "QQQ", "IEF"],
    "yield_curve_inversion": ["TLT", "SHY", "XLF", "KRE"],
    "credit_tightening": ["HYG", "JNK", "LQD", "^VIX"],
    "liquidity_crisis": ["^VIX", "VIXY", "TLT", "GLD", "BIL"],
    # Risk sentiment channels
    "risk_off_flight": ["TLT", "GLD", "^VIX", "VIXY", "FXY"],
    "risk_on_rally": ["SPY", "QQQ", "IWM", "HYG"],
    "vix_spike": ["^VIX", "VIXY", "UVXY", "SPY"],
    # Sanctions channels
    "trade_sanctions": ["SPY", "EEM", "SMH", "XLE"],
    "capital_controls": ["EEM", "BTC-USD", "GLD"],
    "export_restrictions": ["SMH", "INTC", "AMD", "NVDA"],
    # Inflation channels
    "inflation_spike": ["TIP", "GLD", "XLE", "DJP"],
    "deflation_risk": ["TLT", "EDV", "XLU"],
    "wage_pressure": ["XLY", "XRT", "XLP"],
}

# Medium-term: Sector ETFs, individual stocks, options
MEDIUM_TERM_INSTRUMENTS: dict[str, list[str]] = {
    # Commodity channels
    "oil_supply_disruption": ["XLE", "OXY", "CVX", "XOM", "DVN", "PXD", "SLB"],
    "oil_demand_shock": ["XLE", "VDE", "PSX", "VLO", "MPC", "DAL", "UAL"],
    "natural_gas_supply": ["LNG", "GLNG", "EQT", "RRC", "AR", "SWN"],
    "metals_supply": ["COPX", "CPER", "FCX", "SCCO", "TECK", "NEM", "GOLD"],
    "agricultural_supply": ["DBA", "ADM", "BG", "CTVA", "MOS", "NTR", "CF"],
    # Currency channels
    "dollar_strength": ["UUP", "EEM", "VWO", "GLD", "SLV", "FXE"],
    "dollar_weakness": ["UDN", "GLD", "SLV", "EEM", "VWO", "COPX"],
    "em_currency_stress": ["EEM", "VWO", "EMB", "EMLC", "EWZ", "EWW"],
    "carry_trade_unwind": ["EWJ", "FXY", "SPY", "QQQ", "HYG"],
    "yuan_devaluation": ["FXI", "KWEB", "MCHI", "ASHR", "CQQQ"],
    # Rates channels
    "fed_hawkish": ["TLT", "XLF", "KRE", "ARKK"],
    "fed_dovish": ["TLT", "ARKK", "XLK", "SMH", "QQQ"],
    "yield_curve_inversion": ["XLF", "KRE", "XLU", "XLP"],
    "credit_tightening": ["HYG", "JNK", "XLF", "KRE", "IWM"],
    "liquidity_crisis": ["TLT", "GLD", "XLU", "XLP", "BIL"],
    # Risk sentiment channels
    "risk_off_flight": ["TLT", "GLD", "XLU", "XLP", "NEM", "GOLD"],
    "risk_on_rally": ["SPY", "QQQ", "IWM", "ARKK", "SMH", "HYG"],
    "vix_spike": ["SPY", "QQQ", "IWM", "HYG", "XLF"],
    # Sanctions channels
    "trade_sanctions": ["LMT", "RTX", "NOC", "GD", "SMH"],
    "capital_controls": ["BTC-USD", "ETH-USD", "GLD", "NEM"],
    "export_restrictions": ["SMH", "INTC", "AMD", "NVDA", "ASML", "MU"],
    # Inflation channels
    "inflation_spike": ["TIP", "XLE", "XLB", "PDBC", "NEM", "GOLD"],
    "deflation_risk": ["TLT", "EDV", "XLU", "VNQ"],
    "wage_pressure": ["XLI", "XLF", "XLP", "PG", "KO"],
}

# Long-term: Equity accumulation, miners, producers
LONG_TERM_INSTRUMENTS: dict[str, list[str]] = {
    # Commodity channels
    "oil_supply_disruption": ["XOM", "CVX", "OXY", "DVN", "PXD", "EOG", "COP"],
    "oil_demand_shock": ["XOM", "CVX", "PSX", "VLO", "MPC"],
    "natural_gas_supply": ["LNG", "EQT", "RRC", "AR", "SWN", "TELL"],
    "metals_supply": ["FCX", "SCCO", "TECK", "AA", "NEM", "GOLD", "WPM", "FNV"],
    "agricultural_supply": ["ADM", "BG", "CTVA", "MOS", "NTR", "CF", "DE"],
    # Currency channels
    "dollar_strength": ["EEM", "VWO", "GLD"],
    "dollar_weakness": ["NEM", "GOLD", "WPM", "FNV", "FCX", "EEM"],
    "em_currency_stress": ["VWO", "EEM"],
    "carry_trade_unwind": ["EWJ", "VWO"],
    "yuan_devaluation": ["KWEB", "BABA", "JD", "PDD"],
    # Rates channels
    "fed_hawkish": ["XLF", "JPM", "BAC", "WFC", "GS"],
    "fed_dovish": ["MSFT", "GOOGL", "AMZN", "NVDA", "META"],
    "yield_curve_inversion": ["XLU", "NEE", "DUK", "SO", "D"],
    "credit_tightening": ["XLU", "XLP", "JNJ", "PG", "KO"],
    "liquidity_crisis": ["NEM", "GOLD", "WPM", "FNV", "RGLD"],
    # Risk sentiment channels
    "risk_off_flight": ["NEM", "GOLD", "WPM", "FNV", "XLU", "XLP"],
    "risk_on_rally": ["SPY", "QQQ", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "vix_spike": ["MSFT", "GOOGL", "JNJ", "PG"],  # Quality for accumulation
    # Sanctions channels
    "trade_sanctions": ["LMT", "RTX", "NOC", "GD", "BA"],
    "capital_controls": ["NEM", "GOLD", "WPM"],
    "export_restrictions": ["INTC", "AMD", "NVDA", "ASML", "AMAT", "LRCX"],
    # Inflation channels
    "inflation_spike": ["NEM", "GOLD", "WPM", "FCX", "XOM", "CVX"],
    "deflation_risk": ["NEE", "DUK", "SO", "XLU"],
    "wage_pressure": ["MSFT", "GOOGL", "META"],  # Tech with low labor intensity
}

# Default instruments when channel not matched
DEFAULT_INSTRUMENTS: dict[TradeHorizon, list[str]] = {
    TradeHorizon.SHORT_TERM: ["SPY", "QQQ", "TLT", "GLD", "^VIX"],
    TradeHorizon.MEDIUM_TERM: ["SPY", "QQQ", "TLT", "GLD", "XLE", "XLF"],
    TradeHorizon.LONG_TERM: ["SPY", "QQQ", "VTI", "MSFT", "GOOGL", "NEM"],
}

# Entry approach by horizon
ENTRY_APPROACHES: dict[TradeHorizon, list[str]] = {
    TradeHorizon.SHORT_TERM: [
        "Enter immediately on confirmation",
        "Use limit orders at current levels",
        "Scale in over 1-2 sessions if size is large",
    ],
    TradeHorizon.MEDIUM_TERM: [
        "Scale in over 3-5 sessions",
        "Await pullback to key support levels",
        "Build position on dips",
        "Use 1/3 position sizing per entry",
    ],
    TradeHorizon.LONG_TERM: [
        "Accumulate on weakness over weeks",
        "Use dollar-cost averaging approach",
        "Build core position, add on pullbacks",
        "Consider selling puts to enter at lower prices",
    ],
}

# Risk management by horizon
RISK_MANAGEMENT: dict[TradeHorizon, list[str]] = {
    TradeHorizon.SHORT_TERM: [
        "Tight stop-loss at -3-5%",
        "Take partial profits at +5-10%",
        "Use trailing stops after initial move",
        "Size position for max 1% portfolio risk",
    ],
    TradeHorizon.MEDIUM_TERM: [
        "Stop-loss at -8-12% or key support break",
        "Hedge with protective puts if conviction is medium",
        "Scale out in thirds as targets hit",
        "Rebalance if position exceeds 5% of portfolio",
    ],
    TradeHorizon.LONG_TERM: [
        "Wide stops at -15-20% or thesis invalidation",
        "Use options collar for downside protection",
        "Rebalance quarterly to target weight",
        "Focus on thesis validity, not price volatility",
    ],
}


def get_instruments_for_horizon(
    horizon: TradeHorizon,
    channel_types: list[str],
    max_instruments: int = 8,
) -> list[str]:
    """
    Get appropriate instruments for a horizon based on channel types.

    Args:
        horizon: Trading horizon
        channel_types: List of transmission channel type values
        max_instruments: Maximum instruments to return

    Returns:
        Deduplicated list of instrument symbols
    """
    instrument_map = {
        TradeHorizon.SHORT_TERM: SHORT_TERM_INSTRUMENTS,
        TradeHorizon.MEDIUM_TERM: MEDIUM_TERM_INSTRUMENTS,
        TradeHorizon.LONG_TERM: LONG_TERM_INSTRUMENTS,
    }

    mapping = instrument_map.get(horizon, {})
    instruments: list[str] = []
    seen: set[str] = set()

    # Get instruments from matched channels
    for channel_type in channel_types:
        for instrument in mapping.get(channel_type, []):
            if instrument not in seen:
                seen.add(instrument)
                instruments.append(instrument)
                if len(instruments) >= max_instruments:
                    return instruments

    # Fall back to defaults if no matches
    if not instruments:
        instruments = DEFAULT_INSTRUMENTS.get(horizon, [])[:max_instruments]

    return instruments[:max_instruments]


def determine_direction_from_behavior(
    horizon: TradeHorizon,
    time_horizon_behavior: dict[str, Any] | None,
    channel_types: list[str],
) -> TradeDirection:
    """
    Determine trade direction based on historical time horizon behavior.

    Args:
        horizon: Trading horizon
        time_horizon_behavior: Historical behavior data from case files
        channel_types: Matched channel types

    Returns:
        TradeDirection based on analysis
    """
    if not time_horizon_behavior:
        # Default based on channel type
        bearish_channels = {
            "risk_off_flight",
            "credit_tightening",
            "liquidity_crisis",
            "vix_spike",
            "dollar_strength",
            "fed_hawkish",
        }
        if any(ct in bearish_channels for ct in channel_types):
            return TradeDirection.SHORT
        return TradeDirection.LONG

    # Map horizon to behavior key
    horizon_key_map = {
        TradeHorizon.SHORT_TERM: "short_term_1_5d",
        TradeHorizon.MEDIUM_TERM: "medium_term_2_8w",
        TradeHorizon.LONG_TERM: "long_term_6m_plus",
    }

    behavior_key = horizon_key_map.get(horizon, "short_term_1_5d")
    behavior = time_horizon_behavior.get(behavior_key, {})

    # Check primary commodity direction (usually oil for supply disruptions)
    oil_direction = behavior.get("oil_direction", "").lower()
    gold_direction = behavior.get("gold_direction", "").lower()

    # Prioritize oil for commodity channels
    commodity_channels = {
        "oil_supply_disruption",
        "oil_demand_shock",
        "natural_gas_supply",
    }
    if any(ct in commodity_channels for ct in channel_types):
        if oil_direction == "up":
            return TradeDirection.LONG
        elif oil_direction == "down":
            return TradeDirection.SHORT

    # For other channels, check gold (often a proxy for risk sentiment)
    if gold_direction == "up":
        return TradeDirection.LONG
    elif gold_direction == "down":
        return TradeDirection.SHORT

    return TradeDirection.NEUTRAL


def determine_magnitude_from_behavior(
    horizon: TradeHorizon,
    time_horizon_behavior: dict[str, Any] | None,
    quantitative_impacts: dict[str, Any] | None,
) -> str:
    """
    Determine expected magnitude based on historical behavior.

    Args:
        horizon: Trading horizon
        time_horizon_behavior: Historical behavior data
        quantitative_impacts: Quantitative impact data

    Returns:
        String describing expected magnitude
    """
    if time_horizon_behavior:
        horizon_key_map = {
            TradeHorizon.SHORT_TERM: "short_term_1_5d",
            TradeHorizon.MEDIUM_TERM: "medium_term_2_8w",
            TradeHorizon.LONG_TERM: "long_term_6m_plus",
        }
        behavior_key = horizon_key_map.get(horizon, "short_term_1_5d")
        behavior = time_horizon_behavior.get(behavior_key, {})

        oil_mag = behavior.get("oil_magnitude_pct", 0)
        gold_mag = behavior.get("gold_magnitude_pct", 0)

        if oil_mag or gold_mag:
            parts = []
            if oil_mag:
                parts.append(f"Oil {oil_mag:+.0f}%")
            if gold_mag:
                parts.append(f"Gold {gold_mag:+.0f}%")
            return ", ".join(parts)

    # Fall back to quantitative impacts
    if quantitative_impacts:
        price_impact = quantitative_impacts.get(
            "peak_price_impact_pct", quantitative_impacts.get("price_impact_pct", 0)
        )
        if price_impact:
            return f"Primary asset {price_impact:+.0f}%"

    # Default estimates by horizon
    defaults = {
        TradeHorizon.SHORT_TERM: "5-15% in primary instruments",
        TradeHorizon.MEDIUM_TERM: "15-40% in primary instruments",
        TradeHorizon.LONG_TERM: "Variable; thesis-dependent",
    }
    return defaults.get(horizon, "Unknown")


def build_rationale(
    horizon: TradeHorizon,
    channel_types: list[str],
    time_horizon_behavior: dict[str, Any] | None,
) -> str:
    """
    Build rationale text for a horizon recommendation.

    Args:
        horizon: Trading horizon
        channel_types: Matched channel types
        time_horizon_behavior: Historical behavior data

    Returns:
        Rationale string
    """
    parts = []

    # Add horizon-specific context
    if horizon == TradeHorizon.SHORT_TERM:
        parts.append("Immediate event reaction expected.")
    elif horizon == TradeHorizon.MEDIUM_TERM:
        parts.append("Event impact typically compounds over this period.")
    else:
        parts.append("Structural positioning for longer-term thesis.")

    # Add behavior-based rationale
    if time_horizon_behavior:
        horizon_key_map = {
            TradeHorizon.SHORT_TERM: "short_term_1_5d",
            TradeHorizon.MEDIUM_TERM: "medium_term_2_8w",
            TradeHorizon.LONG_TERM: "long_term_6m_plus",
        }
        behavior_key = horizon_key_map.get(horizon, "short_term_1_5d")
        behavior = time_horizon_behavior.get(behavior_key, {})

        driver = behavior.get("primary_driver", "")
        volatility = behavior.get("volatility", "")

        if driver:
            parts.append(f"Primary driver: {driver}.")
        if volatility and volatility != "normal":
            parts.append(f"Expected volatility: {volatility}.")

    # Add channel context
    if channel_types:
        channel_names = [ct.replace("_", " ").title() for ct in channel_types[:2]]
        parts.append(f"Channels: {', '.join(channel_names)}.")

    return " ".join(parts)


def analyze_time_horizons(
    event_headline: str,
    channel_types: list[str] | None = None,
    historical_cases: list[dict[str, Any]] | None = None,
    quantitative_impacts: dict[str, Any] | None = None,
    conviction_level: ConvictionLevel = ConvictionLevel.MEDIUM,
) -> HorizonAnalysis:
    """
    Analyze trading opportunities across all time horizons.

    This is the main entry point for horizon analysis. It combines:
    - Channel-based instrument selection
    - Historical behavior patterns
    - Quantitative impact data
    - Conviction level adjustments

    Args:
        event_headline: Event headline for context
        channel_types: List of transmission channel type values
        historical_cases: List of matched historical case data
        quantitative_impacts: Aggregated quantitative impact data
        conviction_level: Overall conviction level from conviction scoring

    Returns:
        HorizonAnalysis with recommendations for each timeframe
    """
    analysis = HorizonAnalysis(event_summary=event_headline)
    channel_types = channel_types or []

    # Extract time horizon behavior from historical cases
    time_horizon_behavior: dict[str, Any] | None = None
    if historical_cases:
        # Use the first case with time_horizon_behavior
        for case in historical_cases:
            if case.get("time_horizon_behavior"):
                time_horizon_behavior = case["time_horizon_behavior"]
                break

    # Build recommendations for each horizon
    for horizon in TradeHorizon:
        instruments = get_instruments_for_horizon(horizon, channel_types)

        if not instruments:
            continue

        direction = determine_direction_from_behavior(horizon, time_horizon_behavior, channel_types)
        magnitude = determine_magnitude_from_behavior(
            horizon, time_horizon_behavior, quantitative_impacts
        )
        rationale = build_rationale(horizon, channel_types, time_horizon_behavior)

        # Select entry and risk approaches
        entry_options = ENTRY_APPROACHES.get(horizon, [])
        entry_approach = entry_options[0] if entry_options else ""

        risk_options = RISK_MANAGEMENT.get(horizon, [])
        risk_management = risk_options[0] if risk_options else ""

        recommendation = HorizonRecommendation(
            horizon=horizon,
            instruments=instruments,
            direction=direction,
            rationale=rationale,
            conviction=conviction_level,
            entry_approach=entry_approach,
            risk_management=risk_management,
            expected_magnitude=magnitude,
        )

        if horizon == TradeHorizon.SHORT_TERM:
            analysis.short_term = recommendation
        elif horizon == TradeHorizon.MEDIUM_TERM:
            analysis.medium_term = recommendation
        else:
            analysis.long_term = recommendation

    # Add warnings based on data quality
    if not historical_cases:
        analysis.warnings.append("No historical case data available")
    if not quantitative_impacts:
        analysis.warnings.append("No quantitative impact data available")
    if conviction_level in (ConvictionLevel.LOW, ConvictionLevel.INSUFFICIENT):
        analysis.warnings.append(
            f"Low conviction ({conviction_level.value}); reduce position sizes"
        )

    return analysis


def format_horizons_for_prompt(analysis: HorizonAnalysis) -> str:
    """
    Format horizon analysis for LLM prompt inclusion.

    Args:
        analysis: HorizonAnalysis to format

    Returns:
        Formatted string for prompt injection
    """
    lines = ["=== TIME HORIZON ANALYSIS ==="]
    lines.append("")
    lines.append(f"Event: {analysis.event_summary}")
    lines.append("")

    for rec in analysis.all_recommendations():
        lines.append(f"### {HORIZON_LABELS[rec.horizon]}")
        lines.append(f"Direction: {rec.direction.value.upper()}")
        lines.append(f"Conviction: {rec.conviction.value.upper()}")
        lines.append(f"Instruments: {', '.join(rec.instruments)}")
        lines.append(f"Expected Move: {rec.expected_magnitude}")
        lines.append(f"Entry: {rec.entry_approach}")
        lines.append(f"Risk: {rec.risk_management}")
        lines.append(f"Rationale: {rec.rationale}")
        lines.append("")

    if analysis.warnings:
        lines.append("WARNINGS:")
        for warning in analysis.warnings:
            lines.append(f"  - {warning}")
        lines.append("")

    lines.append("=" * 29)

    return "\n".join(lines)
