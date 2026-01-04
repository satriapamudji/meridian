"""Telegram message formatting utilities.

Handles escaping for MarkdownV2 and plain text message rendering.
"""

from __future__ import annotations

from typing import Any

# Characters that need escaping in Telegram MarkdownV2
MARKDOWN_V2_ESCAPE_CHARS = r"_*[]()~`>#+-=|{}.!"


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2 format."""
    result = []
    for char in text:
        if char in MARKDOWN_V2_ESCAPE_CHARS:
            result.append("\\")
        result.append(char)
    return "".join(result)


def format_digest_for_telegram(digest_text: str) -> str:
    """Format the full digest text for Telegram.

    The digest is already rendered as plain text by the digest service.
    For Telegram, we use it as-is (plain text mode) to avoid escaping complexity.
    """
    return digest_text


def format_events_list(events: list[dict[str, Any]]) -> str:
    """Format a list of macro events for Telegram display."""
    if not events:
        return "No priority events found."

    lines = [f"*Priority Events ({len(events)})*\n"]
    for event in events:
        headline = str(event.get("headline") or "untitled event")
        score = event.get("significance_score") or event.get("score")
        score_text = f"{score}/100" if isinstance(score, int) else "n/a"
        priority = event.get("priority_flag", False)
        marker = "[P] " if priority else ""
        lines.append(f"- {marker}{headline} ({score_text})")

    return "\n".join(lines)


def format_theses_list(theses: list[dict[str, Any]]) -> str:
    """Format a list of theses for Telegram display."""
    if not theses:
        return "No active theses found."

    lines = ["*Active Theses*\n"]
    for thesis in theses:
        thesis_id = str(thesis.get("id", ""))[:8]
        title = str(thesis.get("title") or "untitled")
        status = thesis.get("status") or "unknown"
        asset = thesis.get("asset_symbol") or thesis.get("asset_type") or ""
        suffix = f" [{asset}]" if asset else ""
        lines.append(f"- `{thesis_id}` {title} ({status}){suffix}")

    return "\n".join(lines)


def format_note_confirmation(thesis_id: str, note: str) -> str:
    """Format confirmation message after adding a note."""
    short_id = thesis_id[:8]
    note_preview = note[:50] + "..." if len(note) > 50 else note
    return f'Note added to thesis `{short_id}`:\n"{note_preview}"'


def format_help_message() -> str:
    """Format the help message showing available commands."""
    return """*Meridian Bot Commands*

/today - Daily briefing with market context, events, metals, calendar, and theses
/events - List recent priority macro events with significance scores
/thesis - List active theses
/note <thesis_id> <text> - Add an update note to a thesis
/help - Show this help message

*Examples*
`/note abc12345 Gold breaking above resistance, thesis on track`
"""
