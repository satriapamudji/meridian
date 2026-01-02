from __future__ import annotations

from pathlib import Path

from app.db.seed_metals import ALLOWED_CATEGORIES, ALLOWED_METALS, load_seed_entries


def test_load_seed_entries_from_repo_data() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data" / "metals"
    entries = load_seed_entries(data_dir)

    assert entries

    keys = {(entry.metal, entry.category) for entry in entries}
    for metal in ALLOWED_METALS:
        for category in ALLOWED_CATEGORIES:
            assert (metal, category) in keys
