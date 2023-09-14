from dotenv import load_dotenv
import os
import dj_database_url

load_dotenv()


class ConfigurationError(Exception):
    pass


def get_allowed_origins() -> list[str]:
    origins = os.getenv("SSE_ALLOWED_ORIGINS")
    return [] if origins is None else [v.strip() for v in origins.split(",")]


def get_debug_value() -> bool:
    return os.getenv("SSE_RELAY_SERVER_DEBUG") == "True"


def get_database_params() -> dict:
    if not os.getenv("DATABASE_URL"):
        raise ConfigurationError("DATABASE_URL is not set")
    parsed_params = dj_database_url.config()
    if parsed_params["ENGINE"] not in [
        "django.db.backends.postgresql_psycopg2",
        "django.db.backends.postgresql",
    ]:
        raise ConfigurationError("A postgresql database is require")
    return {
        "client_encoding": "UTF8",
        "dbname": parsed_params["NAME"],
        "user": parsed_params["USER"],
        "password": parsed_params["PASSWORD"],
        "host": parsed_params["HOST"],
    }
