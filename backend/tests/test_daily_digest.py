from __future__ import annotations

from datetime import date, datetime, timezone

from app.services.digests import build_digest_payload


def test_build_digest_payload_renders_sections() -> None:
    digest_date = date(2026, 2, 1)
    window_start = datetime(2026, 2, 1, tzinfo=timezone.utc)
    window_end = datetime(2026, 2, 2, tzinfo=timezone.utc)
    priority_events = [
        {
            "id": "event-1",
            "headline": "Fed signals rate cuts",
            "score": 72,
            "published_at": "2026-02-01T08:00:00+00:00",
            "source": "reuters",
            "analysis_ready": True,
        }
    ]
    metals_snapshot = {
        "metals": {
            "gold": {
                "symbol": "GC=F",
                "price": 2000.0,
                "change_percent": 0.5,
                "as_of": "2026-02-01",
            },
            "silver": {
                "symbol": "SI=F",
                "price": 25.0,
                "change_percent": -0.2,
                "as_of": "2026-02-01",
            },
            "copper": {
                "symbol": "HG=F",
                "price": 4.0,
                "change_percent": None,
                "as_of": "2026-02-01",
            },
        },
        "ratio": {
            "name": "gold_silver",
            "value": 80.0,
            "change_percent": 1.25,
            "as_of": "2026-02-01",
        },
    }
    economic_calendar = [
        {
            "event_name": "CPI Release",
            "event_date": "2026-02-01T10:00:00+00:00",
            "region": "US",
            "impact_level": "high",
            "expected_value": "2.0%",
            "actual_value": "1.9%",
            "previous_value": "2.1%",
            "surprise_direction": "negative",
            "surprise_magnitude": 0.1,
        }
    ]
    active_theses = [
        {
            "id": "thesis-1",
            "title": "Silver mean reversion",
            "asset_type": "metal",
            "asset_symbol": "SLV",
            "status": "watching",
            "price_change_percent": 3.2,
            "updated_at": "2026-02-01T00:00:00+00:00",
        }
    ]

    digest = build_digest_payload(
        digest_date,
        window_start,
        window_end,
        priority_events,
        metals_snapshot,
        economic_calendar,
        active_theses,
        generated_at=datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc),
    )

    assert "MERIDIAN DAILY BRIEFING" in digest.full_digest
    assert "PRIORITY EVENTS (1)" in digest.full_digest
    assert "- Fed signals rate cuts (72/100) [analysis ready]" in digest.full_digest
    assert "Gold: $2000.00 (+0.50%)" in digest.full_digest
    assert "Silver: $25.00 (-0.20%)" in digest.full_digest
    assert "Copper: $4.00 (n/a)" in digest.full_digest
    assert "G/S Ratio: 80.00 (+1.25%)" in digest.full_digest
    assert "- 10:00 US CPI Release (HIGH)" in digest.full_digest
    assert "- Silver mean reversion (watching) SLV +3.20%" in digest.full_digest

    response = digest.as_response()
    assert response["digest_date"] == "2026-02-01"
    assert response["timezone"] == "UTC"
