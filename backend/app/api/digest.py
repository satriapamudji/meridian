from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.digests import get_or_create_digest

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/today")
def get_today_digest() -> dict[str, Any]:
    digest_date = datetime.now(timezone.utc).date()
    try:
        digest = get_or_create_digest(digest_date)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="digest unavailable") from exc
    return digest.as_response()
