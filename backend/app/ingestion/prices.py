from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import logging
import math
import time
from typing import Any, Iterable
import urllib.parse
import urllib.request

import httpx
import psycopg

from app.core.settings import get_settings, normalize_database_url

CORE_SYMBOLS = ("GC=F", "SI=F", "HG=F")
OPTIONAL_SYMBOLS = ("GLD", "SLV", "COPX", "NEM", "GOLD", "FCX")
DEFAULT_LOOKBACK_DAYS = 10
DEFAULT_SOURCE = "yahoo"
FRED_SOURCE = "fred"
GOLD_SYMBOL = "GC=F"
SILVER_SYMBOL = "SI=F"
DEFAULT_RATIO_NAME = "gold_silver"

# FRED API configuration
DEFAULT_FRED_BASE_URL = "https://api.stlouisfed.org/fred"
FRED_REQUEST_TIMEOUT = 30

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PriceBar:
    symbol: str
    price_date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    adj_close: Decimal | None
    volume: int | None


@dataclass(frozen=True)
class RatioEntry:
    ratio_name: str
    price_date: date
    value: Decimal
    base_symbol: str
    quote_symbol: str


def parse_yahoo_chart(payload: str, symbol: str) -> list[PriceBar]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []
    chart = data.get("chart") or {}
    if chart.get("error"):
        return []
    result = chart.get("result") or []
    if not result:
        return []
    series = result[0] or {}
    timestamps = series.get("timestamp") or []
    if not isinstance(timestamps, list):
        return []
    indicators = series.get("indicators") or {}
    quote_list = indicators.get("quote") or []
    quote = quote_list[0] if quote_list else {}
    if not isinstance(quote, dict):
        quote = {}
    adjclose_list = indicators.get("adjclose") or []
    adjclose_series: list[object] = []
    if adjclose_list:
        adjclose_candidate = adjclose_list[0]
        if isinstance(adjclose_candidate, dict):
            adjclose_series = adjclose_candidate.get("adjclose") or []
    if not isinstance(adjclose_series, list):
        adjclose_series = []

    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    bars: list[PriceBar] = []
    for idx, ts in enumerate(timestamps):
        price_date = _parse_timestamp_date(ts)
        if price_date is None:
            continue
        close_value = _parse_decimal(_value_at(closes, idx))
        if close_value is None:
            continue
        bars.append(
            PriceBar(
                symbol=symbol,
                price_date=price_date,
                open=_parse_decimal(_value_at(opens, idx)),
                high=_parse_decimal(_value_at(highs, idx)),
                low=_parse_decimal(_value_at(lows, idx)),
                close=close_value,
                adj_close=_parse_decimal(_value_at(adjclose_series, idx)),
                volume=_parse_int(_value_at(volumes, idx)),
            )
        )
    return bars


def build_ratio_series(
    base_symbol: str,
    quote_symbol: str,
    base_bars: Iterable[PriceBar],
    quote_bars: Iterable[PriceBar],
    ratio_name: str = DEFAULT_RATIO_NAME,
) -> list[RatioEntry]:
    base_map = {
        bar.price_date: bar.close
        for bar in base_bars
        if bar.close is not None and bar.symbol == base_symbol
    }
    quote_map = {
        bar.price_date: bar.close
        for bar in quote_bars
        if bar.close is not None and bar.symbol == quote_symbol
    }
    shared_dates = sorted(set(base_map) & set(quote_map))
    ratios: list[RatioEntry] = []
    for ratio_date in shared_dates:
        quote_value = quote_map[ratio_date]
        base_value = base_map[ratio_date]
        if quote_value is None or base_value is None or quote_value == 0:
            continue
        ratios.append(
            RatioEntry(
                ratio_name=ratio_name,
                price_date=ratio_date,
                value=base_value / quote_value,
                base_symbol=base_symbol,
                quote_symbol=quote_symbol,
            )
        )
    return ratios


