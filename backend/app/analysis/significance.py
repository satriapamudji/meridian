from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable, Sequence
import uuid

import psycopg
from psycopg.types.json import Json

from app.core.settings import get_settings, normalize_database_url

PRIORITY_THRESHOLD = 65
MONITORING_THRESHOLD = 50

STRUCTURAL_WEIGHT = 35
TRANSMISSION_WEIGHT = 30
HISTORICAL_WEIGHT = 20
ATTENTION_WEIGHT = 15

STRUCTURAL_BASE = {
    "financial_crisis": 90,
    "monetary_policy": 75,
    "geopolitical": 70,
    "economic_data": 55,
    "supply_shock": 80,
}

TRANSMISSION_BASE = {
    "financial_crisis": 80,
    "monetary_policy": 80,
    "geopolitical": 65,
    "economic_data": 55,
    "supply_shock": 75,
}

HISTORICAL_BASE = {
    "financial_crisis": 80,
    "monetary_policy": 65,
    "geopolitical": 60,
    "economic_data": 50,
    "supply_shock": 70,
}

SOURCE_ATTENTION_BASE = {
    "reuters": 60,
    "ap": 55,
    "google_news": 45,
}

EVENT_TYPE_ALIASES = {
    "monetary": "monetary_policy",
    "central_bank": "monetary_policy",
    "rate_decision": "monetary_policy",
    "geopolitics": "geopolitical",
    "sanctions": "geopolitical",
    "war": "geopolitical",
    "crisis": "financial_crisis",
    "banking_crisis": "financial_crisis",
    "data": "economic_data",
    "macro_data": "economic_data",
    "supply": "supply_shock",
    "energy": "supply_shock",
}

MAJOR_REGIONS = {"US", "EU", "CHINA", "UK", "JAPAN", "GLOBAL"}
REGION_ALIASES = {
    "UNITED STATES": "US",
    "UNITED STATES OF AMERICA": "US",
    "USA": "US",
    "U.S.": "US",
    "EUROPE": "EU",
    "EUROZONE": "EU",
    "UNITED KINGDOM": "UK",
    "UK": "UK",
    "CHINA": "CHINA",
    "JAPAN": "JAPAN",
    "GLOBAL": "GLOBAL",
    "WORLD": "GLOBAL",
}

MAJOR_ENTITIES = {
    "federal reserve",
    "fed",
    "european central bank",
    "ecb",
    "people's bank of china",
    "pboc",
    "bank of japan",
    "boj",
    "bank of england",
    "boe",
    "imf",
    "opec",
    "treasury",
}

MONETARY_TERMS = ("rate", "rates", "central bank", "fed", "ecb", "boj", "pboc", "hike")
CRISIS_TERMS = ("crisis", "default", "bank", "collapse", "liquidity", "bailout")
GEOPOLITICAL_TERMS = ("war", "sanction", "invasion", "conflict", "missile")
SUPPLY_TERMS = ("supply", "production", "strike", "shutdown", "export ban", "mine")
ECON_DATA_TERMS = ("cpi", "inflation", "gdp", "jobs", "payrolls", "unemployment", "pmi")

METAL_TERMS = ("gold", "silver", "copper", "metals", "bullion")
MACRO_TERMS = ("rate", "rates", "inflation", "cpi", "yield", "usd", "dollar")
HISTORICAL_TERMS = ("crisis", "default", "war", "recession", "sanction", "bank")
ATTENTION_TERMS = ("breaking", "urgent", "emergency", "surprise", "unexpected", "shock")


@dataclass(frozen=True)
class MacroEvent:
    source: str
    headline: str
    full_text: str | None = None
    event_type: str | None = None
    regions: Sequence[str] | None = None
    entities: Sequence[str] | None = None
    id: uuid.UUID | None = None


@dataclass(frozen=True)
class ScoreComponents:
    structural: int
    transmission: int
    historical: int
    attention: int

    def as_dict(self) -> dict[str, int]:
        return {
            "structural": self.structural,
            "transmission": self.transmission,
            "historical": self.historical,
            "attention": self.attention,
        }


@dataclass(frozen=True)
class ScoredEvent:
    total_score: int
    components: ScoreComponents
    priority_flag: bool
    tier: str


