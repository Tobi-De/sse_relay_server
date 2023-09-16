from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class ConfigurationError(Exception):
    pass


def get_allowed_origins() -> list[str]:
    origins = os.getenv("ALLOWED_ORIGINS")
    return [] if origins is None else [v.strip() for v in origins.split(",")]


def get_debug_value() -> bool:
    return os.getenv("RELAY_SERVER_DEBUG") == "True"


def get_postgres_url() -> str | None:
    return os.getenv("DATABASE_URL")


def get_redis_url() -> str | None:
    return os.getenv("REDIS_URL")
