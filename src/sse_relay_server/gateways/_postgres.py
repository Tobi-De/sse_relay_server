import json
from typing import AsyncGenerator

import dj_database_url
import psycopg
from loguru import logger
from sse_starlette import ServerSentEvent

from ..config import ConfigurationError


class PostgresGateway:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url
        parsed_params = dj_database_url.parse(postgres_url)
        if parsed_params["ENGINE"] not in [
            "django.db.backends.postgresql_psycopg2",
            "django.db.backends.postgresql",
        ]:
            raise ConfigurationError("A postgresql database is require")
        self.db_params = {
            "client_encoding": "UTF8",
            "dbname": parsed_params["NAME"],
            "user": parsed_params["USER"],
            "password": parsed_params["PASSWORD"],
            "host": parsed_params["HOST"],
        }

    async def listen(self, channel: str) -> AsyncGenerator[ServerSentEvent, None]:
        connection = await psycopg.AsyncConnection.connect(
            **self.db_params,
            autocommit=True,
        )

        async with connection.cursor() as cursor:
            await cursor.execute(f"LISTEN {channel}")
            generator = connection.notifies()
            async for notify_message in generator:
                payload = json.loads(notify_message.payload)
                logger.debug(f"Received from {channel}: {payload}")
                yield ServerSentEvent(**payload)

    def notify(self, channel: str, sse_payload: dict) -> None:
        connection = psycopg.Connection.connect(
            **self.db_params,
            autocommit=True,
        )
        with connection.cursor() as cursor:
            cursor.execute(f"NOTIFY {channel}, '{json.dumps(sse_payload)}'")
