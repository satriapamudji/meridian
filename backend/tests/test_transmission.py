from __future__ import annotations

from app.analysis.transmission import evaluate_transmission, normalize_crypto_transmission


def test_normalize_crypto_transmission_maps_strength_and_assets() -> None:
    payload = {"exists": True, "path": "Bitcoin and USDC demand", "strength": "low"}

    normalized = normalize_crypto_transmission(payload)

    assert normalized["strength"] == "weak"
    assert normalized["relevant_assets"] == ["BTC", "USDC"]


def test_evaluate_transmission_uses_event_type_liquidity_path() -> None:
    result = evaluate_transmission("Fed hikes rates as liquidity tightens", "monetary_policy")

    assert result["exists"] is True
    assert result["strength"] == "weak"
    assert "BTC" in result["relevant_assets"]
