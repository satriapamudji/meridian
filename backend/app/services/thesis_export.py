from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Mapping, Sequence


def render_thesis_markdown(thesis: Mapping[str, Any]) -> str:
    title = _string_value(thesis.get("title")) or "Untitled"
    created_at = _format_date(thesis.get("created_at"))
    status = _string_value(thesis.get("status")) or "watching"
    asset_type = _string_value(thesis.get("asset_type")) or "n/a"
    asset_symbol = _string_value(thesis.get("asset_symbol"))
    asset_label = f"{asset_type} / {asset_symbol}" if asset_symbol else asset_type

    core_thesis = _string_value(thesis.get("core_thesis")) or "n/a"
    trigger_event = _string_value(thesis.get("trigger_event")) or "n/a"
    historical_precedent = _string_value(thesis.get("historical_precedent")) or "n/a"

    bull_case = _format_list(thesis.get("bull_case"))
    bear_case = _format_list(thesis.get("bear_case"))

    entry_consideration = _string_value(thesis.get("entry_consideration")) or "n/a"
    target = _string_value(thesis.get("target")) or "n/a"
    invalidation = _string_value(thesis.get("invalidation")) or "n/a"

    vehicle = _string_value(thesis.get("vehicle")) or "n/a"
    position_size = _string_value(thesis.get("position_size")) or "n/a"
    entry_date = _format_date(thesis.get("entry_date"))
    entry_price = _format_number(thesis.get("entry_price"))

    updates = thesis.get("updates") or []
    updates_table = _format_updates(updates)

    lines = [
        f"# Thesis: {title}",
        "",
        f"**Created:** {created_at}",
        f"**Status:** {status}",
        f"**Metal/Asset:** {asset_label}",
        "",
        "## Core Thesis",
        core_thesis,
        "",
        "## Trigger Event",
        trigger_event,
        "",
        "## Historical Precedent",
        historical_precedent,
        "",
        "## Bull Case",
        bull_case,
        "",
        "## Bear Case / Counter-Case",
        bear_case,
        "",
        "## Key Levels",
        f"- Entry consideration: {entry_consideration}",
        f"- Target: {target}",
        f"- Invalidation: {invalidation}",
        "",
        "## Position",
        f"- Vehicle: {vehicle}",
        f"- Size: {position_size}",
        f"- Entry date: {entry_date}",
        f"- Entry price: {entry_price}",
        "",
        "## Updates Log",
        updates_table,
        "",
        "## Outcome",
        "n/a",
    ]
    return "\n".join(lines)


def _format_list(value: Any) -> str:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        items = [str(item).strip() for item in value if isinstance(item, str) and item.strip()]
        if items:
            return "\n".join(f"- {item}" for item in items)
    return "- n/a"


def _string_value(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _format_number(value: Any) -> str:
    if isinstance(value, Decimal):
        return format(value, "f").rstrip("0").rstrip(".") or "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "n/a"


def _format_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "n/a"


def _format_updates(updates: Any) -> str:
    rows = ["| Date | Note | Price |", "|------|------|-------|"]
    if not isinstance(updates, list) or not updates:
        rows.append("| n/a | n/a | n/a |")
        return "\n".join(rows)

    for entry in updates:
        if not isinstance(entry, dict):
            continue
        date_value = _format_date(entry.get("date"))
        note_value = _string_value(entry.get("note")) or "n/a"
        price_value = _format_number(entry.get("price"))
        rows.append(f"| {date_value} | {note_value} | {price_value} |")
    if len(rows) == 2:
        rows.append("| n/a | n/a | n/a |")
    return "\n".join(rows)
