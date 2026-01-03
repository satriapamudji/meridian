from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Sequence
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
import psycopg

from app.analysis.macro_event_analysis import (
    AnalysisRequest,
    MacroEventAnalysis,
    MacroEventRecord,
    analyze_event,
    fetch_historical_cases,
    fetch_metals_knowledge,
    resolve_provider,
)
from app.core.settings import get_settings, normalize_database_url

router = APIRouter(prefix="/events", tags=["events"])


@dataclass(frozen=True)
class MacroEventRow:
    id: uuid.UUID
    source: str
    headline: str
    full_text: str | None
    published_at: datetime | None
    event_type: str | None
    regions: list[str] | None
    entities: list[str] | None
    significance_score: int | None
    priority_flag: bool
    status: str | None
    raw_facts: list[str] | None
    metal_impacts: dict[str, Any] | None
    historical_precedent: str | None
    counter_case: str | None
    crypto_transmission: dict[str, Any] | None


class AnalyzeRequest(BaseModel):
    overwrite: bool = False
    provider: str = Field(default="local", pattern="^(local|openrouter)$")
    model: str | None = None


class AnalyzeResponse(BaseModel):
    event_id: uuid.UUID
    status: str
    analysis: dict[str, Any]


class EventRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self._database_url = normalize_database_url(settings.database_url)

    def list_events(
        self,
        *,
        priority_only: bool,
        score_min: int | None,
        score_max: int | None,
        status: str | None,
        start_date: date | None,
        end_date: date | None,
        limit: int,
    ) -> list[MacroEventRow]:
        query = """
            SELECT id,
                   source,
                   headline,
                   full_text,
                   published_at,
                   event_type,
                   regions,
                   entities,
                   significance_score,
                   priority_flag,
                   status,
                   raw_facts,
                   metal_impacts,
                   historical_precedent,
                   counter_case,
                   crypto_transmission
            FROM macro_events
            WHERE 1=1
        """
        params: dict[str, object] = {"limit": limit}
        if priority_only:
            query += " AND priority_flag = true"
        if status:
            query += " AND status = %(status)s"
            params["status"] = status
        if score_min is not None:
            query += " AND significance_score >= %(score_min)s"
            params["score_min"] = score_min
        if score_max is not None:
            query += " AND significance_score <= %(score_max)s"
            params["score_max"] = score_max
        if start_date:
            query += " AND published_at >= %(start_ts)s"
            params["start_ts"] = _start_of_day(start_date)
        if end_date:
            query += " AND published_at < %(end_ts)s"
            params["end_ts"] = _end_of_day(end_date)

        query += " ORDER BY published_at DESC NULLS LAST, created_at DESC LIMIT %(limit)s"

        with psycopg.connect(self._database_url) as conn:
            rows = conn.execute(query, params).fetchall()

        return [_row_to_event(row) for row in rows]

    def get_event(self, event_id: uuid.UUID) -> MacroEventRow | None:
        query = """
            SELECT id,
                   source,
                   headline,
                   full_text,
                   published_at,
                   event_type,
                   regions,
                   entities,
                   significance_score,
                   priority_flag,
                   status,
                   raw_facts,
                   metal_impacts,
                   historical_precedent,
                   counter_case,
                   crypto_transmission
            FROM macro_events
            WHERE id = %(id)s
        """
        with psycopg.connect(self._database_url) as conn:
            row = conn.execute(query, {"id": event_id}).fetchone()
        return _row_to_event(row) if row else None

    def update_analysis(
        self, event_id: uuid.UUID, analysis: MacroEventAnalysis, *, overwrite: bool
    ) -> bool:
        from app.analysis.macro_event_analysis import update_event_analysis

        return update_event_analysis(event_id, analysis, overwrite=overwrite)

    def fetch_metals(self) -> list:
        return fetch_metals_knowledge()

    def fetch_cases(self, event_type: str | None) -> list:
        return fetch_historical_cases(event_type)


def get_event_repository() -> EventRepository:
    return EventRepository()


