from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Json

from app.core.settings import get_settings, normalize_database_url
from app.db.embeddings import format_embedding

REQUIRED_FIELDS = {
    "event_name",
    "date_range",
    "event_type",
    "significance_score",
    "structural_drivers",
    "metal_impacts",
    "traditional_market_reaction",
    "crypto_reaction",
    "crypto_transmission",
    "time_delays",
    "lessons",
    "counter_examples",
}

METAL_KEYS = {"gold", "silver", "copper"}


@dataclass(frozen=True)
class HistoricalCaseEntry:
    event_name: str
    date_range: str
    event_type: str
    significance_score: int
    structural_drivers: list[str]
    metal_impacts: dict[str, Any]
    traditional_market_reaction: list[str]
    crypto_reaction: list[str]
    crypto_transmission: dict[str, Any]
    time_delays: list[str]
    lessons: list[str]
    counter_examples: list[str]
    embedding: list[float] | None
    # New optional fields for quantitative analysis
    quantitative_impacts: dict[str, Any] | None = None
    time_horizon_behavior: dict[str, Any] | None = None
    transmission_channels: list[str] | None = None


def load_case_entries(data_dir: Path) -> list[HistoricalCaseEntry]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Seed directory not found: {data_dir}")

    entries: list[HistoricalCaseEntry] = []
    for path in sorted(data_dir.glob("*.json")):
        entries.append(_load_case_file(path))
    return entries


def _load_case_file(path: Path) -> HistoricalCaseEntry:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _validate_payload(payload, path)


def _validate_payload(payload: dict[str, Any], path: Path) -> HistoricalCaseEntry:
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: payload must be a JSON object")

    missing = REQUIRED_FIELDS - set(payload)
    if missing:
        raise ValueError(f"{path}: missing required fields: {sorted(missing)}")

    event_name = _require_str(payload, "event_name", path)
    date_range = _require_str(payload, "date_range", path)
    event_type = _require_str(payload, "event_type", path)
    significance_score = _require_int(payload, "significance_score", path)

    structural_drivers = _require_str_list(payload, "structural_drivers", path)
    metal_impacts = _require_dict(payload, "metal_impacts", path)
    traditional_market_reaction = _require_str_list(payload, "traditional_market_reaction", path)
    crypto_reaction = _require_str_list(payload, "crypto_reaction", path, allow_empty=True)
    crypto_transmission = _require_dict(payload, "crypto_transmission", path)
    time_delays = _require_str_list(payload, "time_delays", path)
    lessons = _require_str_list(payload, "lessons", path)
    counter_examples = _require_str_list(payload, "counter_examples", path, allow_empty=True)

    _validate_metal_impacts(metal_impacts, path)
    _validate_crypto_transmission(crypto_transmission, path)

    embedding = payload.get("embedding")
    if embedding is not None:
        if not isinstance(embedding, list):
            raise ValueError(f"{path}: embedding must be a list of floats")
        format_embedding(embedding)

    # Parse optional quantitative fields
    quantitative_impacts = payload.get("quantitative_impacts")
    if quantitative_impacts is not None and not isinstance(quantitative_impacts, dict):
        raise ValueError(f"{path}: quantitative_impacts must be an object when provided")

    time_horizon_behavior = payload.get("time_horizon_behavior")
    if time_horizon_behavior is not None and not isinstance(time_horizon_behavior, dict):
        raise ValueError(f"{path}: time_horizon_behavior must be an object when provided")

    transmission_channels = payload.get("transmission_channels")
    if transmission_channels is not None:
        if not isinstance(transmission_channels, list) or not all(
            isinstance(x, str) for x in transmission_channels
        ):
            raise ValueError(f"{path}: transmission_channels must be a list of strings")

    return HistoricalCaseEntry(
        event_name=event_name,
        date_range=date_range,
        event_type=event_type,
        significance_score=significance_score,
        structural_drivers=structural_drivers,
        metal_impacts=metal_impacts,
        traditional_market_reaction=traditional_market_reaction,
        crypto_reaction=crypto_reaction,
        crypto_transmission=crypto_transmission,
        time_delays=time_delays,
        lessons=lessons,
        counter_examples=counter_examples,
        embedding=embedding,
        quantitative_impacts=quantitative_impacts,
        time_horizon_behavior=time_horizon_behavior,
        transmission_channels=transmission_channels,
    )


def _require_str(payload: dict[str, Any], field: str, path: Path) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: field '{field}' must be a non-empty string")
    return value


def _require_int(payload: dict[str, Any], field: str, path: Path) -> int:
    value = payload.get(field)
    if not isinstance(value, int):
        raise ValueError(f"{path}: field '{field}' must be an integer")
    return value


def _require_str_list(
    payload: dict[str, Any],
    field: str,
    path: Path,
    *,
    allow_empty: bool = False,
) -> list[str]:
    value = payload.get(field)
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{path}: field '{field}' must be a list of strings")
    if not value and not allow_empty:
        raise ValueError(f"{path}: field '{field}' must be a non-empty list")
    return value


