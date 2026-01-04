"""Tests for Telegram bot integration."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import uuid

from app.integrations.telegram.formatting import (
    escape_markdown_v2,
    format_digest_for_telegram,
    format_events_list,
    format_help_message,
    format_note_confirmation,
    format_theses_list,
)
from app.integrations.telegram.commands import (
    handle_events,
    handle_help,
    handle_note,
    handle_thesis_list,
    handle_today,
)


# ============================================================================
# Formatting Tests
# ============================================================================


def test_escape_markdown_v2_escapes_special_chars() -> None:
    text = "Hello *world* [test] (example)"
    result = escape_markdown_v2(text)
    assert result == r"Hello \*world\* \[test\] \(example\)"


def test_escape_markdown_v2_handles_empty_string() -> None:
    assert escape_markdown_v2("") == ""


def test_escape_markdown_v2_no_special_chars() -> None:
    text = "plain text"
    assert escape_markdown_v2(text) == "plain text"


def test_format_digest_for_telegram_returns_text() -> None:
    digest_text = "MERIDIAN DAILY BRIEFING\nSome content here"
    result = format_digest_for_telegram(digest_text)
    assert result == digest_text


def test_format_events_list_with_events() -> None:
    events = [
        {
            "id": "event-1",
            "headline": "Fed signals rate cuts",
            "significance_score": 72,
            "priority_flag": True,
        },
        {
            "id": "event-2",
            "headline": "Oil prices surge",
            "significance_score": 65,
            "priority_flag": False,
        },
    ]
    result = format_events_list(events)
    assert "PRIORITY EVENTS (2)" in result
    assert "[P] Fed signals rate cuts (72/100)" in result
    assert "- Oil prices surge (65/100)" in result


def test_format_events_list_empty() -> None:
    result = format_events_list([])
    assert result == "No priority events found."


def test_format_events_list_handles_missing_score() -> None:
    events = [{"id": "event-1", "headline": "Test event", "priority_flag": False}]
    result = format_events_list(events)
    assert "(n/a)" in result


def test_format_theses_list_with_theses() -> None:
    theses = [
        {
            "id": "12345678-1234-1234-1234-123456789abc",
            "title": "Silver breakout thesis",
            "status": "watching",
            "asset_symbol": "SLV",
        },
        {
            "id": "abcdefab-abcd-abcd-abcd-abcdefabcdef",
            "title": "Gold accumulation",
            "status": "active",
            "asset_type": "metal",
        },
    ]
    result = format_theses_list(theses)
    assert "ACTIVE THESES" in result
    assert "12345678: Silver breakout thesis (watching) [SLV]" in result
    assert "abcdefab: Gold accumulation (active) [metal]" in result


def test_format_theses_list_empty() -> None:
    result = format_theses_list([])
    assert result == "No active theses found."


def test_format_note_confirmation() -> None:
    result = format_note_confirmation(
        "12345678-1234-1234-1234-123456789abc",
        "Breaking above resistance",
    )
    assert "12345678" in result
    assert "Breaking above resistance" in result


def test_format_note_confirmation_truncates_long_note() -> None:
    long_note = "A" * 100
    result = format_note_confirmation("12345678", long_note)
    assert "..." in result
    assert len(result) < 200


def test_format_help_message() -> None:
    result = format_help_message()
    assert "/today" in result
    assert "/events" in result
    assert "/thesis" in result
    assert "/note" in result
    assert "/help" in result


# ============================================================================
# Command Handler Tests (with mocks)
# ============================================================================


@patch("app.integrations.telegram.commands.get_or_create_digest")
def test_handle_today_returns_digest(mock_get_digest: MagicMock) -> None:
    mock_digest = MagicMock()
    mock_digest.full_digest = "MERIDIAN DAILY BRIEFING\nTest content"
    mock_get_digest.return_value = mock_digest

    result = handle_today()
    assert "MERIDIAN DAILY BRIEFING" in result
    assert mock_get_digest.called


@patch("app.integrations.telegram.commands.get_or_create_digest")
def test_handle_today_handles_error(mock_get_digest: MagicMock) -> None:
    mock_get_digest.side_effect = Exception("Database error")
    result = handle_today()
    assert "Error generating daily digest" in result


@patch("app.integrations.telegram.commands.EventRepository")
def test_handle_events_returns_formatted_list(mock_repo_class: MagicMock) -> None:
    mock_repo = MagicMock()
    mock_event = MagicMock()
    mock_event.id = uuid.uuid4()
    mock_event.headline = "Fed rate decision"
    mock_event.significance_score = 75
    mock_event.priority_flag = True
    mock_event.published_at = datetime.now(timezone.utc)
    mock_repo.list_events.return_value = [mock_event]
    mock_repo_class.return_value = mock_repo

    result = handle_events()
    assert "PRIORITY EVENTS" in result
    assert "Fed rate decision" in result


@patch("app.integrations.telegram.commands.EventRepository")
def test_handle_events_handles_error(mock_repo_class: MagicMock) -> None:
    mock_repo_class.side_effect = Exception("Connection failed")
    result = handle_events()
    assert "Error fetching events" in result


@patch("app.api.theses.list_theses")
def test_handle_thesis_list_returns_formatted_list(mock_list: MagicMock) -> None:
    mock_thesis = MagicMock()
    mock_thesis.id = uuid.uuid4()
    mock_thesis.title = "Silver mean reversion"
    mock_thesis.status = "watching"
    mock_thesis.asset_symbol = "SLV"
    mock_thesis.asset_type = "metal"
    mock_list.return_value = [mock_thesis]

    result = handle_thesis_list()
    assert "ACTIVE THESES" in result
    assert "Silver mean reversion" in result


@patch("app.api.theses.list_theses")
def test_handle_thesis_list_filters_closed(mock_list: MagicMock) -> None:
    mock_active = MagicMock()
    mock_active.id = uuid.uuid4()
    mock_active.title = "Active thesis"
    mock_active.status = "watching"
    mock_active.asset_symbol = None
    mock_active.asset_type = None

    mock_closed = MagicMock()
    mock_closed.id = uuid.uuid4()
    mock_closed.title = "Closed thesis"
    mock_closed.status = "closed"
    mock_closed.asset_symbol = None
    mock_closed.asset_type = None

    mock_list.return_value = [mock_active, mock_closed]

    result = handle_thesis_list()
    assert "Active thesis" in result
    assert "Closed thesis" not in result


def test_handle_note_no_args() -> None:
    result = handle_note("")
    assert "Usage: /note" in result


def test_handle_note_missing_text() -> None:
    result = handle_note("abc12345")
    assert "Usage: /note" in result


def test_handle_note_short_id() -> None:
    result = handle_note("abc Note text")
    assert "at least 8 characters" in result


@patch("app.api.theses.list_theses")
def test_handle_note_thesis_not_found(mock_list: MagicMock) -> None:
    mock_list.return_value = []
    result = handle_note("12345678 Some note text")
    assert "No thesis found" in result


@patch("app.api.theses.list_theses")
@patch("app.api.theses.add_thesis_update")
def test_handle_note_success(
    mock_add_update: MagicMock,
    mock_list: MagicMock,
) -> None:
    thesis_id = uuid.UUID("12345678-1234-1234-1234-123456789abc")
    mock_thesis = MagicMock()
    mock_thesis.id = thesis_id
    mock_thesis.title = "Test thesis"
    mock_thesis.status = "watching"
    mock_list.return_value = [mock_thesis]
    mock_add_update.return_value = mock_thesis

    result = handle_note("12345678 Breaking above resistance")
    assert "Note added" in result
    assert "12345678" in result
    mock_add_update.assert_called_once()


def test_handle_help() -> None:
    result = handle_help()
    assert "/today" in result
    assert "/help" in result


# ============================================================================
# Bot Authorization Tests
# ============================================================================


def test_bot_authorization_allows_configured_chat_id() -> None:
    from app.integrations.telegram.bot import TelegramBot

    bot = TelegramBot(token="test_token", allowed_chat_ids=[12345, 67890])
    assert bot._is_authorized(12345) is True
    assert bot._is_authorized(67890) is True
    assert bot._is_authorized(99999) is False


def test_bot_authorization_allows_all_when_empty() -> None:
    from app.integrations.telegram.bot import TelegramBot

    bot = TelegramBot(token="test_token", allowed_chat_ids=[])
    assert bot._is_authorized(12345) is True
    assert bot._is_authorized(99999) is True


# ============================================================================
# Settings Tests
# ============================================================================


def test_parse_chat_ids_parses_comma_separated() -> None:
    from app.core.settings import _parse_chat_ids

    result = _parse_chat_ids("123,456,789")
    assert result == [123, 456, 789]


def test_parse_chat_ids_handles_empty_string() -> None:
    from app.core.settings import _parse_chat_ids

    result = _parse_chat_ids("")
    assert result == []


def test_parse_chat_ids_handles_whitespace() -> None:
    from app.core.settings import _parse_chat_ids

    result = _parse_chat_ids(" 123 , 456 , 789 ")
    assert result == [123, 456, 789]


def test_parse_chat_ids_skips_invalid() -> None:
    from app.core.settings import _parse_chat_ids

    result = _parse_chat_ids("123,invalid,456")
    assert result == [123, 456]