@router.get("")
def list_events(
    priority_only: bool = False,
    score_min: int | None = Query(default=None, ge=0, le=100),
    score_max: int | None = Query(default=None, ge=0, le=100),
    status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=200, ge=1, le=500),
    repo: EventRepository = Depends(get_event_repository),
) -> dict[str, Any]:
    events = repo.list_events(
        priority_only=priority_only,
        score_min=score_min,
        score_max=score_max,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    return {"events": [_serialize_event(event, include_full_text=False) for event in events]}


@router.get("/{event_id}")
def get_event(
    event_id: uuid.UUID, repo: EventRepository = Depends(get_event_repository)
) -> dict[str, Any]:
    event = repo.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    return _serialize_event(event, include_full_text=True)


@router.post("/{event_id}/analyze", response_model=AnalyzeResponse)
def analyze_event_endpoint(
    event_id: uuid.UUID,
    payload: AnalyzeRequest,
    repo: EventRepository = Depends(get_event_repository),
) -> AnalyzeResponse:
    event = repo.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="event not found")
    if not event.priority_flag:
        raise HTTPException(status_code=400, detail="event is not priority")

    try:
        provider = resolve_provider(payload.provider, payload.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    request = AnalysisRequest(
        event=_to_macro_event_record(event),
        metals_knowledge=repo.fetch_metals(),
        historical_cases=repo.fetch_cases(event.event_type),
    )
    try:
        analysis, _prompt = analyze_event(provider, request)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    updated = repo.update_analysis(event_id, analysis, overwrite=payload.overwrite)
    return AnalyzeResponse(
        event_id=event_id,
        status="updated" if updated else "skipped",
        analysis=_serialize_analysis(analysis),
    )


def _serialize_event(event: MacroEventRow, *, include_full_text: bool) -> dict[str, Any]:
    raw: dict[str, Any] = {
        "id": event.id,
        "source": event.source,
        "headline": event.headline,
        "published_at": event.published_at,
        "event_type": event.event_type,
        "regions": event.regions,
        "entities": event.entities,
        "significance_score": event.significance_score,
        "priority_flag": event.priority_flag,
        "status": event.status,
    }
    if include_full_text:
        raw["full_text"] = event.full_text
    return {
        "raw": raw,
        "analysis": {
            "raw_facts": event.raw_facts,
            "interpretation": {
                "metal_impacts": event.metal_impacts,
                "historical_precedent": event.historical_precedent,
                "counter_case": event.counter_case,
                "crypto_transmission": event.crypto_transmission,
            },
        },
    }


def _serialize_analysis(analysis: MacroEventAnalysis) -> dict[str, Any]:
    return {
        "raw_facts": analysis.raw_facts,
        "interpretation": {
            "metal_impacts": analysis.metal_impacts,
            "historical_precedent": analysis.historical_precedent,
            "counter_case": analysis.counter_case,
            "crypto_transmission": analysis.crypto_transmission,
        },
    }


def _row_to_event(row: Sequence[Any]) -> MacroEventRow:
    return MacroEventRow(
        id=row[0],
        source=row[1],
        headline=row[2],
        full_text=row[3],
        published_at=row[4],
        event_type=row[5],
        regions=row[6],
        entities=row[7],
        significance_score=row[8],
        priority_flag=row[9],
        status=row[10],
        raw_facts=row[11],
        metal_impacts=row[12],
        historical_precedent=row[13],
        counter_case=row[14],
        crypto_transmission=row[15],
    )


def _to_macro_event_record(event: MacroEventRow) -> MacroEventRecord:
    return MacroEventRecord(
        id=event.id,
        source=event.source,
        headline=event.headline,
        full_text=event.full_text,
        published_at=event.published_at,
        event_type=event.event_type,
        regions=event.regions,
        entities=event.entities,
        significance_score=event.significance_score,
    )


def _start_of_day(value: date) -> datetime:
    return datetime.combine(value, time.min).replace(tzinfo=timezone.utc)


def _end_of_day(value: date) -> datetime:
    return datetime.combine(value, time.min).replace(tzinfo=timezone.utc) + timedelta(days=1)
