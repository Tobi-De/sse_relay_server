import psycopg
import json

from .config import get_database_params


def postgres_notify(channel: str, sse_payload: dict):
    connection = psycopg.Connection.connect(
        **get_database_params(),
        autocommit=True,
    )
    with connection.cursor() as cursor:
        cursor.execute(f"NOTIFY {channel}, '{json.dumps(sse_payload)}'")
