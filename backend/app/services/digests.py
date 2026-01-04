from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Sequence

import psycopg
from psycopg.types.json import Json

from app.analysis.market_context import fetch_latest_market_context
from app.core.settings import get_settings, normalize_database_url
from app.ingestion.prices import DEFAULT_RATIO_NAME, GOLD_SYMBOL, SILVER_SYMBOL

COPPER_SYMBOL = "HG=F"
DEFAULT_TIMEZONE = "UTC"
PRIORITY_EVENT_LIMIT = 10
THESIS_LIMIT = 10

METAL_SYMBOLS = {
    GOLD_SYMBOL: "gold",
    SILVER_SYMBOL: "silver",
    COPPER_SYMBOL: "copper",
}
METAL_ORDER = ("gold", "silver", "copper")


def fetch_market_context_summary() -> dict[str, Any] | None:
    """
    Fetch the latest market context and return a summary dict for the digest.

    Returns:
        Dictionary with regimes, key_levels, ratios, and position_sizing,
        or None if no market context is available.
    """
    record = fetch_latest_market_context()
    if record is None:
        return None

    return {
        "context_date": record.context_date.isoformat(),
        "regimes": {
            "volatility": record.volatility_regime,
            "dollar": record.dollar_regime,
            "curve": record.curve_regime,
            "credit": record.credit_regime,
        },
        "key_levels": {
            "vix": record.vix_level,
            "dxy": record.dxy_level,
            "us10y": record.us10y_level,
            "us2y": record.us2y_level,
            "spread_2s10s": record.spread_2s10s,
            "gold": record.gold_level,
            "oil": record.oil_level,
            "spx": record.spx_level,
            "btc": record.btc_level,
            "hy_spread": record.hy_spread,
        },
        "ratios": {
            "gold_silver": record.gold_silver_ratio,
            "copper_gold": record.copper_gold_ratio,
            "vix_term_structure": record.vix_term_structure,
            "spy_rsp": record.spy_rsp_ratio,
        },
        "suggested_size_multiplier": record.suggested_size_multiplier,
    }


def _render_market_context_section(market_context: dict[str, Any] | None) -> list[str]:
    """Render market context section for the digest text."""
    lines: list[str] = []
    lines.append("MARKET CONTEXT")

    if market_context is None:
        lines.append("- No market context available")
        return lines

    # Regimes
    regimes = market_context.get("regimes", {})
    regime_parts = []
    if regimes.get("volatility"):
        regime_parts.append(f"Vol: {regimes['volatility'].upper()}")
    if regimes.get("dollar"):
        regime_parts.append(f"USD: {regimes['dollar'].upper()}")
    if regimes.get("curve"):
        regime_parts.append(f"Curve: {regimes['curve'].upper()}")
    if regimes.get("credit"):
        regime_parts.append(f"Credit: {regimes['credit'].upper()}")
    if regime_parts:
        lines.append(f"Regimes: {' | '.join(regime_parts)}")

    # Key levels
    key_levels = market_context.get("key_levels", {})
    level_parts = []
    if key_levels.get("vix") is not None:
        level_parts.append(f"VIX {key_levels['vix']:.1f}")
    if key_levels.get("dxy") is not None:
        level_parts.append(f"DXY {key_levels['dxy']:.1f}")
    if key_levels.get("us10y") is not None:
        level_parts.append(f"10Y {key_levels['us10y']:.2f}%")
    if key_levels.get("gold") is not None:
        level_parts.append(f"Gold ${key_levels['gold']:.0f}")
    if key_levels.get("oil") is not None:
        level_parts.append(f"Oil ${key_levels['oil']:.1f}")
    if level_parts:
        lines.append(f"Levels: {' | '.join(level_parts)}")

    # Position sizing
    multiplier = market_context.get("suggested_size_multiplier")
    if multiplier is not None:
        lines.append(f"Position Sizing: {multiplier:.0%} of normal")

    return lines


@dataclass(frozen=True)
class DailyDigest:
    digest_date: date
    window_start: datetime
    window_end: datetime
    generated_at: datetime
    priority_events: list[dict[str, Any]]
    metals_snapshot: dict[str, Any]
    economic_calendar: list[dict[str, Any]]
    active_theses: list[dict[str, Any]]
    full_digest: str
    market_context: dict[str, Any] | None = None
    timezone: str = DEFAULT_TIMEZONE

    def as_response(self) -> dict[str, Any]:
        return {
            "digest_date": self.digest_date.isoformat(),
            "timezone": self.timezone,
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "generated_at": self.generated_at.isoformat(),
            "market_context": self.market_context,
            "priority_events": self.priority_events,
            "metals_snapshot": self.metals_snapshot,
            "economic_calendar": self.economic_calendar,
            "active_theses": self.active_theses,
            "full_digest": self.full_digest,
        }


