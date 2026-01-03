from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any, Iterable, Protocol
import uuid

import psycopg
from psycopg.types.json import Json

from app.analysis.transmission import evaluate_transmission, normalize_crypto_transmission
from app.core.settings import get_settings, normalize_database_url

METAL_KEYS = ("gold", "silver", "copper")

_PROMPT_TEMPLATE = """You are a macro analyst. Produce JSON only.

Return a JSON object with these keys:
- raw_facts: list of short, literal facts drawn only from EVENT_JSON. No interpretation.
- metal_impacts: object keyed by gold/silver/copper with direction, magnitude, driver.
- historical_precedent: reference case ids from HISTORICAL_CASES_JSON.
- counter_case: plausible counter-case to the main interpretation.
- crypto_transmission: object with exists (bool), path (string),
  strength (strong/moderate/weak/none), relevant_assets (list).
- thesis_seed: short thesis seed (optional).

If data is missing, say "insufficient data". Do not include extra keys.
Avoid signal-bot tone; keep language thesis-supportive.

EVENT_JSON:
{event_json}

METALS_KB_JSON:
{metals_json}

HISTORICAL_CASES_JSON:
{cases_json}
"""


@dataclass(frozen=True)
class MacroEventRecord:
    id: uuid.UUID
    source: str
    headline: str
    full_text: str | None
    published_at: datetime | None
    event_type: str | None
    regions: list[str] | None
    entities: list[str] | None
    significance_score: int | None


@dataclass(frozen=True)
class MetalsKnowledgeEntry:
    metal: str
    category: str
    content: dict[str, Any] | list[Any]


@dataclass(frozen=True)
class HistoricalCaseSummary:
    id: uuid.UUID
    event_name: str
    date_range: str
    event_type: str | None
    significance_score: int | None
    metal_impacts: dict[str, Any] | None
    crypto_transmission: dict[str, Any] | None
    lessons: list[str] | None
    counter_examples: list[str] | None


@dataclass(frozen=True)
class AnalysisRequest:
    event: MacroEventRecord
    metals_knowledge: list[MetalsKnowledgeEntry]
    historical_cases: list[HistoricalCaseSummary]


@dataclass(frozen=True)
class MacroEventAnalysis:
    raw_facts: list[str]
    metal_impacts: dict[str, Any]
    historical_precedent: str
    counter_case: str
    crypto_transmission: dict[str, Any]
    thesis_seed: str | None


class LlmProvider(Protocol):
    def complete(self, prompt: str) -> str:
        ...


class LocalHeuristicProvider:
    def complete(self, prompt: str) -> str:
        event_payload = _extract_json_block(prompt, "EVENT_JSON") or {}
        cases_payload = _extract_json_block(prompt, "HISTORICAL_CASES_JSON") or []

        headline = str(event_payload.get("headline") or "").strip()
        full_text = str(event_payload.get("full_text") or "").strip()
        raw_facts = []
        if headline:
            raw_facts.append(headline)
        if full_text:
            raw_facts.append(full_text.split(".")[0].strip() + ".")
        if not raw_facts:
            raw_facts.append("insufficient data")

        precedent = "insufficient data"
        if cases_payload:
            case = cases_payload[0]
            case_id = case.get("id", "unknown")
            event_name = case.get("event_name", "historical case")
            date_range = case.get("date_range", "unknown period")
            precedent = f"case_id {case_id}: {event_name} ({date_range})"

        event_type = event_payload.get("event_type")
        event_text = " ".join([headline, full_text]).strip()
        payload = {
            "raw_facts": raw_facts,
            "metal_impacts": {
                "gold": {
                    "direction": "unknown",
                    "magnitude": "unknown",
                    "driver": "insufficient data",
                },
                "silver": {
                    "direction": "unknown",
                    "magnitude": "unknown",
                    "driver": "insufficient data",
                },
                "copper": {
                    "direction": "unknown",
                    "magnitude": "unknown",
                    "driver": "insufficient data",
                },
            },
            "historical_precedent": precedent,
            "counter_case": "insufficient data",
            "crypto_transmission": evaluate_transmission(event_text, event_type),
            "thesis_seed": "insufficient data",
        }
        return json.dumps(payload)


class OpenRouterProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        base_url: str,
        app_url: str | None = None,
        app_title: str | None = None,
        timeout: int = 30,
    ) -> None:
        if not api_key:
            raise ValueError("MERIDIAN_OPENROUTER_API_KEY is required")
        if not model:
            raise ValueError("OpenRouter model is required")
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._app_url = app_url or ""
        self._app_title = app_title or ""
        self._timeout = timeout

    def complete(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self._app_url:
            headers["HTTP-Referer"] = self._app_url
        if self._app_title:
            headers["X-Title"] = self._app_title
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 900,
        }
        response = _post_json(self._base_url, payload, headers, timeout=self._timeout)
        return _extract_openrouter_content(response)


def build_prompt(request: AnalysisRequest) -> str:
    event_payload = {
        "id": str(request.event.id),
        "source": request.event.source,
        "headline": request.event.headline,
        "full_text": request.event.full_text,
        "published_at": request.event.published_at.isoformat()
        if request.event.published_at
        else None,
        "event_type": request.event.event_type,
        "regions": request.event.regions,
        "entities": request.event.entities,
        "significance_score": request.event.significance_score,
    }
    metals_payload = _format_metals_knowledge(request.metals_knowledge)
    cases_payload = [
        {
            "id": str(case.id),
            "event_name": case.event_name,
            "date_range": case.date_range,
            "event_type": case.event_type,
            "significance_score": case.significance_score,
            "metal_impacts": case.metal_impacts,
            "crypto_transmission": case.crypto_transmission,
            "lessons": case.lessons,
            "counter_examples": case.counter_examples,
        }
        for case in request.historical_cases
    ]
    return _PROMPT_TEMPLATE.format(
        event_json=json.dumps(event_payload, indent=2, sort_keys=True),
        metals_json=json.dumps(metals_payload, indent=2, sort_keys=True),
        cases_json=json.dumps(cases_payload, indent=2, sort_keys=True),
    )


def parse_analysis_response(response: str) -> MacroEventAnalysis:
    payload = _parse_json_payload(response)
    raw_facts = _normalize_raw_facts(_require_list(payload, "raw_facts"))
    metal_impacts = _normalize_metal_impacts(_require_dict(payload, "metal_impacts"))
    historical_precedent = _string_or_default(
        payload.get("historical_precedent"), "insufficient data"
    )
    counter_case = _string_or_default(payload.get("counter_case"), "insufficient data")
    crypto_transmission = normalize_crypto_transmission(
        _require_dict(payload, "crypto_transmission")
    )
    thesis_seed = payload.get("thesis_seed")
    if thesis_seed is not None and not isinstance(thesis_seed, str):
        raise ValueError("thesis_seed must be a string when provided")

    return MacroEventAnalysis(
        raw_facts=raw_facts,
        metal_impacts=metal_impacts,
        historical_precedent=historical_precedent,
        counter_case=counter_case,
        crypto_transmission=crypto_transmission,
        thesis_seed=thesis_seed,
    )


def analyze_event(
    provider: LlmProvider, request: AnalysisRequest, *, return_prompt: bool = False
) -> tuple[MacroEventAnalysis, str | None]:
    prompt = build_prompt(request)
    response = provider.complete(prompt)
    analysis = parse_analysis_response(response)
    return analysis, prompt if return_prompt else None


