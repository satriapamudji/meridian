from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import psycopg

from app.core.settings import get_settings, normalize_database_url

EMBEDDING_DIM = 1536


@dataclass(frozen=True)
class EmbeddingUpdate:
    event_name: str
    date_range: str
    embedding: list[float]


def format_embedding(values: Iterable[float]) -> str:
    embedding = [float(value) for value in values]
    if len(embedding) != EMBEDDING_DIM:
        raise ValueError(
            f"embedding must have {EMBEDDING_DIM} dimensions, got {len(embedding)}"
        )
    return json.dumps(embedding)


def load_embedding_updates(path: Path) -> list[EmbeddingUpdate]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"{path}: embeddings file must be a non-empty list")

    updates: list[EmbeddingUpdate] = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: entry {idx} must be an object")

        event_name = item.get("event_name")
        date_range = item.get("date_range")
        embedding = item.get("embedding")
        if not isinstance(event_name, str) or not event_name.strip():
            raise ValueError(f"{path}: entry {idx} missing event_name")
        if not isinstance(date_range, str) or not date_range.strip():
            raise ValueError(f"{path}: entry {idx} missing date_range")
        if not isinstance(embedding, list):
            raise ValueError(f"{path}: entry {idx} embedding must be a list")

        format_embedding(embedding)
        updates.append(
            EmbeddingUpdate(
                event_name=event_name,
                date_range=date_range,
                embedding=embedding,
            )
        )

    return updates


def apply_embedding_updates(path: Path) -> int:
    updates = load_embedding_updates(path)
    if not updates:
        return 0

    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        UPDATE historical_cases
        SET embedding = %(embedding)s
        WHERE event_name = %(event_name)s AND date_range = %(date_range)s
    """

    updated = 0
    with psycopg.connect(database_url) as conn:
        for entry in updates:
            result = conn.execute(
                query,
                {
                    "event_name": entry.event_name,
                    "date_range": entry.date_range,
                    "embedding": format_embedding(entry.embedding),
                },
            )
            updated += result.rowcount or 0

    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply historical case embeddings")
    parser.add_argument(
        "--embeddings-file",
        type=Path,
        required=True,
        help="JSON file with embeddings (list of {event_name,date_range,embedding})",
    )
    args = parser.parse_args()

    count = apply_embedding_updates(args.embeddings_file)
    print(f"Updated embeddings for {count} historical cases")


if __name__ == "__main__":
    main()
