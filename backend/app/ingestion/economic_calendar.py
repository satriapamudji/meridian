from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import logging
from pathlib import Path
import time
from typing import Any, Iterable

import psycopg

from app.core.logging import configure_logging
from app.core.settings import get_settings, normalize_database_url

logger = logging.getLogger(__name__)

IMPACT_LEVELS = {"high", "medium", "low"}
MISSING_VALUE_TOKENS = {"", "-", "n/a", "na"}
DEFAULT_FOREX_FACTORY_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
DEFAULT_FRED_BASE_URL = "https://api.stlouisfed.org/fred"
FRED_IMPACT_LEVEL = "medium"
FRED_RELEASES_LIMIT = 50
FRED_RELEASE_DATES_LIMIT = 5
FRED_REQUEST_TIMEOUT = 30

# FRED Release ID mappings for key economic indicators
# Format: release_id -> (event_name, impact_level, region)
FRED_RELEASE_MAPPINGS: dict[int, tuple[str, str, str]] = {
    # High impact releases
    10: ("Consumer Price Index (CPI)", "high", "USD"),
    50: ("Employment Situation (NFP)", "high", "USD"),
    53: ("Gross Domestic Product (GDP)", "high", "USD"),
    54: ("Personal Income and Outlays (PCE)", "high", "USD"),
    101: ("FOMC Press Release", "high", "USD"),
    # Medium impact releases
    9: ("Retail Sales", "medium", "USD"),
    13: ("Industrial Production", "medium", "USD"),
    46: ("Producer Price Index (PPI)", "medium", "USD"),
    11: ("Unemployment Insurance Weekly Claims", "medium", "USD"),
}

# Default list of release IDs to fetch
DEFAULT_FRED_RELEASE_IDS = list(FRED_RELEASE_MAPPINGS.keys())


@dataclass(frozen=True)
class EconomicCalendarEvent:
    event_name: str
    event_date: datetime
    region: str
    impact_level: str
    expected_value: str | None
    actual_value: str | None
    previous_value: str | None
    surprise_direction: str | None
    surprise_magnitude: Decimal | None


class CalendarAdapter:
    name = "base"

    def fetch_events(self, start: datetime, end: datetime) -> list[EconomicCalendarEvent]:
        raise NotImplementedError


@dataclass(frozen=True)
class JsonCalendarAdapter(CalendarAdapter):
    data_dir: Path | None = None
    data_file: Path | None = None
    name: str = "json"

    def fetch_events(self, start: datetime, end: datetime) -> list[EconomicCalendarEvent]:
        payloads = load_calendar_payloads(self.data_dir, self.data_file)
        events: list[EconomicCalendarEvent] = []
        for source, payload in payloads:
            events.extend(parse_calendar_payload(payload, source))
        return filter_events(events, start, end)


@dataclass(frozen=True)
class ForexFactoryAdapter(CalendarAdapter):
    url: str = DEFAULT_FOREX_FACTORY_URL
    data_file: Path | None = None
    name: str = "forex_factory"
    future_only: bool = True

    def fetch_events(self, start: datetime, end: datetime) -> list[EconomicCalendarEvent]:
        if self.data_file is not None:
            payload = _load_json(self.data_file)
        else:
            payload = fetch_forex_factory_payload(self.url)
        events = parse_forex_factory_payload(payload)

        # Filter to future events only if enabled
        if self.future_only and self.data_file is None:
            now = datetime.now(timezone.utc)
            future_events = [e for e in events if e.event_date >= now]

            if events and not future_events:
                logger.warning(
                    "Forex Factory feed appears stale - all %d events are in the past. "
                    "Feed may not have updated yet for the new week.",
                    len(events),
                )
            events = future_events

        return filter_events(events, start, end)


@dataclass(frozen=True)
class FredCalendarAdapter(CalendarAdapter):
    api_key: str
    base_url: str = DEFAULT_FRED_BASE_URL
    data_file: Path | None = None
    name: str = "fred"
    release_ids: tuple[int, ...] | None = None

    def fetch_events(self, start: datetime, end: datetime) -> list[EconomicCalendarEvent]:
        if self.data_file is not None:
            payload = _load_json(self.data_file)
            fixture_events = parse_fred_fixture_payload(payload)
            return filter_events(fixture_events, start, end)

        # Use configured release IDs or default to high-impact releases
        ids_to_fetch = self.release_ids or tuple(DEFAULT_FRED_RELEASE_IDS)

        events: list[EconomicCalendarEvent] = []
        for release_id in ids_to_fetch:
            release_dates = fetch_fred_release_dates(
                self.base_url,
                self.api_key,
                release_id,
                start,
                end,
            )
            events.extend(release_dates)

        logger.info(
            "FRED calendar fetch complete: release_ids=%s events=%s",
            len(ids_to_fetch),
            len(events),
        )
        return filter_events(events, start, end)


