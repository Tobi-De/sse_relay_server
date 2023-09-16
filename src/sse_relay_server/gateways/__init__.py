from typing import Protocol, AsyncGenerator

from sse_starlette import ServerSentEvent

from sse_relay_server.config import (
    ConfigurationError,
    get_redis_url,
    get_postgres_url,
)
from ._postgres import PostgresGateway
from ._redis import RedisGateway


def _select_gateway():
    if redis_url := get_redis_url():
        return RedisGateway(redis_url)
    if postgres_url := get_postgres_url():
        return PostgresGateway(postgres_url)
    else:
        raise ConfigurationError("Set either SSE_REDIS_URL or SSE_DATABASE_URL")


gateway = _select_gateway()


class Gateway(Protocol):
    async def listen(self, channel: str) -> AsyncGenerator[ServerSentEvent, None]:
        ...

    def notify(self, channel: str, sse_payload: dict) -> None:
        ...
