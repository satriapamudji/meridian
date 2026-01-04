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
from app.analysis.asset_discovery import DiscoveryResult
from app.analysis.transmission_channels import ALL_CHANNELS


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
    metals = [MetalsKnowledgeEntry(metal="gold", category="patterns", content={"trend": "up"})]
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
    prompt = 'EVENT_JSON:\n{ "headline": "Fed holds rates" }\n'

    analysis = parse_analysis_response(provider.complete(prompt))

    assert analysis.raw_facts[0] == "Fed holds rates"


def test_build_prompt_includes_discovered_assets_section() -> None:
    """Test that discovered assets section is included in prompt when provided."""
    event_id = uuid.uuid4()
    event = MacroEventRecord(
        id=event_id,
        source="reuters",
        headline="Russia cuts gas to Europe",
        full_text="Russia announced pipeline cuts.",
        published_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        event_type="geopolitical",
        regions=["Russia", "Europe"],
        entities=["Gazprom"],
        significance_score=85,
    )
    metals = [MetalsKnowledgeEntry(metal="gold", category="patterns", content={"trend": "up"})]
    cases: list[HistoricalCaseSummary] = []

    # Without discovered assets
    prompt_without = build_prompt(AnalysisRequest(event, metals, cases))
    assert "DISCOVERED ASSETS" not in prompt_without

    # With discovered assets
    discovered_assets_section = """=== DISCOVERED ASSETS ===

TRANSMISSION CHANNELS:
  • Gas Supply Disruption
    European energy crisis scenario...

PRIMARY ASSETS (high relevance):
  CL=F, NG=F, UNG

========================="""
    prompt_with = build_prompt(
        AnalysisRequest(event, metals, cases, discovered_assets=discovered_assets_section)
    )
    assert "DISCOVERED ASSETS" in prompt_with
    assert "Gas Supply Disruption" in prompt_with
    assert "CL=F, NG=F, UNG" in prompt_with


def test_parse_analysis_response_handles_asset_opportunities() -> None:
    """Test that asset_opportunities field is parsed when present."""
    payload = {
        "raw_facts": ["Oil supply disrupted"],
        "metal_impacts": {
            "gold": {"direction": "up", "magnitude": "medium", "driver": "safe haven"},
            "silver": {"direction": "up", "magnitude": "low", "driver": "gold follows"},
            "copper": {"direction": "down", "magnitude": "medium", "driver": "demand fear"},
        },
        "historical_precedent": "case_id 456",
        "counter_case": "OPEC could increase production",
        "crypto_transmission": {
            "exists": False,
            "path": "",
            "strength": "none",
            "relevant_assets": [],
        },
        "thesis_seed": "Long oil, short copper",
        "asset_opportunities": [
            {
                "ticker": "CL=F",
                "direction": "long",
                "conviction": "high",
                "rationale": "Supply disruption",
            },
            {
                "ticker": "XLE",
                "direction": "long",
                "conviction": "medium",
                "rationale": "Energy sector benefits",
            },
        ],
    }

    analysis = parse_analysis_response(json.dumps(payload))

    assert analysis.asset_opportunities is not None
    assert len(analysis.asset_opportunities) == 2
    assert analysis.asset_opportunities[0]["ticker"] == "CL=F"
    assert analysis.asset_opportunities[0]["direction"] == "long"
    assert analysis.asset_opportunities[0]["conviction"] == "high"
    assert analysis.asset_opportunities[1]["ticker"] == "XLE"


def test_parse_analysis_response_preserves_discovery_result() -> None:
    """Test that discovery_result is preserved in analysis."""
    payload = {
        "raw_facts": ["Test fact"],
        "metal_impacts": {
            "gold": {"direction": "unknown", "magnitude": "unknown", "driver": "test"},
            "silver": {"direction": "unknown", "magnitude": "unknown", "driver": "test"},
            "copper": {"direction": "unknown", "magnitude": "unknown", "driver": "test"},
        },
        "historical_precedent": "none",
        "counter_case": "none",
        "crypto_transmission": {
            "exists": False,
            "path": "",
            "strength": "none",
            "relevant_assets": [],
        },
    }

    # Create a discovery result with channels
    discovery = DiscoveryResult(
        channels=[ALL_CHANNELS[0]],  # First channel
        primary_assets=["CL=F", "BZ=F"],
        secondary_assets=["XLE", "OXY"],
    )

    analysis = parse_analysis_response(json.dumps(payload), discovery_result=discovery)

    assert analysis.discovery_result is not None
    assert analysis.discovery_result is discovery
    assert analysis.discovery_result.primary_assets == ["CL=F", "BZ=F"]
    assert len(analysis.discovery_result.channels) == 1
