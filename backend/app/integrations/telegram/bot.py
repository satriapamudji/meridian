"""Telegram bot integration with polling/webhook abstraction.

Usage:
    # Polling (local dev):
    python -m app.integrations.telegram.bot

    # Webhook (production):
    python -m app.integrations.telegram.bot --webhook --port 8443 --url https://example.com/webhook
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, TYPE_CHECKING

from app.core.settings import get_settings
from app.integrations.telegram.commands import (
    handle_events,
    handle_help,
    handle_note,
    handle_thesis_list,
    handle_today,
)

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot with command routing and transport abstraction."""

    def __init__(self, token: str, allowed_chat_ids: list[int]) -> None:
        self.token = token
        self.allowed_chat_ids = set(allowed_chat_ids)
        self._app: Any = None

    def _is_authorized(self, chat_id: int) -> bool:
        """Check if a chat ID is authorized to use the bot."""
        # If no allowed IDs configured, allow all (dev mode)
        if not self.allowed_chat_ids:
            return True
        return chat_id in self.allowed_chat_ids

    async def _handle_unauthorized(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle unauthorized access attempts."""
        chat_id = update.effective_chat.id if update.effective_chat else None
        logger.warning(f"Unauthorized access attempt from chat_id={chat_id}")
        # Silently ignore unauthorized messages

    async def cmd_today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /today command."""
        if not update.effective_chat:
            return
        if not self._is_authorized(update.effective_chat.id):
            return

        response = handle_today()
        await update.message.reply_text(response)  # type: ignore[union-attr]

    async def cmd_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /events command."""
        if not update.effective_chat:
            return
        if not self._is_authorized(update.effective_chat.id):
            return

        response = handle_events()
        await update.message.reply_text(response)  # type: ignore[union-attr]

    async def cmd_thesis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /thesis command."""
        if not update.effective_chat:
            return
        if not self._is_authorized(update.effective_chat.id):
            return

        response = handle_thesis_list()
        await update.message.reply_text(response)  # type: ignore[union-attr]

    async def cmd_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /note command."""
        if not update.effective_chat:
            return
        if not self._is_authorized(update.effective_chat.id):
            return

        # Extract arguments after /note
        args = " ".join(context.args) if context.args else ""
        response = handle_note(args)
        await update.message.reply_text(response)  # type: ignore[union-attr]

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help and /start commands."""
        if not update.effective_chat:
            return
        if not self._is_authorized(update.effective_chat.id):
            return

        response = handle_help()
        await update.message.reply_text(response)  # type: ignore[union-attr]

    def build_application(self) -> Any:
        """Build the Telegram application with all handlers."""
        from telegram.ext import Application, CommandHandler

        builder = Application.builder().token(self.token)
        app = builder.build()

        # Register command handlers
        app.add_handler(CommandHandler("start", self.cmd_help))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("today", self.cmd_today))
        app.add_handler(CommandHandler("events", self.cmd_events))
        app.add_handler(CommandHandler("thesis", self.cmd_thesis))
        app.add_handler(CommandHandler("note", self.cmd_note))

        self._app = app
        return app

    def run_polling(self) -> None:
        """Run the bot using long polling (for local development)."""
        app = self.build_application()
        logger.info("Starting Telegram bot in polling mode...")
        app.run_polling()

    def run_webhook(self, url: str, port: int = 8443) -> None:
        """Run the bot using webhooks (for production).

        Args:
            url: The webhook URL (e.g., https://example.com/webhook)
            port: The port to listen on (default: 8443)
        """
        app = self.build_application()
        logger.info(f"Starting Telegram bot in webhook mode on port {port}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=f"{url}/webhook",
        )


def create_bot() -> TelegramBot:
    """Create a TelegramBot instance from settings."""
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "MERIDIAN_TELEGRAM_BOT_TOKEN not configured. Set it in your .env file or environment."
        )
    return TelegramBot(
        token=settings.telegram_bot_token,
        allowed_chat_ids=settings.telegram_allowed_chat_ids,
    )


def main() -> None:
    """Entry point for running the bot from command line."""
    parser = argparse.ArgumentParser(description="Run the Meridian Telegram bot")
    parser.add_argument(
        "--webhook",
        action="store_true",
        help="Use webhook mode instead of polling",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="",
        help="Webhook URL (required for webhook mode)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8443,
        help="Port for webhook listener (default: 8443)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        bot = create_bot()
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)

    if args.webhook:
        if not args.url:
            logger.error("--url is required for webhook mode")
            sys.exit(1)
        bot.run_webhook(url=args.url, port=args.port)
    else:
        bot.run_polling()


if __name__ == "__main__":
    main()
