from __future__ import annotations

from datetime import datetime, timezone
import uuid

from fastapi.testclient import TestClient

from app.api.events import MacroEventRow, get_event_repository
from app.main import create_app


class FakeEventRepository:
    def __init__(self, event: MacroEventRow) -> None:
        self._event = event
        self.updated_analysis = None

    def list_events(
        self,
        *,
        priority_only: bool,
        score_min: int | None,
        score_max: int | None,
        status: str | None,
        start_date,
        end_date,
        limit: int,
    ) -> list[MacroEventRow]:
        return [self._event]

    def get_event(self, event_id: uuid.UUID) -> MacroEventRow | None:
        if event_id == self._event.id:
            return self._event
        return None

    def update_analysis(self, event_id: uuid.UUID, analysis, *, overwrite: bool) -> bool:
        self.updated_analysis = analysis
        return True

    def fetch_metals(self) -> list:
        return []

    def fetch_cases(self, event_type: str | None) -> list:
        return []


def _build_event() -> MacroEventRow:
    return MacroEventRow(
        id=uuid.uuid4(),
        source="reuters",
        headline="Fed signals patience",
        full_text="The committee held rates steady.",
        published_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        event_type="monetary_policy",
        regions=["US"],
        entities=["Federal Reserve"],
        significance_score=72,
        priority_flag=True,
        status="new",
        raw_facts=None,
        metal_impacts=None,
        historical_precedent=None,
        counter_case=None,
        crypto_transmission=None,
    )


def test_list_events_returns_raw_and_analysis() -> None:
    app = create_app()
    event = _build_event()
    repo = FakeEventRepository(event)
    app.dependency_overrides[get_event_repository] = lambda: repo
    client = TestClient(app)

    response = client.get("/events")
    assert response.status_code == 200
    payload = response.json()
    entry = payload["events"][0]

    assert entry["raw"]["id"] == str(event.id)
    assert "full_text" not in entry["raw"]
    assert "analysis" in entry
    assert "interpretation" in entry["analysis"]


def test_get_event_includes_full_text() -> None:
    app = create_app()
    event = _build_event()
    repo = FakeEventRepository(event)
    app.dependency_overrides[get_event_repository] = lambda: repo
    client = TestClient(app)

    response = client.get(f"/events/{event.id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["raw"]["full_text"] == event.full_text


def test_analyze_event_endpoint_updates_analysis() -> None:
    app = create_app()
    event = _build_event()
    repo = FakeEventRepository(event)
    app.dependency_overrides[get_event_repository] = lambda: repo
    client = TestClient(app)

    response = client.post(
        f"/events/{event.id}/analyze",
        json={"provider": "local", "overwrite": True},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "updated"
    assert payload["analysis"]["raw_facts"]
