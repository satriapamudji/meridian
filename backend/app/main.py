from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
import psycopg

from app.api.digest import router as digest_router
from app.api.events import router as events_router
from app.api.theses import router as theses_router
from app.core.logging import configure_logging
from app.core.settings import get_settings, normalize_database_url

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="Meridian API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        database_url = normalize_database_url(settings.database_url)
        try:
            with psycopg.connect(database_url, connect_timeout=2) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
        except Exception as exc:
            logger.exception("Database readiness check failed")
            raise HTTPException(status_code=503, detail="database unavailable") from exc

        return {"status": "ready"}

    app.include_router(events_router)
    app.include_router(digest_router)
    app.include_router(theses_router)

    return app


app = create_app()