def load_calendar_payloads(
    data_dir: Path | None,
    data_file: Path | None,
) -> list[tuple[str, Any]]:
    if data_dir and data_file:
        raise ValueError("Provide either data_dir or data_file, not both.")

    payloads: list[tuple[str, Any]] = []
    if data_file is not None:
        if not data_file.exists():
            raise FileNotFoundError(f"Calendar file not found: {data_file}")
        payloads.append((data_file.name, _load_json(data_file)))
        return payloads

    if data_dir is None:
        data_dir = default_calendar_dir()

    if not data_dir.exists():
        raise FileNotFoundError(f"Calendar directory not found: {data_dir}")

    for path in sorted(data_dir.glob("*.json")):
        payloads.append((path.name, _load_json(path)))

    return payloads


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_calendar_payload(payload: Any, source: str) -> list[EconomicCalendarEvent]:
    if isinstance(payload, dict):
        entries = payload.get("events")
        if entries is None:
            raise ValueError(f"{source}: expected 'events' list")
    elif isinstance(payload, list):
        entries = payload
    else:
        raise ValueError(f"{source}: payload must be an object or list")

    if not isinstance(entries, list):
        raise ValueError(f"{source}: events must be a list")

    events: list[EconomicCalendarEvent] = []
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            logger.warning("Skipping calendar entry %s #%s: not an object", source, idx)
            continue
        try:
            event = parse_calendar_entry(entry)
        except ValueError as exc:
            logger.warning("Skipping calendar entry %s #%s: %s", source, idx, exc)
            continue
        if event.impact_level not in IMPACT_LEVELS:
            continue
        events.append(event)
    return events


def parse_calendar_entry(entry: dict[str, Any]) -> EconomicCalendarEvent:
    event_name = _require_str(entry, ("event_name", "event", "name"))
    event_date_raw = _require_str(entry, ("event_date", "date", "datetime"))
    event_date = parse_event_datetime(event_date_raw)

    impact_raw = _require_str(entry, ("impact_level", "impact"))
    impact_level = normalize_impact_level(impact_raw)
    if impact_level is None:
        raise ValueError("impact_level must be high, medium, or low")

    region = _optional_str(entry, ("region", "currency")) or "unknown"
    expected_value = normalize_value(_optional_str(entry, ("expected_value", "expected")))
    actual_value = normalize_value(_optional_str(entry, ("actual_value", "actual")))
    previous_value = normalize_value(_optional_str(entry, ("previous_value", "previous")))

    return build_event(
        event_name=event_name,
        event_date=event_date,
        region=region,
        impact_level=impact_level,
        expected_value=expected_value,
        actual_value=actual_value,
        previous_value=previous_value,
    )


def parse_forex_factory_payload(payload: Any) -> list[EconomicCalendarEvent]:
    if not isinstance(payload, list):
        raise ValueError("forex_factory payload must be a list")

    events: list[EconomicCalendarEvent] = []
    for idx, entry in enumerate(payload):
        if not isinstance(entry, dict):
            logger.warning("Skipping forex factory entry #%s: not an object", idx)
            continue
        try:
            event = parse_forex_factory_entry(entry)
        except ValueError as exc:
            logger.warning("Skipping forex factory entry #%s: %s", idx, exc)
            continue
        if event.impact_level not in IMPACT_LEVELS:
            continue
        events.append(event)
    return events


def parse_forex_factory_entry(entry: dict[str, Any]) -> EconomicCalendarEvent:
    event_name = _require_str(entry, ("title", "event_name", "event"))
    event_date_raw = _require_str(entry, ("date", "event_date"))
    event_date = parse_event_datetime(event_date_raw)

    impact_raw = _require_str(entry, ("impact",))
    impact_level = normalize_impact_level(impact_raw)
    if impact_level is None:
        raise ValueError("impact must be high, medium, or low")

    region = _optional_str(entry, ("country", "region")) or "unknown"
    expected_value = normalize_value(_optional_str(entry, ("forecast", "expected")))
    actual_value = normalize_value(_optional_str(entry, ("actual",)))
    previous_value = normalize_value(_optional_str(entry, ("previous",)))

    return build_event(
        event_name=event_name,
        event_date=event_date,
        region=region,
        impact_level=impact_level,
        expected_value=expected_value,
        actual_value=actual_value,
        previous_value=previous_value,
    )