def normalize_event_type(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return EVENT_TYPE_ALIASES.get(normalized, normalized)


def classify_score(score: int) -> str:
    if score >= PRIORITY_THRESHOLD:
        return "priority"
    if score >= MONITORING_THRESHOLD:
        return "monitoring"
    return "logged"


def score_event(event: MacroEvent) -> ScoredEvent:
    text = _normalize_text(event.headline, event.full_text)
    event_type = normalize_event_type(event.event_type) or _infer_event_type(text)
    regions = _normalize_regions(event.regions)
    entities = _normalize_entities(event.entities)

    structural = _score_structural(event_type, regions, entities)
    transmission = _score_transmission(event_type, text, entities)
    historical = _score_historical(event_type, text, regions)
    attention = _score_attention(event.source, text, regions, entities)

    components = ScoreComponents(
        structural=structural,
        transmission=transmission,
        historical=historical,
        attention=attention,
    )
    total_score = _weighted_total(components)
    tier = classify_score(total_score)

    return ScoredEvent(
        total_score=total_score,
        components=components,
        priority_flag=total_score >= PRIORITY_THRESHOLD,
        tier=tier,
    )


def fetch_events_to_score(limit: int | None = None) -> list[MacroEvent]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT id,
               source,
               headline,
               full_text,
               event_type,
               regions,
               entities
        FROM macro_events
        WHERE significance_score IS NULL
        ORDER BY published_at NULLS LAST, created_at
    """
    params: dict[str, object] = {}
    if limit is not None:
        query += " LIMIT %(limit)s"
        params["limit"] = limit

    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        MacroEvent(
            id=row[0],
            source=row[1],
            headline=row[2],
            full_text=row[3],
            event_type=row[4],
            regions=row[5],
            entities=row[6],
        )
        for row in rows
    ]


def update_event_scores(events: Iterable[MacroEvent]) -> dict[str, int]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        UPDATE macro_events
        SET significance_score = %(significance_score)s,
            score_components = %(score_components)s,
            priority_flag = %(priority_flag)s
        WHERE id = %(id)s
    """
    summary = {"priority": 0, "monitoring": 0, "logged": 0}

    with psycopg.connect(database_url) as conn:
        for event in events:
            if event.id is None:
                raise ValueError("MacroEvent id is required for updates")
            scored = score_event(event)
            conn.execute(
                query,
                {
                    "significance_score": scored.total_score,
                    "score_components": Json(scored.components.as_dict()),
                    "priority_flag": scored.priority_flag,
                    "id": event.id,
                },
            )
            summary[scored.tier] += 1

    return summary


def _weighted_total(components: ScoreComponents) -> int:
    raw = (
        components.structural * STRUCTURAL_WEIGHT
        + components.transmission * TRANSMISSION_WEIGHT
        + components.historical * HISTORICAL_WEIGHT
        + components.attention * ATTENTION_WEIGHT
    )
    total = (raw + 50) // 100
    return _clamp(total)


def _score_structural(
    event_type: str | None,
    regions: set[str],
    entities: set[str],
) -> int:
    base = STRUCTURAL_BASE.get(event_type or "", 40)
    region_score = min(25, len(regions & MAJOR_REGIONS) * 8)
    entity_score = min(15, len(entities & MAJOR_ENTITIES) * 5)
    return _clamp(base + region_score + entity_score)


def _score_transmission(
    event_type: str | None,
    text: str,
    entities: set[str],
) -> int:
    base = TRANSMISSION_BASE.get(event_type or "", 35)
    boost = 0
    if _contains_any(text, METAL_TERMS):
        boost += 20
    if _contains_any(text, MACRO_TERMS):
        boost += 10
    if _contains_any(text, SUPPLY_TERMS):
        boost += 10
    if entities & MAJOR_ENTITIES:
        boost += 5
    return _clamp(base + boost)


def _score_historical(
    event_type: str | None,
    text: str,
    regions: set[str],
) -> int:
    base = HISTORICAL_BASE.get(event_type or "", 30)
    boost = 0
    if _contains_any(text, HISTORICAL_TERMS):
        boost += 10
    if regions & MAJOR_REGIONS:
        boost += min(10, len(regions & MAJOR_REGIONS) * 5)
    return _clamp(base + boost)


def _score_attention(
    source: str,
    text: str,
    regions: set[str],
    entities: set[str],
) -> int:
    base = SOURCE_ATTENTION_BASE.get(source.strip().lower(), 50)
    boost = 0
    if _contains_any(text, ATTENTION_TERMS):
        boost += 15
    if len(regions & MAJOR_REGIONS) >= 2:
        boost += 5
    if len(entities & MAJOR_ENTITIES) >= 2:
        boost += 5
    return _clamp(base + boost)


def _normalize_regions(regions: Sequence[str] | None) -> set[str]:
    normalized: set[str] = set()
    for region in regions or []:
        if not region:
            continue
        key = region.strip().upper()
        normalized.add(REGION_ALIASES.get(key, key))
    return normalized


def _normalize_entities(entities: Sequence[str] | None) -> set[str]:
    normalized: set[str] = set()
    for entity in entities or []:
        if not entity:
            continue
        normalized.add(entity.strip().lower())
    return normalized


def _infer_event_type(text: str) -> str | None:
    if _contains_any(text, CRISIS_TERMS):
        return "financial_crisis"
    if _contains_any(text, MONETARY_TERMS):
        return "monetary_policy"
    if _contains_any(text, GEOPOLITICAL_TERMS):
        return "geopolitical"
    if _contains_any(text, SUPPLY_TERMS):
        return "supply_shock"
    if _contains_any(text, ECON_DATA_TERMS):
        return "economic_data"
    return None


def _normalize_text(headline: str, full_text: str | None) -> str:
    parts = [headline]
    if full_text:
        parts.append(full_text)
    return " ".join(parts).lower()


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


def main() -> None:
    parser = argparse.ArgumentParser(description="Score macro event significance")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of events to score (default: all missing scores)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute scores without updating the database",
    )
    args = parser.parse_args()

    events = fetch_events_to_score(args.limit)
    if not events:
        print("No macro events found without significance scores.")
        return

    if args.dry_run:
        scored = [score_event(event) for event in events]
        summary = {"priority": 0, "monitoring": 0, "logged": 0}
        for result in scored:
            summary[result.tier] += 1
        print(
            "Dry run: "
            f"scored={len(scored)}, priority={summary['priority']}, "
            f"monitoring={summary['monitoring']}, logged={summary['logged']}"
        )
        return

    summary = update_event_scores(events)
    print(
        "Scored macro events: "
        f"priority={summary['priority']}, "
        f"monitoring={summary['monitoring']}, logged={summary['logged']}"
    )


if __name__ == "__main__":
    main()
