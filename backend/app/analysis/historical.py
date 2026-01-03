from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence

import psycopg

from app.analysis.significance import normalize_event_type
from app.core.settings import get_settings, normalize_database_url
from app.db.embeddings import format_embedding

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

TOKEN_RE = re.compile(r"[a-z0-9]+")
EVENT_TYPE_BOOST = 5


@dataclass(frozen=True)
class HistoricalCase:
    event_name: str
    date_range: str | None
    event_type: str | None
    significance_score: int | None
    structural_drivers: Sequence[str] | None = None
    lessons: Sequence[str] | None = None
    counter_examples: Sequence[str] | None = None
    traditional_market_reaction: Sequence[str] | None = None


@dataclass(frozen=True)
class HistoricalMatch:
    event_name: str
    date_range: str | None
    event_type: str | None
    significance_score: int | None
    match_method: str
    distance: float | None = None
    match_score: int | None = None


def find_historical_cases(
    *,
    event_text: str | None = None,
    event_type: str | None = None,
    embedding: list[float] | None = None,
    limit: int = 5,
) -> list[HistoricalMatch]:
    if embedding is not None:
        matches = find_similar_cases(embedding, limit=limit)
        if matches:
            return matches
    return fallback_matches(event_text=event_text, event_type=event_type, limit=limit)


def find_similar_cases(embedding: list[float], *, limit: int = 5) -> list[HistoricalMatch]:
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
        HistoricalMatch(
            event_name=row[0],
            date_range=row[1],
            event_type=row[2],
            significance_score=row[3],
            match_method="embedding",
            distance=float(row[4]),
        )
        for row in rows
    ]


def fallback_matches(
    *,
    event_text: str | None = None,
    event_type: str | None = None,
    limit: int = 5,
) -> list[HistoricalMatch]:
    cases = fetch_historical_cases()
    return rank_cases(cases, event_text=event_text, event_type=event_type, limit=limit)


def fetch_historical_cases() -> list[HistoricalCase]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT event_name,
               date_range,
               event_type,
               significance_score,
               structural_drivers,
               lessons,
               counter_examples,
               traditional_market_reaction
        FROM historical_cases
    """

    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query).fetchall()

    return [
        HistoricalCase(
            event_name=row[0],
            date_range=row[1],
            event_type=row[2],
            significance_score=row[3],
            structural_drivers=row[4],
            lessons=row[5],
            counter_examples=row[6],
            traditional_market_reaction=row[7],
        )
        for row in rows
    ]


def extract_keywords(text: str | None) -> set[str]:
    if not text:
        return set()
    tokens = TOKEN_RE.findall(text.lower())
    return {token for token in tokens if len(token) >= 3 and token not in STOPWORDS}


def rank_cases(
    cases: Iterable[HistoricalCase],
    *,
    event_text: str | None = None,
    event_type: str | None = None,
    limit: int = 5,
) -> list[HistoricalMatch]:
    case_list = list(cases)
    if not case_list:
        return []

    keywords = extract_keywords(event_text)
    normalized_event_type = normalize_event_type(event_type)

    scored: list[tuple[int, HistoricalCase]] = []
    for case in case_list:
        match_score = _score_case(case, keywords, normalized_event_type)
        scored.append((match_score, case))

    scored.sort(key=lambda item: _fallback_sort_key(item[0], item[1]))
    matches: list[HistoricalMatch] = []
    for match_score, case in scored[:limit]:
        matches.append(
            HistoricalMatch(
                event_name=case.event_name,
                date_range=case.date_range,
                event_type=case.event_type,
                significance_score=case.significance_score,
                match_method="fallback",
                match_score=match_score,
            )
        )
    return matches


def _score_case(
    case: HistoricalCase,
    keywords: set[str],
    normalized_event_type: str | None,
) -> int:
    match_score = _keyword_hits(_case_text(case), keywords)
    if normalized_event_type:
        case_type = normalize_event_type(case.event_type)
        if case_type == normalized_event_type:
            match_score += EVENT_TYPE_BOOST
    return match_score


def _case_text(case: HistoricalCase) -> str:
    parts: list[str] = []
    for value in (
        case.event_name,
        case.event_type,
        *_safe_list(case.structural_drivers),
        *_safe_list(case.lessons),
        *_safe_list(case.counter_examples),
        *_safe_list(case.traditional_market_reaction),
    ):
        if value:
            parts.append(value)
    return " ".join(parts).lower()


def _safe_list(values: Sequence[str] | None) -> list[str]:
    if not values:
        return []
    return [value for value in values if value]


def _keyword_hits(text: str, keywords: set[str]) -> int:
    if not keywords:
        return 0
    return sum(1 for keyword in keywords if keyword in text)


def _fallback_sort_key(match_score: int, case: HistoricalCase) -> tuple[int, int, str, str]:
    significance = case.significance_score or 0
    name = case.event_name.lower()
    date_range = case.date_range or ""
    return (-match_score, -significance, name, date_range)
