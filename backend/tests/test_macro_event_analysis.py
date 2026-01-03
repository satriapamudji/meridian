from __future__ import annotations

from datetime import datetime, timezone
import json
import uuid

from app.analysis.macro_event_analysis import (
    AnalysisRequest,
    HistoricalCaseSummary,
    LocalHeuristicProvider,
    MacroEventRecord,
    MetalsKnowledgeEntry,
    build_prompt,
    parse_analysis_response,
)


def test_build_prompt_includes_event_and_case_ids() -> None:
    event_id = uuid.uuid4()
    case_id = uuid.uuid4()
    event = MacroEventRecord(
        id=event_id,
        source="reuters",
        headline="Fed signals patience",
        full_text="The committee held rates steady.",
        published_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        event_type="monetary_policy",
        regions=["US"],
        entities=["Federal Reserve"],
        significance_score=72,
    )
    metals = [
        MetalsKnowledgeEntry(metal="gold", category="patterns", content={"trend": "up"})
    ]
    cases = [
        HistoricalCaseSummary(
            id=case_id,
            event_name="Fed pause",
            date_range="2023",
            event_type="monetary_policy",
            significance_score=70,
            metal_impacts=None,
            crypto_transmission=None,
            lessons=["watch real rates"],
            counter_examples=[],
        )
    ]
    prompt = build_prompt(AnalysisRequest(event, metals, cases))

    assert "EVENT_JSON:" in prompt
    assert str(event_id) in prompt
    assert str(case_id) in prompt


def test_parse_analysis_response_normalizes_payload() -> None:
    payload = {
        "raw_facts": [" Fact one ", "Fact two"],
        "metal_impacts": {
            "gold": {"direction": "up", "magnitude": "medium", "driver": "rates"},
            "silver": {"direction": "flat", "magnitude": "low", "driver": "demand"},
            "copper": {"direction": "down", "magnitude": "high", "driver": "growth"},
        },
        "historical_precedent": "case_id 123",
        "counter_case": "insufficient data",
        "crypto_transmission": {
            "exists": True,
            "path": "liquidity",
            "strength": "medium",
            "relevant_assets": ["BTC", "ETH"],
        },
        "thesis_seed": "Monitor follow-through.",
    }

    analysis = parse_analysis_response(json.dumps(payload))

    assert analysis.raw_facts == ["Fact one", "Fact two"]
    assert analysis.crypto_transmission["exists"] is True
    assert analysis.crypto_transmission["strength"] == "moderate"
    assert analysis.crypto_transmission["relevant_assets"] == ["BTC", "ETH"]


def test_local_provider_returns_parsable_output() -> None:
    provider = LocalHeuristicProvider()
    prompt = "EVENT_JSON:\n{ \"headline\": \"Fed holds rates\" }\n"

    analysis = parse_analysis_response(provider.complete(prompt))

    assert analysis.raw_facts[0] == "Fed holds rates"
