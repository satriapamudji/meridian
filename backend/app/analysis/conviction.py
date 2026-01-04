"""Component-based conviction scoring for trading theses.

This module provides a structured approach to calculating conviction scores
for trading theses based on multiple weighted components:

1. Historical precedent strength (0-25 points)
2. Quantitative impact magnitude (0-25 points)
3. Transmission channel clarity (0-20 points)
4. Timing/catalyst clarity (0-15 points)
5. Counter-case discount (0 to -15 points)

Final conviction score: 0-100 scale mapped to HIGH/MEDIUM/LOW labels.

Usage:
    from app.analysis.conviction import (
        calculate_conviction_score,
        ConvictionResult,
        ConvictionLevel,
    )

    result = calculate_conviction_score(
        historical_cases=[case1, case2],
        quantitative_impacts={"production_drop_pct": 50, "price_impact_pct": 30},
        matched_channels=["oil_supply_disruption", "sanctions_trade_war"],
        catalyst_clarity="high",
        counter_case_strength="weak",
    )
    print(result.total_score)  # 78
    print(result.level)  # ConvictionLevel.HIGH
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConvictionLevel(Enum):
    """Conviction level classification."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class CatalystClarity(Enum):
    """How clear is the catalyst/timing for the trade."""

    HIGH = "high"  # Specific date/event known
    MEDIUM = "medium"  # General timeframe known
    LOW = "low"  # Vague or uncertain
    NONE = "none"  # No clear catalyst


class CounterCaseStrength(Enum):
    """Strength of the counter-case/bear case."""

    STRONG = "strong"  # Compelling counter-arguments
    MODERATE = "moderate"  # Some valid concerns
    WEAK = "weak"  # Minor concerns
    NONE = "none"  # No significant counter-case


@dataclass
class ConvictionComponent:
    """A single component of the conviction score."""

    name: str
    raw_score: float
    max_score: float
    weight: float = 1.0
    rationale: str = ""

    @property
    def weighted_score(self) -> float:
        """Return the weighted contribution to total score."""
        return min(self.raw_score * self.weight, self.max_score)

    @property
    def percentage(self) -> float:
        """Return percentage of max possible for this component."""
        if self.max_score == 0:
            return 0.0
        return (self.raw_score / self.max_score) * 100


@dataclass
class ConvictionResult:
    """Result of conviction score calculation."""

    total_score: float
    level: ConvictionLevel
    components: list[ConvictionComponent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_score": round(self.total_score, 1),
            "level": self.level.value,
            "components": [
                {
                    "name": c.name,
                    "score": round(c.weighted_score, 1),
                    "max": c.max_score,
                    "percentage": round(c.percentage, 0),
                    "rationale": c.rationale,
                }
                for c in self.components
            ],
            "warnings": self.warnings,
        }


# Component scoring configuration
COMPONENT_CONFIG = {
    "historical_precedent": {"max_score": 25, "weight": 1.0},
    "quantitative_magnitude": {"max_score": 25, "weight": 1.0},
    "channel_clarity": {"max_score": 20, "weight": 1.0},
    "timing_catalyst": {"max_score": 15, "weight": 1.0},
    "counter_case_discount": {"max_score": 15, "weight": -1.0},  # Negative weight
}

# Thresholds for conviction levels
CONVICTION_THRESHOLDS = {
    ConvictionLevel.HIGH: 70,
    ConvictionLevel.MEDIUM: 50,
    ConvictionLevel.LOW: 30,
    ConvictionLevel.INSUFFICIENT: 0,
}


def calculate_conviction_score(
    historical_cases: list[dict[str, Any]] | None = None,
    quantitative_impacts: dict[str, Any] | None = None,
    matched_channels: list[str] | None = None,
    catalyst_clarity: str = "medium",
    counter_case_strength: str = "moderate",
) -> ConvictionResult:
    """
    Calculate a conviction score for a trading thesis.

    Args:
        historical_cases: List of matched historical case summaries
        quantitative_impacts: Dict with keys like production_drop_pct, price_impact_pct
        matched_channels: List of transmission channel types that match
        catalyst_clarity: "high", "medium", "low", or "none"
        counter_case_strength: "strong", "moderate", "weak", or "none"

    Returns:
        ConvictionResult with total score, level, and component breakdown
    """
    components: list[ConvictionComponent] = []
    warnings: list[str] = []

    # 1. Historical precedent component (0-25 points)
    hist_component = _score_historical_precedent(historical_cases or [])
    components.append(hist_component)
    if hist_component.raw_score < 10:
        warnings.append("Limited historical precedent data")

    # 2. Quantitative magnitude component (0-25 points)
    quant_component = _score_quantitative_magnitude(quantitative_impacts or {})
    components.append(quant_component)
    if quant_component.raw_score < 10:
        warnings.append("Limited quantitative impact data")

    # 3. Channel clarity component (0-20 points)
    channel_component = _score_channel_clarity(matched_channels or [])
    components.append(channel_component)

    # 4. Timing/catalyst component (0-15 points)
    timing_component = _score_timing_catalyst(catalyst_clarity)
    components.append(timing_component)

    # 5. Counter-case discount (0 to -15 points)
    counter_component = _score_counter_case(counter_case_strength)
    components.append(counter_component)

    # Calculate total score
    total = sum(c.weighted_score for c in components)
    total = max(0, min(100, total))  # Clamp to 0-100

    # Determine conviction level
    level = _classify_conviction_level(total)

    return ConvictionResult(
        total_score=total,
        level=level,
        components=components,
        warnings=warnings,
    )


