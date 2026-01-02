from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Json

from app.core.settings import get_settings, normalize_database_url

ALLOWED_METALS = {"gold", "silver", "copper"}
ALLOWED_CATEGORIES = {"supply_chain", "use_cases", "patterns", "correlations", "actors"}


@dataclass(frozen=True)
class SeedEntry:
    metal: str
    category: str
    content: dict[str, Any] | list[Any]


def load_seed_entries(data_dir: Path) -> list[SeedEntry]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Seed directory not found: {data_dir}")

    entries: list[SeedEntry] = []
    for path in sorted(data_dir.glob("*.json")):
        entries.extend(_load_seed_file(path))
    return entries


def _load_seed_file(path: Path) -> list[SeedEntry]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    metal, categories = _validate_payload(payload, path)

    entries: list[SeedEntry] = []
    for category, content in categories.items():
        entries.append(SeedEntry(metal=metal, category=category, content=content))
    return entries


def _validate_payload(payload: dict[str, Any], path: Path) -> tuple[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: payload must be a JSON object")

    metal = payload.get("metal")
    if metal not in ALLOWED_METALS:
        raise ValueError(f"{path}: metal must be one of {sorted(ALLOWED_METALS)}")

    categories = payload.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise ValueError(f"{path}: categories must be a non-empty object")

    unknown = set(categories) - ALLOWED_CATEGORIES
    if unknown:
        raise ValueError(f"{path}: unknown categories: {sorted(unknown)}")

    missing = ALLOWED_CATEGORIES - set(categories)
    if missing:
        raise ValueError(f"{path}: missing categories: {sorted(missing)}")

    for category, content in categories.items():
        if not isinstance(content, (dict, list)):
            raise ValueError(f"{path}: category '{category}' must be an object or list")

    return metal, categories


def seed_metals(data_dir: Path) -> int:
    entries = load_seed_entries(data_dir)
    if not entries:
        return 0

    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        INSERT INTO metals_knowledge (id, metal, category, content, updated_at)
        VALUES (gen_random_uuid(), %(metal)s, %(category)s, %(content)s, now())
        ON CONFLICT (metal, category)
        DO UPDATE SET content = EXCLUDED.content, updated_at = now()
    """

    with psycopg.connect(database_url) as conn:
        for entry in entries:
            conn.execute(
                query,
                {
                    "metal": entry.metal,
                    "category": entry.category,
                    "content": Json(entry.content),
                },
            )

    return len(entries)


def _default_seed_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "metals"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed metals knowledge base")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=_default_seed_dir(),
        help="Path to metals seed files (default: data/metals)",
    )
    args = parser.parse_args()

    count = seed_metals(args.data_dir)
    print(f"Seeded {count} metal knowledge entries from {args.data_dir}")


if __name__ == "__main__":
    main()
