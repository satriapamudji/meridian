from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os

_DEFAULT_DATABASE_URL = "postgresql://meridian:meridian@localhost:5432/meridian"
_DEFAULT_REDIS_URL = "redis://localhost:6379/0"


@dataclass(frozen=True)
class Settings:
    env: str
    database_url: str
    redis_url: str
    log_level: str


def _get_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value else default


def normalize_database_url(url: str) -> str:
    return url.replace("+psycopg", "")


@lru_cache
def get_settings() -> Settings:
    return Settings(
        env=_get_env("MERIDIAN_ENV", "local"),
        database_url=_get_env("MERIDIAN_DATABASE_URL", _DEFAULT_DATABASE_URL),
        redis_url=_get_env("MERIDIAN_REDIS_URL", _DEFAULT_REDIS_URL),
        log_level=_get_env("MERIDIAN_LOG_LEVEL", "INFO"),
    )
