from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.settings import get_settings
from app.main import create_app


def test_health_ok() -> None:
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_503_when_db_unavailable(monkeypatch) -> None:
    monkeypatch.setenv(
        "MERIDIAN_DATABASE_URL",
        "postgresql://meridian:meridian@localhost:6543/meridian",
    )
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"
