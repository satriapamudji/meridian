from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

_DEFAULT_DATABASE_URL = "postgresql://meridian:meridian@localhost:5432/meridian"
_DEFAULT_REDIS_URL = "redis://localhost:6379/0"
_ENV_LOADED = False


@dataclass(frozen=True)
class Settings:
    env: str
    database_url: str
    redis_url: str
    log_level: str
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str
    openrouter_app_url: str
    openrouter_app_title: str
    fred_api_key: str
    telegram_bot_token: str
    telegram_allowed_chat_ids: list[int]
    # Scheduler settings
    scheduler_timezone: str
    scheduler_rss_interval_minutes: int
    scheduler_calendar_interval_minutes: int
    scheduler_fed_interval_minutes: int
    scheduler_prices_interval_minutes: int
    scheduler_digest_hour: int
    scheduler_digest_minute: int


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def _load_dotenv() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True

    backend_dir = Path(__file__).resolve().parents[2]
    candidate_paths = [backend_dir / ".env", backend_dir.parent / ".env"]

    for path in candidate_paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("export "):
                stripped = stripped[7:].strip()
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value and value[0] in ("'", '"') and value[-1] == value[0]:
                value = value[1:-1]
            os.environ.setdefault(key, value)


def normalize_database_url(url: str) -> str:
    return url.replace("+psycopg", "")


def _parse_chat_ids(value: str) -> list[int]:
    """Parse comma-separated chat IDs into a list of integers."""
    if not value.strip():
        return []
    result = []
    for item in value.split(","):
        item = item.strip()
        if item:
            try:
                result.append(int(item))
            except ValueError:
                pass
    return result


@lru_cache
def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        env=_get_env("MERIDIAN_ENV", "local"),
        database_url=_get_env("MERIDIAN_DATABASE_URL", _DEFAULT_DATABASE_URL),
        redis_url=_get_env("MERIDIAN_REDIS_URL", _DEFAULT_REDIS_URL),
        log_level=_get_env("MERIDIAN_LOG_LEVEL", "INFO"),
        openrouter_api_key=_get_env("MERIDIAN_OPENROUTER_API_KEY", ""),
        openrouter_model=_get_env("MERIDIAN_OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        openrouter_base_url=_get_env(
            "MERIDIAN_OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1/chat/completions",
        ),
        openrouter_app_url=_get_env("MERIDIAN_OPENROUTER_APP_URL", ""),
        openrouter_app_title=_get_env("MERIDIAN_OPENROUTER_APP_TITLE", "Meridian"),
        fred_api_key=_get_env("MERIDIAN_FRED_API_KEY", ""),
        telegram_bot_token=_get_env("MERIDIAN_TELEGRAM_BOT_TOKEN", ""),
        telegram_allowed_chat_ids=_parse_chat_ids(
            _get_env("MERIDIAN_TELEGRAM_ALLOWED_CHAT_IDS", "")
        ),
        # Scheduler settings with sensible defaults
        scheduler_timezone=_get_env("MERIDIAN_SCHEDULER_TIMEZONE", "UTC"),
        scheduler_rss_interval_minutes=int(_get_env("MERIDIAN_SCHEDULER_RSS_INTERVAL", "10")),
        scheduler_calendar_interval_minutes=int(
            _get_env("MERIDIAN_SCHEDULER_CALENDAR_INTERVAL", "360")
        ),
        scheduler_fed_interval_minutes=int(_get_env("MERIDIAN_SCHEDULER_FED_INTERVAL", "60")),
        scheduler_prices_interval_minutes=int(
            _get_env("MERIDIAN_SCHEDULER_PRICES_INTERVAL", "1440")
        ),
        scheduler_digest_hour=int(_get_env("MERIDIAN_SCHEDULER_DIGEST_HOUR", "6")),
        scheduler_digest_minute=int(_get_env("MERIDIAN_SCHEDULER_DIGEST_MINUTE", "0")),
    )