def fetch_priority_events(
    limit: int | None = None,
    *,
    include_analyzed: bool = False,
) -> list[MacroEventRecord]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT id,
               source,
               headline,
               full_text,
               published_at,
               event_type,
               regions,
               entities,
               significance_score
        FROM macro_events
        WHERE priority_flag = true
    """
    if not include_analyzed:
        query += """
          AND raw_facts IS NULL
          AND metal_impacts IS NULL
          AND historical_precedent IS NULL
          AND counter_case IS NULL
          AND crypto_transmission IS NULL
        """
    query += " ORDER BY published_at DESC NULLS LAST, created_at DESC"
    params: dict[str, object] = {}
    if limit is not None:
        query += " LIMIT %(limit)s"
        params["limit"] = limit

    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        MacroEventRecord(
            id=row[0],
            source=row[1],
            headline=row[2],
            full_text=row[3],
            published_at=row[4],
            event_type=row[5],
            regions=row[6],
            entities=row[7],
            significance_score=row[8],
        )
        for row in rows
    ]


def fetch_event_by_id(event_id: uuid.UUID) -> MacroEventRecord | None:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT id,
               source,
               headline,
               full_text,
               published_at,
               event_type,
               regions,
               entities,
               significance_score
        FROM macro_events
        WHERE id = %(id)s
    """
    with psycopg.connect(database_url) as conn:
        row = conn.execute(query, {"id": event_id}).fetchone()
    if row is None:
        return None
    return MacroEventRecord(
        id=row[0],
        source=row[1],
        headline=row[2],
        full_text=row[3],
        published_at=row[4],
        event_type=row[5],
        regions=row[6],
        entities=row[7],
        significance_score=row[8],
    )


def fetch_metals_knowledge() -> list[MetalsKnowledgeEntry]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT metal, category, content
        FROM metals_knowledge
        ORDER BY metal, category
    """
    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query).fetchall()
    return [
        MetalsKnowledgeEntry(metal=row[0], category=row[1], content=row[2]) for row in rows
    ]


def fetch_historical_cases(
    event_type: str | None,
    *,
    limit: int = 5,
) -> list[HistoricalCaseSummary]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT id,
               event_name,
               date_range,
               event_type,
               significance_score,
               metal_impacts,
               crypto_transmission,
               lessons,
               counter_examples
        FROM historical_cases
    """
    params: dict[str, object] = {"limit": limit}
    if event_type:
        query += " WHERE event_type = %(event_type)s"
        params["event_type"] = event_type
    query += " ORDER BY significance_score DESC NULLS LAST LIMIT %(limit)s"
    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        HistoricalCaseSummary(
            id=row[0],
            event_name=row[1],
            date_range=row[2],
            event_type=row[3],
            significance_score=row[4],
            metal_impacts=row[5],
            crypto_transmission=row[6],
            lessons=row[7],
            counter_examples=row[8],
        )
        for row in rows
    ]


