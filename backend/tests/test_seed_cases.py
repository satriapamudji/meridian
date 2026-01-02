from __future__ import annotations

from pathlib import Path

from app.db.seed_cases import load_case_entries


def test_load_case_entries_from_repo_data() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data" / "cases"
    entries = load_case_entries(data_dir)

    names = {entry.event_name for entry in entries}
    assert "2008 Global Financial Crisis" in names
    assert "2020 COVID Shock" in names
    assert "2022 Russia-Ukraine War" in names