def utc_day_bounds(digest_date: date) -> tuple[datetime, datetime]:
    start = datetime(digest_date.year, digest_date.month, digest_date.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


def get_or_create_digest(digest_date: date) -> DailyDigest:
    settings = get_settings()
    database_url = normalize_database_url(settings.database_url)
    with psycopg.connect(database_url) as conn:
        cached = _load_cached_digest(conn, digest_date)
        if cached is not None:
            return cached

        window_start, window_end = utc_day_bounds(digest_date)
        priority_events = fetch_priority_events(
            conn,
            window_start,
            window_end,
            limit=PRIORITY_EVENT_LIMIT,
        )
        metals_snapshot = fetch_metals_snapshot(conn, digest_date)
        economic_calendar = fetch_economic_calendar(conn, window_start, window_end)
        active_theses = fetch_active_theses(conn, limit=THESIS_LIMIT)
        market_context = fetch_market_context_summary()
        digest = build_digest_payload(
            digest_date,
            window_start,
            window_end,
            priority_events,
            metals_snapshot,
            economic_calendar,
            active_theses,
            generated_at=datetime.now(timezone.utc),
            market_context=market_context,
        )
        _cache_digest(conn, digest)
        return digest


def build_digest_payload(
    digest_date: date,
    window_start: datetime,
    window_end: datetime,
    priority_events: Sequence[dict[str, Any]],
    metals_snapshot: dict[str, Any],
    economic_calendar: Sequence[dict[str, Any]],
    active_theses: Sequence[dict[str, Any]],
    *,
    generated_at: datetime,
    market_context: dict[str, Any] | None = None,
) -> DailyDigest:
    digest = render_digest(
        digest_date,
        priority_events,
        metals_snapshot,
        economic_calendar,
        active_theses,
        DEFAULT_TIMEZONE,
        market_context=market_context,
    )
    return DailyDigest(
        digest_date=digest_date,
        window_start=window_start,
        window_end=window_end,
        generated_at=generated_at,
        priority_events=list(priority_events),
        metals_snapshot=metals_snapshot,
        economic_calendar=list(economic_calendar),
        active_theses=list(active_theses),
        full_digest=digest,
        market_context=market_context,
    )


def render_digest(
    digest_date: date,
    priority_events: Sequence[dict[str, Any]],
    metals_snapshot: dict[str, Any],
    economic_calendar: Sequence[dict[str, Any]],
    active_theses: Sequence[dict[str, Any]],
    timezone_label: str,
    market_context: dict[str, Any] | None = None,
) -> str:
    lines: list[str] = []
    lines.append("MERIDIAN DAILY BRIEFING")
    lines.append(f"{digest_date.strftime('%A, %b %d, %Y')} ({timezone_label})")
    lines.append("")

    # Market context section at the top
    lines.extend(_render_market_context_section(market_context))
    lines.append("")

    lines.append(f"PRIORITY EVENTS ({len(priority_events)})")
    if not priority_events:
        lines.append("- None")
    else:
        for event in priority_events:
            headline = str(event.get("headline") or "untitled event")
            score = event.get("score")
            score_text = f"{score}/100" if isinstance(score, int) else "n/a"
            analysis_ready = event.get("analysis_ready")
            suffix = " [analysis ready]" if analysis_ready else ""
            lines.append(f"- {headline} ({score_text}){suffix}")

    lines.append("")
    lines.append("METALS SNAPSHOT")
    metals = metals_snapshot.get("metals") if metals_snapshot else None
    if not metals:
        lines.append("- No price data")
    else:
        for metal in METAL_ORDER:
            entry = metals.get(metal) if isinstance(metals, dict) else None
            if not entry:
                continue
            price = _format_price(entry.get("price"))
            change = _format_percent(entry.get("change_percent"))
            lines.append(f"{metal.title()}: {price} ({change})")
        ratio = metals_snapshot.get("ratio")
        if ratio:
            ratio_value = _format_ratio(ratio.get("value"))
            ratio_change = _format_percent(ratio.get("change_percent"))
            lines.append(f"G/S Ratio: {ratio_value} ({ratio_change})")

    lines.append("")
    lines.append("TODAY'S CALENDAR")
    if not economic_calendar:
        lines.append("- None")
    else:
        for event in economic_calendar:
            event_time = _format_event_time(event.get("event_date"))
            name = str(event.get("event_name") or "event")
            region = event.get("region")
            impact = event.get("impact_level")
            impact_label = str(impact).upper() if impact else "N/A"
            region_label = ""
            if region and str(region).upper() not in name.upper():
                region_label = f"{region} "
            lines.append(f"- {event_time} {region_label}{name} ({impact_label})")

    lines.append("")
    lines.append("THESIS UPDATES")
    if not active_theses:
        lines.append("- None")
    else:
        for thesis in active_theses:
            title = str(thesis.get("title") or "untitled thesis")
            status = thesis.get("status") or "unknown"
            asset = thesis.get("asset_symbol") or thesis.get("asset_type") or ""
            change = _format_percent(thesis.get("price_change_percent"))
            suffix_parts = []
            if asset:
                suffix_parts.append(str(asset))
            if change != "n/a":
                suffix_parts.append(change)
            suffix = f" {' '.join(suffix_parts)}" if suffix_parts else ""
            lines.append(f"- {title} ({status}){suffix}")

    return "\n".join(lines)


def fetch_priority_events(
    conn: psycopg.Connection,
    start: datetime,
    end: datetime,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    query = """
        SELECT id,
               source,
               headline,
               published_at,
               significance_score,
               raw_facts,
               metal_impacts,
               historical_precedent,
               counter_case,
               crypto_transmission,
               created_at
        FROM macro_events
        WHERE priority_flag = true
          AND (
            (published_at >= %(start)s AND published_at < %(end)s)
            OR (published_at IS NULL AND created_at >= %(start)s AND created_at < %(end)s)
          )
        ORDER BY significance_score DESC NULLS LAST,
                 published_at DESC NULLS LAST,
                 created_at DESC,
                 id DESC
        LIMIT %(limit)s
    """
    rows = conn.execute(query, {"start": start, "end": end, "limit": limit}).fetchall()
    results: list[dict[str, Any]] = []
    for row in rows:
        published_at = row[3] or row[10]
        analysis_ready = any(field is not None for field in row[5:10])
        results.append(
            {
                "id": str(row[0]),
                "source": row[1],
                "headline": row[2],
                "published_at": published_at.isoformat() if published_at else None,
                "score": row[4] if isinstance(row[4], int) else None,
                "analysis_ready": analysis_ready,
            }
        )
    return results


def fetch_metals_snapshot(conn: psycopg.Connection, as_of_date: date) -> dict[str, Any]:
    symbols = list(METAL_SYMBOLS.keys())
    query = """
        SELECT symbol,
               price_date,
               close,
               rn
        FROM (
            SELECT symbol,
                   price_date,
                   close,
                   ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY price_date DESC) AS rn
            FROM daily_prices
            WHERE symbol = ANY(%(symbols)s)
              AND price_date <= %(as_of)s
              AND close IS NOT NULL
        ) ranked
        WHERE rn <= 2
        ORDER BY symbol, price_date DESC
    """
    rows = conn.execute(query, {"symbols": symbols, "as_of": as_of_date}).fetchall()
    history: dict[str, list[tuple[date, Decimal]]] = {symbol: [] for symbol in symbols}
    for row in rows:
        history[row[0]].append((row[1], row[2]))

    metals: dict[str, dict[str, Any]] = {}
    for symbol, metal in METAL_SYMBOLS.items():
        entries = history.get(symbol) or []
        latest = entries[0] if entries else None
        previous = entries[1] if len(entries) > 1 else None
        latest_value = latest[1] if latest else None
        previous_value = previous[1] if previous else None
        metals[metal] = {
            "symbol": symbol,
            "price": _round_decimal(latest_value, 2),
            "change_percent": _change_percent(latest_value, previous_value),
            "as_of": latest[0].isoformat() if latest else None,
        }

    ratio = fetch_ratio_snapshot(conn, as_of_date)
    return {"metals": metals, "ratio": ratio}


def fetch_ratio_snapshot(conn: psycopg.Connection, as_of_date: date) -> dict[str, Any]:
    query = """
        SELECT ratio_name,
               price_date,
               value,
               rn
        FROM (
            SELECT ratio_name,
                   price_date,
                   value,
                   ROW_NUMBER() OVER (PARTITION BY ratio_name ORDER BY price_date DESC) AS rn
            FROM price_ratios
            WHERE ratio_name = %(ratio_name)s
              AND price_date <= %(as_of)s
        ) ranked
        WHERE rn <= 2
        ORDER BY price_date DESC
    """
    rows = conn.execute(
        query,
        {"ratio_name": DEFAULT_RATIO_NAME, "as_of": as_of_date},
    ).fetchall()
    latest = rows[0] if rows else None
    previous = rows[1] if len(rows) > 1 else None
    latest_value = latest[2] if latest else None
    previous_value = previous[2] if previous else None
    return {
        "name": DEFAULT_RATIO_NAME,
        "value": _round_decimal(latest_value, 2),
        "change_percent": _change_percent(latest_value, previous_value),
        "as_of": latest[1].isoformat() if latest else None,
    }


def fetch_economic_calendar(
    conn: psycopg.Connection,
    start: datetime,
    end: datetime,
) -> list[dict[str, Any]]:
    query = """
        SELECT event_name,
               event_date,
               region,
               impact_level,
               expected_value,
               actual_value,
               previous_value,
               surprise_direction,
               surprise_magnitude
        FROM economic_events
        WHERE event_date >= %(start)s
          AND event_date < %(end)s
          AND impact_level = 'high'
        ORDER BY event_date ASC, event_name ASC
    """
    rows = conn.execute(query, {"start": start, "end": end}).fetchall()
    events: list[dict[str, Any]] = []
    for row in rows:
        event_date = row[1]
        events.append(
            {
                "event_name": row[0],
                "event_date": event_date.isoformat() if event_date else None,
                "region": row[2],
                "impact_level": row[3],
                "expected_value": row[4],
                "actual_value": row[5],
                "previous_value": row[6],
                "surprise_direction": row[7],
                "surprise_magnitude": _round_decimal(row[8], 2),
            }
        )
    return events


def fetch_active_theses(
    conn: psycopg.Connection,
    *,
    limit: int,
) -> list[dict[str, Any]]:
    query = """
        SELECT id,
               title,
               asset_type,
               asset_symbol,
               status,
               price_change_percent,
               updated_at,
               created_at
        FROM theses
        WHERE status IS NULL
           OR status NOT IN ('closed', 'dismissed', 'archived')
        ORDER BY updated_at DESC NULLS LAST, created_at DESC, id DESC
        LIMIT %(limit)s
    """
    rows = conn.execute(query, {"limit": limit}).fetchall()
    theses: list[dict[str, Any]] = []
    for row in rows:
        updated_at = row[6] or row[7]
        theses.append(
            {
                "id": str(row[0]),
                "title": row[1],
                "asset_type": row[2],
                "asset_symbol": row[3],
                "status": row[4],
                "price_change_percent": _round_decimal(row[5], 2),
                "updated_at": updated_at.isoformat() if updated_at else None,
            }
        )
    return theses


def _load_cached_digest(
    conn: psycopg.Connection,
    digest_date: date,
) -> DailyDigest | None:
    query = """
        SELECT digest_date,
               created_at,
               priority_events,
               metals_snapshot,
               economic_calendar,
               active_theses,
               full_digest
        FROM daily_digests
        WHERE digest_date = %(digest_date)s
    """
    row = conn.execute(query, {"digest_date": digest_date}).fetchone()
    if row is None:
        return None
    window_start, window_end = utc_day_bounds(row[0])
    return DailyDigest(
        digest_date=row[0],
        window_start=window_start,
        window_end=window_end,
        generated_at=row[1],
        priority_events=row[2] or [],
        metals_snapshot=row[3] or {},
        economic_calendar=row[4] or [],
        active_theses=row[5] or [],
        full_digest=row[6] or "",
    )


def _cache_digest(conn: psycopg.Connection, digest: DailyDigest) -> None:
    query = """
        INSERT INTO daily_digests (
            digest_date,
            priority_events,
            metals_snapshot,
            economic_calendar,
            active_theses,
            full_digest
        )
        VALUES (
            %(digest_date)s,
            %(priority_events)s,
            %(metals_snapshot)s,
            %(economic_calendar)s,
            %(active_theses)s,
            %(full_digest)s
        )
        ON CONFLICT (digest_date)
        DO UPDATE SET
            priority_events = EXCLUDED.priority_events,
            metals_snapshot = EXCLUDED.metals_snapshot,
            economic_calendar = EXCLUDED.economic_calendar,
            active_theses = EXCLUDED.active_theses,
            full_digest = EXCLUDED.full_digest
    """
    conn.execute(
        query,
        {
            "digest_date": digest.digest_date,
            "priority_events": Json(digest.priority_events),
            "metals_snapshot": Json(digest.metals_snapshot),
            "economic_calendar": Json(digest.economic_calendar),
            "active_theses": Json(digest.active_theses),
            "full_digest": digest.full_digest,
        },
    )


def _round_decimal(value: Decimal | None, places: int) -> float | None:
    if value is None:
        return None
    quant = Decimal("1").scaleb(-places)
    return float(value.quantize(quant))


def _change_percent(latest: Decimal | None, previous: Decimal | None) -> float | None:
    if latest is None or previous is None or previous == 0:
        return None
    percent = (latest - previous) / previous * Decimal("100")
    return _round_decimal(percent, 2)


def _format_price(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:.2f}"


def _format_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def _format_event_time(value: str | None) -> str:
    if not value:
        return "??:??"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return "??:??"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%H:%M")
