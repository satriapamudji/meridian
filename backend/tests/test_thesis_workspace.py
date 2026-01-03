from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.api.theses import _ensure_thesis_requirements, _normalize_status
from app.services.thesis_export import render_thesis_markdown


def test_render_thesis_markdown_includes_updates() -> None:
    thesis = {
        "title": "Gold Thesis",
        "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc),
        "status": "watching",
        "asset_type": "Gold",
        "asset_symbol": "GC=F",
        "core_thesis": "Macro regime shift favors gold.",
        "trigger_event": "Fed pauses hikes.",
        "historical_precedent": "2008 Global Financial Crisis",
        "bull_case": ["Rates fall", "USD weakens"],
        "bear_case": ["Risk-on rotation"],
        "entry_consideration": "Buy on dips",
        "target": "2200",
        "invalidation": "Sustained real rate rise",
        "vehicle": "GLD",
        "position_size": "starter",
        "entry_date": datetime(2026, 2, 2, tzinfo=timezone.utc),
        "entry_price": 2050,
        "updates": [
            {
                "date": "2026-02-03",
                "note": "Initial position started.",
                "price": 2060,
            }
        ],
    }

    markdown = render_thesis_markdown(thesis)

    assert "# Thesis: Gold Thesis" in markdown
    assert "## Core Thesis" in markdown
    assert "| 2026-02-03 | Initial position started. | 2060 |" in markdown


def test_active_thesis_requires_bear_case_and_invalidation() -> None:
    with pytest.raises(HTTPException):
        _ensure_thesis_requirements("active", None, "missing bear case")
    with pytest.raises(HTTPException):
        _ensure_thesis_requirements("active", ["risk"], None)


def test_normalize_status_accepts_known_values() -> None:
    assert _normalize_status("ACTIVE") == "active"
