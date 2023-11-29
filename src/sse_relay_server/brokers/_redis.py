import json
from typing import AsyncGenerator

import redis
import redis.asyncio as async_redis
import structlog
from sse_starlette import ServerSentEvent

logger = structlog.stdlib.get_logger("brokers.postgres")


class RedisBroker:
    def __init__(self, redis_url: str) -> None:
        self._client = async_redis.from_url(redis_url)
        self._sync_client = redis.from_url(redis_url)

    async def listen(self, channel: str) -> AsyncGenerator[ServerSentEvent, None]:
        async with self._client.pubsub() as pubsub:
            logger.debug(f"Listening to {channel}")
            await pubsub.subscribe(channel)
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    payload = json.loads(message["data"].decode())
                    logger.debug(f"Data received from {channel}")
                    yield ServerSentEvent(**payload)

    def notify(self, channel: str, sse_payload: dict) -> None:
        logger.debug(f"Publishing to {channel}: {sse_payload}")
        self._sync_client.publish(channel=channel, message=json.dumps(sse_payload))
