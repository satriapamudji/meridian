from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import json

from app.ingestion.economic_calendar import (
    build_fred_events,
    filter_events,
    FRED_RELEASE_MAPPINGS,
    load_calendar_entries,
    parse_forex_factory_payload,
    parse_fred_release_dates,
    parse_fred_release_list,
    parse_numeric_value,
    EconomicCalendarEvent,
)


def test_load_calendar_entries_from_repo_data() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data" / "calendar"
    entries = load_calendar_entries(data_dir)

    names = {entry.event_name for entry in entries}
    assert "US CPI (YoY)" in names
    assert "EU GDP (QoQ)" in names

    cpi = next(entry for entry in entries if entry.event_name == "US CPI (YoY)")
    assert cpi.surprise_direction == "negative"
    assert cpi.surprise_magnitude == Decimal("0.1")


def test_parse_numeric_value_handles_suffixes() -> None:
    assert parse_numeric_value("1.2K") == Decimal("1200")
    assert parse_numeric_value("3.5%") == Decimal("3.5")
    assert parse_numeric_value("N/A") is None


def test_parse_forex_factory_payload_fixture() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fixture_path = repo_root / "backend" / "tests" / "fixtures" / "forex_factory_calendar.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    events = parse_forex_factory_payload(payload)
    names = {event.event_name for event in events}

    assert "Nonfarm Payrolls" in names
    assert "German CPI m/m" in names

    payrolls = next(event for event in events if event.event_name == "Nonfarm Payrolls")
    assert payrolls.surprise_direction == "negative"
    assert payrolls.surprise_magnitude == Decimal("30000")


def test_parse_fred_payload_fixture() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    fixture_path = repo_root / "backend" / "tests" / "fixtures" / "fred_calendar.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    release_names = parse_fred_release_list(payload)
    release_dates = parse_fred_release_dates(payload)
    events = build_fred_events(release_dates, release_names)

    names = {event.event_name for event in events}
    assert "Consumer Price Index" in names
    assert "Employment Situation" in names


def test_fred_release_mappings_have_required_fields() -> None:
    """Verify FRED release mappings have proper structure."""
    assert len(FRED_RELEASE_MAPPINGS) > 0

    for release_id, (name, impact, region) in FRED_RELEASE_MAPPINGS.items():
        assert isinstance(release_id, int)
        assert isinstance(name, str) and len(name) > 0
        assert impact in ("high", "medium", "low")
        assert isinstance(region, str) and len(region) > 0


def test_fred_release_mappings_include_high_impact() -> None:
    """Verify key high-impact releases are configured."""
    # CPI
    assert 10 in FRED_RELEASE_MAPPINGS
    assert FRED_RELEASE_MAPPINGS[10][1] == "high"

    # NFP
    assert 50 in FRED_RELEASE_MAPPINGS
    assert FRED_RELEASE_MAPPINGS[50][1] == "high"

    # GDP
    assert 53 in FRED_RELEASE_MAPPINGS
    assert FRED_RELEASE_MAPPINGS[53][1] == "high"


def test_filter_events_excludes_past_events() -> None:
    """Verify filter_events can exclude events before start date."""
    now = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    past_event = EconomicCalendarEvent(
        event_name="Past Event",
        event_date=datetime(2026, 1, 10, 12, 0, 0, tzinfo=timezone.utc),
        region="USD",
        impact_level="high",
        expected_value=None,
        actual_value=None,
        previous_value=None,
        surprise_direction=None,
        surprise_magnitude=None,
    )
    future_event = EconomicCalendarEvent(
        event_name="Future Event",
        event_date=datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc),
        region="USD",
        impact_level="high",
        expected_value=None,
        actual_value=None,
        previous_value=None,
        surprise_direction=None,
        surprise_magnitude=None,
    )

    events = [past_event, future_event]
    end = datetime(2026, 1, 31, 23, 59, 59, tzinfo=timezone.utc)

    # Filter from now onwards - should only include future event
    filtered = filter_events(events, now, end)
    assert len(filtered) == 1
    assert filtered[0].event_name == "Future Event"


def test_filter_events_includes_events_in_range() -> None:
    """Verify filter_events includes events within the date range."""
    start = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end = datetime(2026, 1, 31, 23, 59, 59, tzinfo=timezone.utc)

    event_in_range = EconomicCalendarEvent(
        event_name="In Range",
        event_date=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        region="USD",
        impact_level="high",
        expected_value=None,
        actual_value=None,
        previous_value=None,
        surprise_direction=None,
        surprise_magnitude=None,
    )
    event_after_range = EconomicCalendarEvent(
        event_name="After Range",
        event_date=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
        region="USD",
        impact_level="high",
        expected_value=None,
        actual_value=None,
        previous_value=None,
        surprise_direction=None,
        surprise_magnitude=None,
    )

    events = [event_in_range, event_after_range]
    filtered = filter_events(events, start, end)

    assert len(filtered) == 1
    assert filtered[0].event_name == "In Range"