def update_event_analysis(
    event_id: uuid.UUID,
    analysis: MacroEventAnalysis,
    *,
    overwrite: bool = False,
) -> bool:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        UPDATE macro_events
        SET raw_facts = %(raw_facts)s,
            metal_impacts = %(metal_impacts)s,
            historical_precedent = %(historical_precedent)s,
            counter_case = %(counter_case)s,
            crypto_transmission = %(crypto_transmission)s
        WHERE id = %(id)s
    """
    if not overwrite:
        query += """
          AND raw_facts IS NULL
          AND metal_impacts IS NULL
          AND historical_precedent IS NULL
          AND counter_case IS NULL
          AND crypto_transmission IS NULL
        """
    params = {
        "id": event_id,
        "raw_facts": analysis.raw_facts,
        "metal_impacts": Json(analysis.metal_impacts),
        "historical_precedent": analysis.historical_precedent,
        "counter_case": analysis.counter_case,
        "crypto_transmission": Json(analysis.crypto_transmission),
    }
    with psycopg.connect(database_url) as conn:
        result = conn.execute(query, params)
    return (result.rowcount or 0) > 0


def _format_metals_knowledge(entries: Iterable[MetalsKnowledgeEntry]) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = {}
    for entry in entries:
        grouped.setdefault(entry.metal, {})[entry.category] = entry.content
    return grouped


def _parse_json_payload(response: str) -> dict[str, Any]:
    text = response.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def _normalize_raw_facts(items: list[Any]) -> list[str]:
    facts: list[str] = []
    for item in items:
        if not isinstance(item, str):
            raise ValueError("raw_facts must be a list of strings")
        normalized = " ".join(item.split())
        if normalized:
            facts.append(normalized)
    if not facts:
        raise ValueError("raw_facts must contain at least one fact")
    return facts


def _normalize_metal_impacts(payload: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for metal in METAL_KEYS:
        entry = payload.get(metal)
        if not isinstance(entry, dict):
            entry = {}
        normalized[metal] = {
            "direction": _string_or_default(entry.get("direction"), "unknown"),
            "magnitude": _string_or_default(entry.get("magnitude"), "unknown"),
            "driver": _string_or_default(entry.get("driver"), "insufficient data"),
        }
    return normalized


def _string_or_default(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _require_dict(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _extract_json_block(prompt: str, label: str) -> Any | None:
    marker = f"{label}:"
    if marker not in prompt:
        return None
    start = prompt.index(marker) + len(marker)
    next_markers = [
        "\nEVENT_JSON:",
        "\nMETALS_KB_JSON:",
        "\nHISTORICAL_CASES_JSON:",
    ]
    end = len(prompt)
    for next_marker in next_markers:
        idx = prompt.find(next_marker, start)
        if idx != -1:
            end = min(end, idx)
    block = prompt[start:end].strip()
    if not block:
        return None
    return json.loads(block)


def _post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: int,
) -> dict[str, Any]:
    import urllib.error
    import urllib.request

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"OpenRouter request failed: {exc.code} {exc.reason}. {body}"
        ) from exc
    if not body:
        raise RuntimeError("OpenRouter response was empty")
    return json.loads(body)


def _extract_openrouter_content(payload: dict[str, Any]) -> str:
    error = payload.get("error")
    if isinstance(error, dict):
        message = error.get("message", "OpenRouter error")
        raise RuntimeError(str(message))
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("OpenRouter response missing choices")
    first = choices[0]
    if isinstance(first, dict):
        message = first.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content
        content = first.get("text")
        if isinstance(content, str) and content.strip():
            return content
    raise RuntimeError("OpenRouter response missing content")


def run_analysis(
    provider: LlmProvider,
    events: Iterable[MacroEventRecord],
    *,
    overwrite: bool = False,
    dry_run: bool = False,
    print_prompts: bool = False,
) -> dict[str, int]:
    metals_knowledge = fetch_metals_knowledge()
    summary = {"analyzed": 0, "skipped": 0}

    for event in events:
        cases = fetch_historical_cases(event.event_type)
        analysis, prompt = analyze_event(
            provider,
            AnalysisRequest(event, metals_knowledge, cases),
            return_prompt=print_prompts,
        )
        if print_prompts and prompt:
            print(prompt)

        if dry_run:
            summary["analyzed"] += 1
            continue

        updated = update_event_analysis(event.id, analysis, overwrite=overwrite)
        if updated:
            summary["analyzed"] += 1
        else:
            summary["skipped"] += 1

    return summary


def resolve_provider(name: str, model_override: str | None) -> LlmProvider:
    if name == "openrouter":
        settings = get_settings()
        model = model_override or settings.openrouter_model
        return OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=model,
            base_url=settings.openrouter_base_url,
            app_url=settings.openrouter_app_url or None,
            app_title=settings.openrouter_app_title or None,
        )
    return LocalHeuristicProvider()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze priority macro events")
    parser.add_argument("--event-id", type=uuid.UUID, help="Analyze a single event by id")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--provider",
        choices=("local", "openrouter"),
        default="local",
        help="LLM provider to use for analysis",
    )
    parser.add_argument("--model", help="Override model name (OpenRouter only)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing analysis")
    parser.add_argument("--dry-run", action="store_true", help="Run without DB updates")
    parser.add_argument(
        "--print-prompts",
        action="store_true",
        help="Print rendered prompts for debugging",
    )
    args = parser.parse_args()

    try:
        provider = resolve_provider(args.provider, args.model)
    except ValueError as exc:
        print(f"Provider error: {exc}")
        return

    if args.event_id:
        event = fetch_event_by_id(args.event_id)
        if event is None:
            print(f"No macro event found for id {args.event_id}")
            return
        events = [event]
    else:
        events = fetch_priority_events(
            limit=args.limit, include_analyzed=args.overwrite
        )
        if not events:
            print("No priority macro events found for analysis.")
            return

    summary = run_analysis(
        provider,
        events,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        print_prompts=args.print_prompts,
    )
    print(f"Analyzed {summary['analyzed']} events (skipped {summary['skipped']}).")


if __name__ == "__main__":
    main()