def _score_historical_precedent(cases: list[dict[str, Any]]) -> ConvictionComponent:
    """
    Score based on historical case matches.

    Scoring logic:
    - 0 cases: 0 points
    - 1 case: 10 points
    - 2 cases: 15 points
    - 3+ cases: 20 points
    - Bonus: +5 if average significance_score > 80
    """
    config = COMPONENT_CONFIG["historical_precedent"]
    max_score = config["max_score"]

    if not cases:
        return ConvictionComponent(
            name="Historical Precedent",
            raw_score=0,
            max_score=max_score,
            rationale="No historical cases matched",
        )

    # Base score from number of cases
    case_count = len(cases)
    if case_count == 1:
        base_score = 10
    elif case_count == 2:
        base_score = 15
    else:
        base_score = 20

    # Bonus for high-significance cases
    significance_scores = [
        c.get("significance_score", 0) for c in cases if c.get("significance_score")
    ]
    avg_significance = (
        sum(significance_scores) / len(significance_scores) if significance_scores else 0
    )
    bonus = 5 if avg_significance > 80 else 0

    raw_score = min(base_score + bonus, max_score)

    return ConvictionComponent(
        name="Historical Precedent",
        raw_score=raw_score,
        max_score=max_score,
        rationale=f"{case_count} case(s) matched, avg significance {avg_significance:.0f}",
    )


def _score_quantitative_magnitude(impacts: dict[str, Any]) -> ConvictionComponent:
    """
    Score based on quantitative impact magnitude.

    Key metrics considered:
    - production_drop_pct: Higher = more impactful
    - price_impact_pct: Higher = more significant
    - global_supply_impact_pct: Market-wide significance
    """
    config = COMPONENT_CONFIG["quantitative_magnitude"]
    max_score = config["max_score"]

    if not impacts:
        return ConvictionComponent(
            name="Quantitative Magnitude",
            raw_score=0,
            max_score=max_score,
            rationale="No quantitative impact data available",
        )

    score = 0
    rationale_parts = []

    # Production drop scoring (0-10 points)
    prod_drop = impacts.get("production_drop_pct", 0)
    if prod_drop >= 90:
        score += 10
        rationale_parts.append(f"production drop {prod_drop}% (severe)")
    elif prod_drop >= 50:
        score += 7
        rationale_parts.append(f"production drop {prod_drop}% (major)")
    elif prod_drop >= 20:
        score += 4
        rationale_parts.append(f"production drop {prod_drop}% (moderate)")
    elif prod_drop > 0:
        score += 2
        rationale_parts.append(f"production drop {prod_drop}% (minor)")

    # Price impact scoring (0-10 points)
    price_impact = impacts.get("price_impact_pct", impacts.get("peak_price_impact_pct", 0))
    if price_impact >= 100:
        score += 10
        rationale_parts.append(f"price impact {price_impact}% (extreme)")
    elif price_impact >= 50:
        score += 7
        rationale_parts.append(f"price impact {price_impact}% (major)")
    elif price_impact >= 20:
        score += 4
        rationale_parts.append(f"price impact {price_impact}% (notable)")
    elif price_impact > 0:
        score += 2
        rationale_parts.append(f"price impact {price_impact}% (minor)")

    # Global supply impact bonus (0-5 points)
    global_impact = impacts.get("global_supply_impact_pct", 0)
    if global_impact >= 5:
        score += 5
        rationale_parts.append(f"global supply {global_impact}% (significant)")
    elif global_impact >= 2:
        score += 3
        rationale_parts.append(f"global supply {global_impact}%")
    elif global_impact > 0:
        score += 1

    raw_score = min(score, max_score)
    rationale = "; ".join(rationale_parts) if rationale_parts else "Minimal quantitative impact"

    return ConvictionComponent(
        name="Quantitative Magnitude",
        raw_score=raw_score,
        max_score=max_score,
        rationale=rationale,
    )