def fetch_forex_factory_payload(url: str) -> Any:
    import urllib.request
    from urllib.error import HTTPError

    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code in {403, 429}:
                if attempt == 0:
                    logger.warning(
                        "Forex factory feed rate-limited (%s); retrying once after delay.",
                        exc.code,
                    )
                    time.sleep(2)
                    continue
                logger.warning(
                    "Forex factory feed blocked (%s); returning empty payload.",
                    exc.code,
                )
                return []
            raise
    return []


def fetch_fred_payload(
    base_url: str,
    endpoint: str,
    params: dict[str, str],
    api_key: str,
) -> dict[str, Any]:
    import httpx

    if not api_key:
        raise ValueError("MERIDIAN_FRED_API_KEY is required for fred source.")

    request_params = {"api_key": api_key, "file_type": "json", **params}
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    for attempt in range(2):
        try:
            with httpx.Client(timeout=FRED_REQUEST_TIMEOUT) as client:
                response = client.get(
                    url,
                    params=request_params,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "FRED API request failed (%s) for %s", exc.response.status_code, endpoint
            )
            return {}
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as exc:
            if attempt == 0:
                logger.warning(
                    "FRED API request failed for %s: %s (retrying once).",
                    endpoint,
                    exc,
                )
                time.sleep(2)
                continue
            logger.warning("FRED API request failed for %s: %s", endpoint, exc)
            return {}
    return {}


def fetch_fred_release_dates(
    base_url: str,
    api_key: str,
    release_id: int,
    start: datetime,
    end: datetime,
) -> list[EconomicCalendarEvent]:
    """Fetch release dates for a specific FRED release ID and return as events."""
    # Get release info from mappings
    release_info = FRED_RELEASE_MAPPINGS.get(release_id)
    if release_info is None:
        event_name = f"FRED Release {release_id}"
        impact_level = FRED_IMPACT_LEVEL
        region = "USD"
    else:
        event_name, impact_level, region = release_info

    params = {
        "release_id": str(release_id),
        "realtime_start": start.date().isoformat(),
        "realtime_end": end.date().isoformat(),
        "include_release_dates_with_no_data": "true",
        "sort_order": "asc",
        "limit": "20",
    }

    payload = fetch_fred_payload(base_url, "release/dates", params, api_key)
    if not payload:
        return []

    release_dates_raw = payload.get("release_dates", [])
    if not isinstance(release_dates_raw, list):
        return []

    events: list[EconomicCalendarEvent] = []
    for entry in release_dates_raw:
        if not isinstance(entry, dict):
            continue
        date_str = entry.get("date")
        if not date_str:
            continue

        try:
            event_date = parse_event_datetime(date_str)
        except ValueError:
            continue

        events.append(
            EconomicCalendarEvent(
                event_name=event_name,
                event_date=event_date,
                region=region,
                impact_level=impact_level,
                expected_value=None,
                actual_value=None,
                previous_value=None,
                surprise_direction=None,
                surprise_magnitude=None,
            )
        )

    return events


