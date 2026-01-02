from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import psycopg

from app.core.settings import get_settings, normalize_database_url
from app.db.embeddings import format_embedding


def load_embedding_vector(path: Path) -> list[float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"{path}: embedding file must be a non-empty list")
    format_embedding(payload)
    return [float(value) for value in payload]


def find_similar_cases(embedding: list[float], limit: int = 5) -> list[dict[str, Any]]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT event_name,
               date_range,
               event_type,
               significance_score,
               embedding <-> %(embedding)s::vector AS distance
        FROM historical_cases
        WHERE embedding IS NOT NULL
        ORDER BY embedding <-> %(embedding)s::vector
        LIMIT %(limit)s
    """
    params = {"embedding": format_embedding(embedding), "limit": limit}

    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        {
            "event_name": row[0],
            "date_range": row[1],
            "event_type": row[2],
            "significance_score": row[3],
            "distance": float(row[4]),
        }
        for row in rows
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Find similar historical cases")
    parser.add_argument(
        "--embedding-file",
        type=Path,
        required=True,
        help="JSON file containing an embedding vector",
    )
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    embedding = load_embedding_vector(args.embedding_file)
    matches = find_similar_cases(embedding, limit=args.limit)
    print(json.dumps(matches, indent=2))


if __name__ == "__main__":
    main()