def _score_channel_clarity(channels: list[str]) -> ConvictionComponent:
    """
    Score based on transmission channel clarity.

    More matched channels = clearer transmission path = higher score.
    """
    config = COMPONENT_CONFIG["channel_clarity"]
    max_score = config["max_score"]

    if not channels:
        return ConvictionComponent(
            name="Channel Clarity",
            raw_score=0,
            max_score=max_score,
            rationale="No transmission channels identified",
        )

    channel_count = len(channels)
    if channel_count == 1:
        raw_score = 10
    elif channel_count == 2:
        raw_score = 15
    else:
        raw_score = 20

    return ConvictionComponent(
        name="Channel Clarity",
        raw_score=min(raw_score, max_score),
        max_score=max_score,
        rationale=f"{channel_count} channel(s): {', '.join(channels[:3])}",
    )


def _score_timing_catalyst(clarity: str) -> ConvictionComponent:
    """
    Score based on timing/catalyst clarity.
    """
    config = COMPONENT_CONFIG["timing_catalyst"]
    max_score = config["max_score"]

    clarity_lower = clarity.lower()
    if clarity_lower == "high":
        raw_score = 15
        rationale = "Clear catalyst with specific timing"
    elif clarity_lower == "medium":
        raw_score = 10
        rationale = "General timeframe identified"
    elif clarity_lower == "low":
        raw_score = 5
        rationale = "Vague or uncertain timing"
    else:
        raw_score = 0
        rationale = "No clear catalyst or timing"

    return ConvictionComponent(
        name="Timing/Catalyst",
        raw_score=raw_score,
        max_score=max_score,
        rationale=rationale,
    )


def _score_counter_case(strength: str) -> ConvictionComponent:
    """
    Score the counter-case discount (negative contribution).

    A strong counter-case reduces conviction; a weak one has minimal impact.
    """
    config = COMPONENT_CONFIG["counter_case_discount"]
    max_score = config["max_score"]

    strength_lower = strength.lower()
    if strength_lower == "strong":
        raw_score = 15  # Will be negated by weight
        rationale = "Strong counter-arguments present"
    elif strength_lower == "moderate":
        raw_score = 10
        rationale = "Some valid concerns identified"
    elif strength_lower == "weak":
        raw_score = 5
        rationale = "Minor concerns only"
    else:
        raw_score = 0
        rationale = "No significant counter-case"

    return ConvictionComponent(
        name="Counter-Case Discount",
        raw_score=raw_score,
        max_score=max_score,
        weight=-1.0,  # Negative weight = discount
        rationale=rationale,
    )


def _classify_conviction_level(score: float) -> ConvictionLevel:
    """
    Classify a numeric score into a conviction level.
    """
    if score >= CONVICTION_THRESHOLDS[ConvictionLevel.HIGH]:
        return ConvictionLevel.HIGH
    elif score >= CONVICTION_THRESHOLDS[ConvictionLevel.MEDIUM]:
        return ConvictionLevel.MEDIUM
    elif score >= CONVICTION_THRESHOLDS[ConvictionLevel.LOW]:
        return ConvictionLevel.LOW
    else:
        return ConvictionLevel.INSUFFICIENT


def format_conviction_for_prompt(result: ConvictionResult) -> str:
    """
    Format conviction result for LLM prompt inclusion.

    Args:
        result: ConvictionResult to format

    Returns:
        Formatted string for prompt injection
    """
    lines = ["=== CONVICTION ASSESSMENT ==="]
    lines.append("")
    lines.append(f"OVERALL: {result.level.value.upper()} ({result.total_score:.0f}/100)")
    lines.append("")
    lines.append("COMPONENT BREAKDOWN:")

    for comp in result.components:
        sign = "-" if comp.weight < 0 else "+"
        if comp.weight < 0:
            lines.append(f"  {comp.name}: {sign}{abs(comp.weighted_score):.0f} pts")
        else:
            lines.append(f"  {comp.name}: {comp.weighted_score:.0f}/{comp.max_score:.0f} pts")
        if comp.rationale:
            lines.append(f"    → {comp.rationale}")

    if result.warnings:
        lines.append("")
        lines.append("WARNINGS:")
        for warning in result.warnings:
            lines.append(f"  ⚠ {warning}")

    lines.append("")
    lines.append("=" * 27)

    return "\n".join(lines)
