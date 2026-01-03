from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
import psycopg
from psycopg.types.json import Json

from app.core.settings import get_settings, normalize_database_url
from app.services.thesis_export import render_thesis_markdown

router = APIRouter(prefix="/theses", tags=["theses"])

ALLOWED_STATUSES = {"watching", "active", "closed"}

THESIS_COLUMNS = [
    "id",
    "created_at",
    "updated_at",
    "title",
    "asset_type",
    "asset_symbol",
    "trigger_event",
    "core_thesis",
    "bull_case",
    "bear_case",
    "historical_precedent",
    "entry_consideration",
    "target",
    "invalidation",
    "vehicle",
    "position_size",
    "entry_date",
    "entry_price",
    "status",
    "price_at_creation",
    "current_price",
    "price_change_percent",
    "updates",
]


class ThesisCreate(BaseModel):
    title: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)
    core_thesis: str = Field(min_length=1)
    asset_symbol: str | None = None
    trigger_event: str | None = None
    bull_case: list[str] | None = None
    bear_case: list[str] | None = None
    historical_precedent: str | None = None
    entry_consideration: str | None = None
    target: str | None = None
    invalidation: str | None = None
    vehicle: str | None = None
    position_size: str | None = None
    entry_date: datetime | None = None
    entry_price: Decimal | None = None
    status: str | None = None
    price_at_creation: Decimal | None = None
    current_price: Decimal | None = None
    price_change_percent: Decimal | None = None


class ThesisUpdate(BaseModel):
    title: str | None = None
    asset_type: str | None = None
    core_thesis: str | None = None
    asset_symbol: str | None = None
    trigger_event: str | None = None
    bull_case: list[str] | None = None
    bear_case: list[str] | None = None
    historical_precedent: str | None = None
    entry_consideration: str | None = None
    target: str | None = None
    invalidation: str | None = None
    vehicle: str | None = None
    position_size: str | None = None
    entry_date: datetime | None = None
    entry_price: Decimal | None = None
    status: str | None = None
    price_at_creation: Decimal | None = None
    current_price: Decimal | None = None
    price_change_percent: Decimal | None = None


class ThesisUpdateEntry(BaseModel):
    note: str = Field(min_length=1)
    date: datetime | None = None
    price: Decimal | None = None


class ThesisResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    title: str
    asset_type: str
    asset_symbol: str | None = None
    trigger_event: str | None = None
    core_thesis: str
    bull_case: list[str] | None = None
    bear_case: list[str] | None = None
    historical_precedent: str | None = None
    entry_consideration: str | None = None
    target: str | None = None
    invalidation: str | None = None
    vehicle: str | None = None
    position_size: str | None = None
    entry_date: datetime | None = None
    entry_price: Decimal | None = None
    status: str
    price_at_creation: Decimal | None = None
    current_price: Decimal | None = None
    price_change_percent: Decimal | None = None
    updates: list[dict[str, Any]]


@router.get("", response_model=list[ThesisResponse])
def list_theses(status: str | None = None) -> list[ThesisResponse]:
    query = "SELECT " + ", ".join(THESIS_COLUMNS) + " FROM theses"
    params: dict[str, object] = {}
    if status:
        normalized = _normalize_status(status)
        query += " WHERE status = %(status)s"
        params["status"] = normalized
    query += " ORDER BY updated_at DESC NULLS LAST, created_at DESC"
    rows = _fetch_rows(query, params)
    return [_row_to_thesis(row) for row in rows]


@router.post("", response_model=ThesisResponse, status_code=status.HTTP_201_CREATED)
def create_thesis(payload: ThesisCreate) -> ThesisResponse:
    normalized_status = _normalize_status(payload.status)
    _ensure_thesis_requirements(
        normalized_status, payload.bear_case, payload.invalidation
    )
    query = """
        INSERT INTO theses (
            title,
            asset_type,
            asset_symbol,
            trigger_event,
            core_thesis,
            bull_case,
            bear_case,
            historical_precedent,
            entry_consideration,
            target,
            invalidation,
            vehicle,
            position_size,
            entry_date,
            entry_price,
            status,
            price_at_creation,
            current_price,
            price_change_percent,
            updates
        )
        VALUES (
            %(title)s,
            %(asset_type)s,
            %(asset_symbol)s,
            %(trigger_event)s,
            %(core_thesis)s,
            %(bull_case)s,
            %(bear_case)s,
            %(historical_precedent)s,
            %(entry_consideration)s,
            %(target)s,
            %(invalidation)s,
            %(vehicle)s,
            %(position_size)s,
            %(entry_date)s,
            %(entry_price)s,
            %(status)s,
            %(price_at_creation)s,
            %(current_price)s,
            %(price_change_percent)s,
            %(updates)s
        )
        RETURNING {columns}
    """.format(columns=", ".join(THESIS_COLUMNS))
    params = payload.model_dump()
    params["status"] = normalized_status
    params["updates"] = Json([])
    row = _require_row(_fetch_one(query, params))
    return _row_to_thesis(row)