def _require_dict(payload: dict[str, Any], field: str, path: Path) -> dict[str, Any]:
    value = payload.get(field)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{path}: field '{field}' must be a non-empty object")
    return value


def _validate_metal_impacts(metal_impacts: dict[str, Any], path: Path) -> None:
    missing = METAL_KEYS - set(metal_impacts)
    if missing:
        raise ValueError(f"{path}: metal_impacts missing keys {sorted(missing)}")

    for metal in METAL_KEYS:
        entry = metal_impacts.get(metal)
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: metal_impacts.{metal} must be an object")
        for key in ("direction", "magnitude", "driver"):
            value = entry.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{path}: metal_impacts.{metal}.{key} must be a non-empty string")


def _validate_crypto_transmission(crypto_transmission: dict[str, Any], path: Path) -> None:
    exists = crypto_transmission.get("exists")
    if not isinstance(exists, bool):
        raise ValueError(f"{path}: crypto_transmission.exists must be boolean")
    for key in ("path", "strength"):
        value = crypto_transmission.get(key)
        if not isinstance(value, str):
            raise ValueError(f"{path}: crypto_transmission.{key} must be a string")


def seed_cases(data_dir: Path) -> int:
    entries = load_case_entries(data_dir)
    if not entries:
        return 0

    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        INSERT INTO historical_cases (
            id,
            event_name,
            date_range,
            event_type,
            significance_score,
            structural_drivers,
            metal_impacts,
            traditional_market_reaction,
            crypto_reaction,
            crypto_transmission,
            time_delays,
            lessons,
            counter_examples,
            embedding,
            quantitative_impacts,
            time_horizon_behavior,
            transmission_channels
        )
        VALUES (
            gen_random_uuid(),
            %(event_name)s,
            %(date_range)s,
            %(event_type)s,
            %(significance_score)s,
            %(structural_drivers)s,
            %(metal_impacts)s,
            %(traditional_market_reaction)s,
            %(crypto_reaction)s,
            %(crypto_transmission)s,
            %(time_delays)s,
            %(lessons)s,
            %(counter_examples)s,
            %(embedding)s,
            %(quantitative_impacts)s,
            %(time_horizon_behavior)s,
            %(transmission_channels)s
        )
        ON CONFLICT (event_name, date_range)
        DO UPDATE SET
            event_type = EXCLUDED.event_type,
            significance_score = EXCLUDED.significance_score,
            structural_drivers = EXCLUDED.structural_drivers,
            metal_impacts = EXCLUDED.metal_impacts,
            traditional_market_reaction = EXCLUDED.traditional_market_reaction,
            crypto_reaction = EXCLUDED.crypto_reaction,
            crypto_transmission = EXCLUDED.crypto_transmission,
            time_delays = EXCLUDED.time_delays,
            lessons = EXCLUDED.lessons,
            counter_examples = EXCLUDED.counter_examples,
            embedding = COALESCE(EXCLUDED.embedding, historical_cases.embedding),
            quantitative_impacts = COALESCE(EXCLUDED.quantitative_impacts, historical_cases.quantitative_impacts),
            time_horizon_behavior = COALESCE(EXCLUDED.time_horizon_behavior, historical_cases.time_horizon_behavior),
            transmission_channels = COALESCE(EXCLUDED.transmission_channels, historical_cases.transmission_channels)
    """

    with psycopg.connect(database_url) as conn:
        for entry in entries:
            embedding_value = None
            if entry.embedding is not None:
                embedding_value = format_embedding(entry.embedding)

            quantitative_impacts_value = None
            if entry.quantitative_impacts is not None:
                quantitative_impacts_value = Json(entry.quantitative_impacts)

            time_horizon_behavior_value = None
            if entry.time_horizon_behavior is not None:
                time_horizon_behavior_value = Json(entry.time_horizon_behavior)

            conn.execute(
                query,
                {
                    "event_name": entry.event_name,
                    "date_range": entry.date_range,
                    "event_type": entry.event_type,
                    "significance_score": entry.significance_score,
                    "structural_drivers": entry.structural_drivers,
                    "metal_impacts": Json(entry.metal_impacts),
                    "traditional_market_reaction": entry.traditional_market_reaction,
                    "crypto_reaction": entry.crypto_reaction,
                    "crypto_transmission": Json(entry.crypto_transmission),
                    "time_delays": entry.time_delays,
                    "lessons": entry.lessons,
                    "counter_examples": entry.counter_examples,
                    "embedding": embedding_value,
                    "quantitative_impacts": quantitative_impacts_value,
                    "time_horizon_behavior": time_horizon_behavior_value,
                    "transmission_channels": entry.transmission_channels,
                },
            )

    return len(entries)


def _default_seed_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "cases"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed historical cases")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=_default_seed_dir(),
        help="Path to historical case files (default: data/cases)",
    )
    args = parser.parse_args()

    count = seed_cases(args.data_dir)
    print(f"Seeded {count} historical cases from {args.data_dir}")


if __name__ == "__main__":
    main()
