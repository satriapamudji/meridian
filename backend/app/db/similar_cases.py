from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.analysis.historical import find_similar_cases as find_similar_matches
from app.db.embeddings import format_embedding


def load_embedding_vector(path: Path) -> list[float]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"{path}: embedding file must be a non-empty list")
    format_embedding(payload)
    return [float(value) for value in payload]


def find_similar_cases(embedding: list[float], limit: int = 5) -> list[dict[str, Any]]:
    matches = find_similar_matches(embedding, limit=limit)
    return [
        {
            "event_name": match.event_name,
            "date_range": match.date_range,
            "event_type": match.event_type,
            "significance_score": match.significance_score,
            "distance": match.distance,
        }
        for match in matches
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