def build_yahoo_chart_url(symbol: str, start_date: date, end_date: date) -> str:
    start = _to_unix_seconds(start_date)
    end = _to_unix_seconds(end_date + timedelta(days=1))
    query = urllib.parse.urlencode(
        {
            "period1": start,
            "period2": end,
            "interval": "1d",
            "includeAdjustedClose": "true",
        }
    )
    encoded_symbol = urllib.parse.quote(symbol, safe="")
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?{query}"


def fetch_yahoo_chart(symbol: str, start_date: date, end_date: date) -> str:
    url = build_yahoo_chart_url(symbol, start_date, end_date)
    request = urllib.request.Request(url, headers={"User-Agent": "MeridianBot/0.1"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


def insert_prices(bars: Iterable[PriceBar], source: str = DEFAULT_SOURCE) -> int:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        INSERT INTO daily_prices (
            id,
            symbol,
            price_date,
            open,
            high,
            low,
            close,
            adj_close,
            volume,
            source,
            created_at
        )
        VALUES (
            gen_random_uuid(),
            %(symbol)s,
            %(price_date)s,
            %(open)s,
            %(high)s,
            %(low)s,
            %(close)s,
            %(adj_close)s,
            %(volume)s,
            %(source)s,
            now()
        )
        ON CONFLICT (symbol, price_date)
        DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            adj_close = EXCLUDED.adj_close,
            volume = EXCLUDED.volume,
            source = EXCLUDED.source
    """
    inserted = 0
    with psycopg.connect(database_url) as conn:
        for bar in bars:
            result = conn.execute(
                query,
                {
                    "symbol": bar.symbol,
                    "price_date": bar.price_date,
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "adj_close": bar.adj_close,
                    "volume": bar.volume,
                    "source": source,
                },
            )
            inserted += result.rowcount or 0
    return inserted


def insert_price_ratios(entries: Iterable[RatioEntry]) -> int:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    query = """
        INSERT INTO price_ratios (
            id,
            ratio_name,
            price_date,
            value,
            base_symbol,
            quote_symbol,
            created_at
        )
        VALUES (
            gen_random_uuid(),
            %(ratio_name)s,
            %(price_date)s,
            %(value)s,
            %(base_symbol)s,
            %(quote_symbol)s,
            now()
        )
        ON CONFLICT (ratio_name, price_date)
        DO UPDATE SET
            value = EXCLUDED.value,
            base_symbol = EXCLUDED.base_symbol,
            quote_symbol = EXCLUDED.quote_symbol
    """
    inserted = 0
    with psycopg.connect(database_url) as conn:
        for entry in entries:
            result = conn.execute(
                query,
                {
                    "ratio_name": entry.ratio_name,
                    "price_date": entry.price_date,
                    "value": entry.value,
                    "base_symbol": entry.base_symbol,
                    "quote_symbol": entry.quote_symbol,
                },
            )
            inserted += result.rowcount or 0
    return inserted


def ingest_prices(symbols: Iterable[str], start_date: date, end_date: date) -> dict[str, int]:
    results: dict[str, int] = {}
    bars_by_symbol: dict[str, list[PriceBar]] = {}
    for symbol in symbols:
        try:
            payload = fetch_yahoo_chart(symbol, start_date, end_date)
            bars = parse_yahoo_chart(payload, symbol)
            bars_by_symbol[symbol] = bars
            results[symbol] = insert_prices(bars)
        except Exception:
            logger.exception("Price ingestion failed for %s", symbol)
            results[symbol] = 0
    ratio_inserted = 0
    gold_bars = bars_by_symbol.get(GOLD_SYMBOL)
    silver_bars = bars_by_symbol.get(SILVER_SYMBOL)
    if gold_bars and silver_bars:
        ratio_entries = build_ratio_series(GOLD_SYMBOL, SILVER_SYMBOL, gold_bars, silver_bars)
        if ratio_entries:
            try:
                ratio_inserted = insert_price_ratios(ratio_entries)
            except Exception:
                logger.exception("Price ratio ingestion failed for %s", DEFAULT_RATIO_NAME)
                ratio_inserted = 0
    results[DEFAULT_RATIO_NAME] = ratio_inserted
    return results


def _parse_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return Decimal(str(value))
    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw.lower() in {"null", "nan"}:
            return None
        try:
            return Decimal(raw)
        except InvalidOperation:
            return None
    return None


def _parse_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return int(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw or raw.lower() in {"null", "nan"}:
            return None
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def _parse_timestamp_date(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        ts = value
    elif isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        ts = int(value)
    elif isinstance(value, Decimal):
        ts = int(value)
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            ts = int(raw)
        except ValueError:
            return None
    else:
        return None
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).date()
    except (OverflowError, OSError, ValueError):
        return None


def _value_at(values: list[object], idx: int) -> object | None:
    if idx >= len(values):
        return None
    return values[idx]


def _to_unix_seconds(value: date) -> int:
    return int(datetime(value.year, value.month, value.day, tzinfo=timezone.utc).timestamp())


# ---------------------------------------------------------------------------
# FRED Series Fetching
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FredObservation:
    """A single FRED observation (date + value)."""

    series_id: str
    observation_date: date
    value: Decimal | None


def fetch_fred_payload(
    base_url: str,
    endpoint: str,
    params: dict[str, str],
    api_key: str,
) -> dict[str, Any]:
    """
    Fetch a FRED API endpoint with retries and error handling.

    Reuses the same pattern from economic_calendar.py for consistency.
    """
    if not api_key:
        raise ValueError("MERIDIAN_FRED_API_KEY is required for FRED data.")

    request_params = {"api_key": api_key, "file_type": "json", **params}
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    for attempt in range(2):
        try:
            with httpx.Client(timeout=FRED_REQUEST_TIMEOUT) as client:
                response = client.get(
                    url,
                    params=request_params,
                    headers={"User-Agent": "MeridianBot/0.1"},
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


def parse_fred_observations(payload: dict[str, Any], series_id: str) -> list[FredObservation]:
    """Parse FRED observations API response into FredObservation objects."""
    observations_raw = payload.get("observations", [])
    if not isinstance(observations_raw, list):
        return []

    observations: list[FredObservation] = []
    for entry in observations_raw:
        if not isinstance(entry, dict):
            continue

        date_str = entry.get("date")
        value_str = entry.get("value")

        if not date_str:
            continue

        # Parse date
        try:
            obs_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Parse value - FRED uses "." for missing values
        obs_value: Decimal | None = None
        if value_str and value_str != ".":
            obs_value = _parse_decimal(value_str)

        observations.append(
            FredObservation(
                series_id=series_id,
                observation_date=obs_date,
                value=obs_value,
            )
        )

    return observations


def fetch_fred_series(
    series_id: str,
    start_date: date,
    end_date: date,
    api_key: str | None = None,
    base_url: str = DEFAULT_FRED_BASE_URL,
) -> list[FredObservation]:
    """
    Fetch observations for a FRED series.

    Args:
        series_id: FRED series ID (e.g., "DGS10" for 10-year Treasury)
        start_date: Start date for observations
        end_date: End date for observations
        api_key: FRED API key (uses settings if not provided)
        base_url: FRED API base URL

    Returns:
        List of FredObservation objects with date and value
    """
    if api_key is None:
        settings = get_settings()
        api_key = settings.fred_api_key

    if not api_key:
        logger.warning("No FRED API key configured; skipping series %s", series_id)
        return []

    params = {
        "series_id": series_id,
        "observation_start": start_date.isoformat(),
        "observation_end": end_date.isoformat(),
        "sort_order": "asc",
    }

    payload = fetch_fred_payload(base_url, "series/observations", params, api_key)
    if not payload:
        return []

    observations = parse_fred_observations(payload, series_id)
    logger.debug(
        "FRED series %s: fetched %d observations from %s to %s",
        series_id,
        len(observations),
        start_date,
        end_date,
    )
    return observations


def fetch_fred_series_batch(
    series_ids: Iterable[str],
    start_date: date,
    end_date: date,
    api_key: str | None = None,
    base_url: str = DEFAULT_FRED_BASE_URL,
) -> dict[str, list[FredObservation]]:
    """
    Fetch multiple FRED series in sequence.

    Args:
        series_ids: List of FRED series IDs
        start_date: Start date for observations
        end_date: End date for observations
        api_key: FRED API key (uses settings if not provided)
        base_url: FRED API base URL

    Returns:
        Dict mapping series_id -> list of FredObservation
    """
    if api_key is None:
        settings = get_settings()
        api_key = settings.fred_api_key

    results: dict[str, list[FredObservation]] = {}

    for series_id in series_ids:
        try:
            observations = fetch_fred_series(
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
                api_key=api_key,
                base_url=base_url,
            )
            results[series_id] = observations
        except Exception:
            logger.exception("FRED series fetch failed for %s", series_id)
            results[series_id] = []

        # Small delay to respect FRED rate limits
        time.sleep(0.2)

    return results


def fred_observations_to_price_bars(
    observations: Iterable[FredObservation],
) -> list[PriceBar]:
    """
    Convert FRED observations to PriceBar format for unified storage.

    FRED data only has a single value, so we store it in the 'close' field.
    Open/high/low/volume are all None.
    """
    bars: list[PriceBar] = []
    for obs in observations:
        if obs.value is None:
            continue
        bars.append(
            PriceBar(
                symbol=obs.series_id,
                price_date=obs.observation_date,
                open=None,
                high=None,
                low=None,
                close=obs.value,
                adj_close=obs.value,
                volume=None,
            )
        )
    return bars


def ingest_fred_series(
    series_ids: Iterable[str],
    start_date: date,
    end_date: date,
    api_key: str | None = None,
) -> dict[str, int]:
    """
    Fetch FRED series and insert into daily_prices table.

    Args:
        series_ids: List of FRED series IDs
        start_date: Start date for observations
        end_date: End date for observations
        api_key: FRED API key (uses settings if not provided)

    Returns:
        Dict mapping series_id -> number of rows inserted/updated
    """
    results: dict[str, int] = {}

    observations_by_series = fetch_fred_series_batch(
        series_ids=series_ids,
        start_date=start_date,
        end_date=end_date,
        api_key=api_key,
    )

    for series_id, observations in observations_by_series.items():
        if not observations:
            results[series_id] = 0
            continue

        bars = fred_observations_to_price_bars(observations)
        try:
            inserted = insert_prices(bars, source=FRED_SOURCE)
            results[series_id] = inserted
            logger.info(
                "FRED series %s: inserted/updated %d prices",
                series_id,
                inserted,
            )
        except Exception:
            logger.exception("FRED price insertion failed for %s", series_id)
            results[series_id] = 0

    return results


def get_latest_fred_values(
    series_ids: Iterable[str],
    api_key: str | None = None,
) -> dict[str, Decimal | None]:
    """
    Get the latest value for each FRED series (convenience function).

    Fetches the last 5 days of data and returns the most recent non-null value.
    """
    today = date.today()
    start_date = today - timedelta(days=5)

    results: dict[str, Decimal | None] = {}
    observations_by_series = fetch_fred_series_batch(
        series_ids=series_ids,
        start_date=start_date,
        end_date=today,
        api_key=api_key,
    )

    for series_id, observations in observations_by_series.items():
        # Find latest non-null observation
        latest_value: Decimal | None = None
        for obs in reversed(observations):
            if obs.value is not None:
                latest_value = obs.value
                break
        results[series_id] = latest_value

    return results