@router.get("/{thesis_id}", response_model=ThesisResponse)
def get_thesis(thesis_id: uuid.UUID) -> ThesisResponse:
    row = _fetch_thesis_row(thesis_id)
    return _row_to_thesis(row)


@router.patch("/{thesis_id}", response_model=ThesisResponse)
def update_thesis(thesis_id: uuid.UUID, payload: ThesisUpdate) -> ThesisResponse:
    current = _row_to_payload(_fetch_thesis_row(thesis_id))
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    if "status" in data:
        data["status"] = _normalize_status(data["status"])
    next_status = data.get("status", current["status"])
    next_bear_case = data.get("bear_case", current.get("bear_case"))
    next_invalidation = data.get("invalidation", current.get("invalidation"))
    _ensure_thesis_requirements(next_status, next_bear_case, next_invalidation)

    set_clauses = [f"{field} = %({field})s" for field in data]
    set_clauses.append("updated_at = now()")
    query = f"""
        UPDATE theses
        SET {", ".join(set_clauses)}
        WHERE id = %(id)s
        RETURNING {", ".join(THESIS_COLUMNS)}
    """
    data["id"] = thesis_id
    row = _require_row(_fetch_one(query, data))
    return _row_to_thesis(row)


@router.post("/{thesis_id}/updates", response_model=ThesisResponse)
def add_thesis_update(thesis_id: uuid.UUID, payload: ThesisUpdateEntry) -> ThesisResponse:
    row = _fetch_thesis_row(thesis_id)
    thesis = _row_to_payload(row)
    updates = thesis.get("updates") or []
    update_entry = _normalize_update_entry(payload)
    updates.append(update_entry)
    query = f"""
        UPDATE theses
        SET updates = %(updates)s,
            updated_at = now()
        WHERE id = %(id)s
        RETURNING {", ".join(THESIS_COLUMNS)}
    """
    params = {"updates": Json(updates), "id": thesis_id}
    updated = _require_row(_fetch_one(query, params))
    return _row_to_thesis(updated)


@router.get("/{thesis_id}/export.md", response_class=PlainTextResponse)
def export_thesis_markdown(thesis_id: uuid.UUID) -> PlainTextResponse:
    row = _fetch_thesis_row(thesis_id)
    thesis = _row_to_payload(row)
    markdown = render_thesis_markdown(thesis)
    return PlainTextResponse(markdown, media_type="text/markdown")


def _normalize_update_entry(payload: ThesisUpdateEntry) -> dict[str, Any]:
    timestamp = payload.date or datetime.now(timezone.utc)
    entry: dict[str, Any] = {
        "date": timestamp.isoformat(),
        "note": payload.note.strip(),
    }
    if payload.price is not None:
        entry["price"] = float(payload.price)
    return entry


def _ensure_thesis_requirements(
    status_value: str | None,
    bear_case: list[str] | None,
    invalidation: str | None,
) -> None:
    if status_value != "active":
        return
    if not bear_case or not any(item.strip() for item in bear_case if item):
        raise HTTPException(
            status_code=400,
            detail="bear_case is required when status is active",
        )
    if not invalidation or not invalidation.strip():
        raise HTTPException(
            status_code=400,
            detail="invalidation is required when status is active",
        )


def _normalize_status(status_value: str | None) -> str:
    if not status_value:
        return "watching"
    normalized = status_value.strip().lower()
    if normalized not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid thesis status")
    return normalized


def _fetch_thesis_row(thesis_id: uuid.UUID) -> tuple[Any, ...]:
    query = """
        SELECT {columns}
        FROM theses
        WHERE id = %(id)s
    """.format(columns=", ".join(THESIS_COLUMNS))
    row = _fetch_one(query, {"id": thesis_id})
    if row is None:
        raise HTTPException(status_code=404, detail="Thesis not found")
    return row


def _row_to_payload(row: tuple[Any, ...]) -> dict[str, Any]:
    payload = dict(zip(THESIS_COLUMNS, row))
    updates = payload.get("updates")
    payload["updates"] = updates if isinstance(updates, list) else []
    return payload


def _row_to_thesis(row: tuple[Any, ...]) -> ThesisResponse:
    return ThesisResponse(**_row_to_payload(row))


def _require_row(row: tuple[Any, ...] | None) -> tuple[Any, ...]:
    if row is None:
        raise HTTPException(status_code=500, detail="Thesis query returned no rows")
    return row


def _fetch_rows(query: str, params: dict[str, object]) -> list[tuple[Any, ...]]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    with psycopg.connect(database_url) as conn:
        return conn.execute(query, params).fetchall()


def _fetch_one(query: str, params: dict[str, object]) -> tuple[Any, ...] | None:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    with psycopg.connect(database_url) as conn:
        return conn.execute(query, params).fetchone()