def parse_fred_release_list(payload: Any) -> dict[int, str]:
    if not isinstance(payload, dict):
        logger.warning("FRED releases payload must be an object")
        return {}
    entries = payload.get("releases")
    if not isinstance(entries, list):
        logger.warning("FRED releases payload missing 'releases' list")
        return {}

    releases: dict[int, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        release_id = entry.get("id") or entry.get("release_id")
        name = entry.get("name") or entry.get("release_name")
        if release_id is None or name is None:
            continue
        try:
            release_key = int(release_id)
        except (TypeError, ValueError):
            continue
        releases[release_key] = str(name).strip()
    return releases


def parse_fred_release_dates(payload: Any) -> list[tuple[int, str, str | None]]:
    if not isinstance(payload, dict):
        logger.warning("FRED release dates payload must be an object")
        return []
    entries = payload.get("release_dates")
    if not isinstance(entries, list):
        logger.warning("FRED release dates payload missing 'release_dates' list")
        return []

    release_dates: list[tuple[int, str, str | None]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        release_id = entry.get("release_id") or entry.get("id")
        date_value = entry.get("date") or entry.get("release_date")
        name_value = entry.get("release_name") or entry.get("name")
        if release_id is None or date_value is None:
            continue
        try:
            release_key = int(release_id)
        except (TypeError, ValueError):
            continue
        if not isinstance(date_value, str) or not date_value.strip():
            continue
        release_name = None
        if isinstance(name_value, str) and name_value.strip():
            release_name = name_value.strip()
        release_dates.append((release_key, date_value.strip(), release_name))
    return release_dates


def build_fred_events(
    release_dates: Iterable[tuple[int, str, str | None]],
    release_names: dict[int, str],
) -> list[EconomicCalendarEvent]:
    events: list[EconomicCalendarEvent] = []
    for release_id, date_value, release_name in release_dates:
        name = release_name or release_names.get(release_id, f"FRED Release {release_id}")
        event_date = parse_event_datetime(date_value)
        events.append(
            build_event(
                event_name=name,
                event_date=event_date,
                region="US",
                impact_level=FRED_IMPACT_LEVEL,
                expected_value=None,
                actual_value=None,
                previous_value=None,
            )
        )
    return events


def parse_fred_fixture_payload(payload: Any) -> list[EconomicCalendarEvent]:
    release_names = parse_fred_release_list(payload)
    release_dates = parse_fred_release_dates(payload)
    return build_fred_events(release_dates, release_names)


def filter_events(
    events: Iterable[EconomicCalendarEvent],
    start: datetime,
    end: datetime,
) -> list[EconomicCalendarEvent]:
    return [event for event in events if start <= event.event_date < end]


def parse_event_datetime(value: str) -> datetime:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_impact_level(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().lower()
    if cleaned in ("med", "medium"):
        return "medium"
    if cleaned in ("hi", "high"):
        return "high"
    if cleaned in ("lo", "low"):
        return "low"
    return None


def normalize_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned.lower() in MISSING_VALUE_TOKENS:
        return None
    return cleaned


def parse_numeric_value(value: str | None) -> Decimal | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned.lower() in MISSING_VALUE_TOKENS:
        return None

    multiplier = Decimal("1")
    suffix = cleaned[-1].upper()
    if suffix in {"K", "M", "B", "%"}:
        cleaned = cleaned[:-1].strip()
        if suffix == "K":
            multiplier = Decimal("1000")
        elif suffix == "M":
            multiplier = Decimal("1000000")
        elif suffix == "B":
            multiplier = Decimal("1000000000")

    cleaned = cleaned.replace(",", "")
    try:
        number = Decimal(cleaned)
    except InvalidOperation:
        return None
    return number * multiplier


def calculate_surprise(
    actual_value: str | None,
    expected_value: str | None,
) -> tuple[str, Decimal] | None:
    actual = parse_numeric_value(actual_value)
    expected = parse_numeric_value(expected_value)
    if actual is None or expected is None:
        return None

    if actual > expected:
        direction = "positive"
    elif actual < expected:
        direction = "negative"
    else:
        direction = "flat"
    magnitude = (actual - expected).copy_abs()
    return direction, magnitude


def build_event(
    *,
    event_name: str,
    event_date: datetime,
    region: str,
    impact_level: str,
    expected_value: str | None,
    actual_value: str | None,
    previous_value: str | None,
) -> EconomicCalendarEvent:
    surprise = calculate_surprise(actual_value, expected_value)
    surprise_direction = None
    surprise_magnitude = None
    if surprise is not None:
        surprise_direction, surprise_magnitude = surprise
        logger.info(
            "Surprise computed for %s: actual=%s expected=%s direction=%s magnitude=%s",
            event_name,
            actual_value,
            expected_value,
            surprise_direction,
            surprise_magnitude,
        )

    return EconomicCalendarEvent(
        event_name=event_name,
        event_date=event_date,
        region=region,
        impact_level=impact_level,
        expected_value=expected_value,
        actual_value=actual_value,
        previous_value=previous_value,
        surprise_direction=surprise_direction,
        surprise_magnitude=surprise_magnitude,
    )


def _require_str(entry: dict[str, Any], keys: Iterable[str]) -> str:
    value = _first_value(entry, keys)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"field '{keys}' must be a non-empty string")
    return value.strip()


def _optional_str(entry: dict[str, Any], keys: Iterable[str]) -> str | None:
    value = _first_value(entry, keys)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"field '{keys}' must be a string")
    return value.strip()


def _first_value(entry: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in entry:
            return entry[key]
    return None


def load_calendar_entries(data_dir: Path) -> list[EconomicCalendarEvent]:
    payloads = load_calendar_payloads(data_dir, None)
    entries: list[EconomicCalendarEvent] = []
    for source, payload in payloads:
        entries.extend(parse_calendar_payload(payload, source))
    return entries


def build_window(days: int, now: datetime | None = None) -> tuple[datetime, datetime]:
    if days <= 0:
        raise ValueError("days must be positive")
    current = now or datetime.now(timezone.utc)
    start = datetime(current.year, current.month, current.day, tzinfo=timezone.utc)
    end = start + timedelta(days=days)
    return start, end


def upsert_events(events: Iterable[EconomicCalendarEvent]) -> int:
    event_list = list(events)
    if not event_list:
        return 0

    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        INSERT INTO economic_events (
            id,
            event_name,
            event_date,
            region,
            impact_level,
            expected_value,
            actual_value,
            previous_value,
            surprise_direction,
            surprise_magnitude
        )
        VALUES (
            gen_random_uuid(),
            %(event_name)s,
            %(event_date)s,
            %(region)s,
            %(impact_level)s,
            %(expected_value)s,
            %(actual_value)s,
            %(previous_value)s,
            %(surprise_direction)s,
            %(surprise_magnitude)s
        )
        ON CONFLICT (event_name, event_date, region)
        DO UPDATE SET
            impact_level = EXCLUDED.impact_level,
            expected_value = EXCLUDED.expected_value,
            actual_value = EXCLUDED.actual_value,
            previous_value = EXCLUDED.previous_value,
            surprise_direction = EXCLUDED.surprise_direction,
            surprise_magnitude = EXCLUDED.surprise_magnitude
    """

    inserted = 0
    with psycopg.connect(database_url) as conn:
        for event in event_list:
            result = conn.execute(
                query,
                {
                    "event_name": event.event_name,
                    "event_date": event.event_date,
                    "region": event.region,
                    "impact_level": event.impact_level,
                    "expected_value": event.expected_value,
                    "actual_value": event.actual_value,
                    "previous_value": event.previous_value,
                    "surprise_direction": event.surprise_direction,
                    "surprise_magnitude": event.surprise_magnitude,
                },
            )
            inserted += result.rowcount or 0
    return inserted


def fetch_events_between(start: datetime, end: datetime) -> list[EconomicCalendarEvent]:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        SELECT
            event_name,
            event_date,
            region,
            impact_level,
            expected_value,
            actual_value,
            previous_value,
            surprise_direction,
            surprise_magnitude
        FROM economic_events
        WHERE event_date >= %(start)s AND event_date < %(end)s
        ORDER BY event_date ASC
    """

    events: list[EconomicCalendarEvent] = []
    with psycopg.connect(database_url) as conn:
        rows = conn.execute(query, {"start": start, "end": end}).fetchall()
    for row in rows:
        events.append(
            EconomicCalendarEvent(
                event_name=row[0],
                event_date=row[1],
                region=row[2],
                impact_level=row[3],
                expected_value=row[4],
                actual_value=row[5],
                previous_value=row[6],
                surprise_direction=row[7],
                surprise_magnitude=row[8],
            )
        )
    return events


def default_calendar_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "calendar"


def sync_calendar(adapter: CalendarAdapter, days: int) -> int:
    start, end = build_window(days)
    events = adapter.fetch_events(start, end)
    inserted = upsert_events(events)
    logger.info(
        "Economic calendar sync complete: source=%s events=%s inserted=%s",
        adapter.name,
        len(events),
        inserted,
    )
    return inserted


def run(interval: int, adapter: CalendarAdapter, days: int) -> None:
    while True:
        sync_calendar(adapter, days)
        if interval <= 0:
            return
        time.sleep(interval)


def resolve_adapter(
    source: str,
    data_dir: Path | None,
    data_file: Path | None,
    url: str,
    fred_api_key: str,
) -> CalendarAdapter:
    if source == "json":
        return JsonCalendarAdapter(data_dir=data_dir, data_file=data_file)
    if source == "forex_factory":
        return ForexFactoryAdapter(url=url, data_file=data_file)
    if source == "fred":
        return FredCalendarAdapter(api_key=fred_api_key, data_file=data_file)
    raise ValueError(f"Unknown source: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync economic calendar events")
    parser.add_argument(
        "--source",
        choices=("json", "forex_factory", "fred"),
        default="json",
        help="Calendar source adapter (default: json)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Path to calendar JSON files (default: data/calendar)",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=None,
        help="Path to a single calendar JSON file",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_FOREX_FACTORY_URL,
        help="Override forex factory feed URL",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to sync starting today",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Poll interval in seconds (0 runs once)",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    adapter = resolve_adapter(
        args.source,
        args.data_dir,
        args.data_file,
        args.url,
        settings.fred_api_key,
    )
    run(args.interval, adapter, args.days)


if __name__ == "__main__":
    main()
