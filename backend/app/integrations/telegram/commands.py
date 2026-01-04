"""Telegram command handlers.

Each handler takes an Update and Context and returns a response message.
"""

from __future__ import annotations

from datetime import date
import uuid

from app.api.events import EventRepository
from app.integrations.telegram.formatting import (
    format_digest_for_telegram,
    format_events_list,
    format_help_message,
    format_note_confirmation,
    format_theses_list,
)
from app.services.digests import get_or_create_digest


def handle_today() -> str:
    """Handle /today command - returns daily briefing."""
    try:
        today = date.today()
        digest = get_or_create_digest(today)
        return format_digest_for_telegram(digest.full_digest)
    except Exception as exc:
        return f"Error generating daily digest: {exc}"


def handle_events(limit: int = 10) -> str:
    """Handle /events command - returns recent priority events."""
    try:
        repo = EventRepository()
        events = repo.list_events(
            priority_only=True,
            score_min=None,
            score_max=None,
            status=None,
            start_date=None,
            end_date=None,
            limit=limit,
        )
        # Convert MacroEventRow to dict for formatting
        event_dicts = [
            {
                "id": str(e.id),
                "headline": e.headline,
                "significance_score": e.significance_score,
                "priority_flag": e.priority_flag,
                "published_at": e.published_at.isoformat() if e.published_at else None,
            }
            for e in events
        ]
        return format_events_list(event_dicts)
    except Exception as exc:
        return f"Error fetching events: {exc}"


def handle_thesis_list() -> str:
    """Handle /thesis command - returns active theses."""
    try:
        from app.api.theses import list_theses

        theses = list_theses(status=None)
        # Filter to active/watching only and convert to dict
        thesis_dicts = [
            {
                "id": str(t.id),
                "title": t.title,
                "status": t.status,
                "asset_symbol": t.asset_symbol,
                "asset_type": t.asset_type,
            }
            for t in theses
            if t.status not in ("closed", "dismissed", "archived")
        ]
        return format_theses_list(thesis_dicts)
    except Exception as exc:
        return f"Error fetching theses: {exc}"


def handle_note(args: str) -> str:
    """Handle /note command - adds update to a thesis.

    Args:
        args: The command arguments as a single string.
              Expected format: "<thesis_id> <note text>"
    """
    if not args or not args.strip():
        return (
            "Usage: /note <thesis_id> <note text>\nExample: /note abc12345 Gold breaking resistance"
        )

    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        return (
            "Usage: /note <thesis_id> <note text>\nPlease provide both a thesis ID and note text."
        )

    thesis_id_input, note_text = parts

    # Validate thesis ID format
    try:
        # Try to find thesis by partial or full UUID
        thesis_id = _resolve_thesis_id(thesis_id_input)
    except ValueError as e:
        return str(e)

    if not note_text.strip():
        return "Note text cannot be empty."

    try:
        from app.api.theses import ThesisUpdateEntry, add_thesis_update

        payload = ThesisUpdateEntry(note=note_text.strip())
        add_thesis_update(thesis_id, payload)
        return format_note_confirmation(str(thesis_id), note_text.strip())
    except Exception as exc:
        return f"Error adding note: {exc}"


def _resolve_thesis_id(input_id: str) -> uuid.UUID:
    """Resolve a thesis ID from partial or full UUID input.

    Args:
        input_id: Partial (8+ chars) or full UUID string

    Returns:
        uuid.UUID of the matching thesis

    Raises:
        ValueError: If thesis not found or ID is ambiguous
    """
    from app.api.theses import list_theses

    input_clean = input_id.strip().lower()

    # Try exact UUID first
    try:
        exact_id = uuid.UUID(input_clean)
        # Verify it exists
        theses = list_theses(status=None)
        for t in theses:
            if t.id == exact_id:
                return exact_id
        raise ValueError(f"Thesis not found: {input_clean}")
    except ValueError:
        pass

    # Try partial match (prefix)
    if len(input_clean) < 8:
        raise ValueError("Thesis ID must be at least 8 characters.")

    theses = list_theses(status=None)
    matches = [t for t in theses if str(t.id).lower().startswith(input_clean)]

    if not matches:
        raise ValueError(f"No thesis found matching: {input_clean}")
    if len(matches) > 1:
        ids = [str(t.id)[:8] for t in matches[:3]]
        raise ValueError(f"Ambiguous ID. Matches: {', '.join(ids)}...")

    return matches[0].id


def handle_help() -> str:
    """Handle /help command - returns available commands."""
    return format_help_message()
