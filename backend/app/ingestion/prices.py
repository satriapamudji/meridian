from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
import logging
import math
from typing import Iterable
import urllib.parse
import urllib.request

import psycopg

from app.core.settings import get_settings, normalize_database_url

CORE_SYMBOLS = ("GC=F", "SI=F", "HG=F")
OPTIONAL_SYMBOLS = ("GLD", "SLV", "COPX", "NEM", "GOLD", "FCX")
DEFAULT_LOOKBACK_DAYS = 10
DEFAULT_SOURCE = "yahoo"
GOLD_SYMBOL = "GC=F"
SILVER_SYMBOL = "SI=F"
DEFAULT_RATIO_NAME = "gold_silver"

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
