import json
from typing import AsyncGenerator

import dj_database_url
import psycopg
import structlog
from sse_starlette import ServerSentEvent

from ..config import ConfigurationError

logger = structlog.stdlib.get_logger("brokers.postgres")


class PostgresBroker:
    def __init__(self, postgres_url: str) -> None:
        self.postgres_url = postgres_url
        parsed_params = dj_database_url.parse(postgres_url)
        if parsed_params["ENGINE"] not in [
            "django.db.backends.postgresql_psycopg2",
            "django.db.backends.postgresql",
        ]:
            raise ConfigurationError("Only PostgreSQL is supported")
        self.db_params = {
            "client_encoding": "UTF8",
            "dbname": parsed_params["NAME"],
            "user": parsed_params["USER"],
            "password": parsed_params["PASSWORD"],
            "host": parsed_params["HOST"],
            "port": parsed_params.get("PORT", 5432),
        }

    async def listen(self, channel: str) -> AsyncGenerator[ServerSentEvent, None]:
        connection = await psycopg.AsyncConnection.connect(
            **self.db_params,
            autocommit=True,
        )

        async with connection.cursor() as cursor:
            logger.debug(f"Listening to {channel}")
            await cursor.execute(f"LISTEN {channel}")
            generator = connection.notifies()
            async for notify_message in generator:
                payload = json.loads(notify_message.payload)
                logger.debug(f"Data received from {channel}")
                yield ServerSentEvent(**payload)

    def notify(self, channel: str, sse_payload: dict) -> None:
        connection = psycopg.Connection.connect(
            **self.db_params,
            autocommit=True,
        )
        logger.debug(f"Publishing to {channel}: {sse_payload}")
        with connection.cursor() as cursor:
            cursor.execute(f"NOTIFY {channel}, '{json.dumps(sse_payload)}'")
