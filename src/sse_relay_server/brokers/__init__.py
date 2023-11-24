from typing import Protocol, AsyncGenerator

from sse_starlette import ServerSentEvent

from sse_relay_server.config import (
    ConfigurationError,
    get_redis_url,
    get_postgres_url,
)
from ._postgres import PostgresBroker
from ._redis import RedisBroker


def _select_broker():
    if redis_url := get_redis_url():
        return RedisBroker(redis_url)
    if postgres_url := get_postgres_url():
        return PostgresBroker(postgres_url)
    else:
        raise ConfigurationError("Set either REDIS_URL or DATABASE_URL")


broker = _select_broker()


class Broker(Protocol):
    async def listen(self, channel: str) -> AsyncGenerator[ServerSentEvent, None]:
        ...

    def notify(self, channel: str, sse_payload: dict) -> None:
        ...