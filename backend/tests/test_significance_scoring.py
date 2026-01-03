from __future__ import annotations

from app.analysis.significance import MacroEvent, classify_score, score_event


def test_score_event_with_structured_inputs() -> None:
    event = MacroEvent(
        source="reuters",
        headline="Fed signals rate cuts",
        event_type="monetary_policy",
        regions=["US"],
        entities=["Federal Reserve"],
    )

    scored = score_event(event)

    assert scored.components.structural == 88
    assert scored.components.transmission == 95
    assert scored.components.historical == 70
    assert scored.components.attention == 60
    assert scored.total_score == 82
    assert scored.priority_flag is True
    assert scored.tier == "priority"


def test_score_event_infers_event_type_from_text() -> None:
    event = MacroEvent(
        source="ap",
        headline="Fed raises rates again",
    )

    scored = score_event(event)

    assert scored.components.structural == 75
    assert scored.components.transmission == 90
    assert scored.components.historical == 65
    assert scored.components.attention == 55
    assert scored.total_score == 75
    assert scored.tier == "priority"


def test_classify_score_thresholds() -> None:
    assert classify_score(65) == "priority"
    assert classify_score(64) == "monitoring"
    assert classify_score(50) == "monitoring"
    assert classify_score(49) == "logged"
