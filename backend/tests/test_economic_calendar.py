from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import json

from app.ingestion.economic_calendar import (
    build_fred_events,
    load_calendar_entries,
    parse_fred_release_dates,
    parse_fred_release_list,
    parse_forex_factory_payload,
    parse_numeric_value,
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
