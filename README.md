# sse-relay-server (wip)

For some background https://github.com/Tobi-De/sse_server_postgres_listen_notify

Originally designed for Django, now a simple, standalone Server-Sent Events relay service, ideal for Django projects
seeking straightforward real-time capabilities without the need for Daphne and async Django setup.

![SSE relay message transmission diagram](diagram.png)

## Installation

As a package

```sh
pip install sse-relay-server
```

As a container

```sh
docker pull ghcr.io/tobi-de/sse_relay_server:latest
```

## Protocols supported

-
postgresql [listen](https://www.postgresql.org/docs/current/sql-listen.html)/[notify](https://www.postgresql.org/docs/15/sql-notify.html)
- redis [pub/sub](https://redis.io/topics/pubsub)

## Environment variables

```sh
ALLOWED_ORIGINS= # comma-separated urls allowed to request sse connections
DATABASE_URL= # postgres database url
REDIS_URL= # redis url if you want to use redis instead of postgres
RELAY_SERVER_DEBUG= # bool for debug mode
```

If the redis Environment variables is set it will be used instead of the postgres database.

## Send messages from your django app.

If you've installed this package to your django project you have access to a simple notify function to send messages,
it works for both redis and postgres.

```python
from sse_relay_server.gateways import gateway

gateway.notify(
    channel="Notifications",
    sse_payload={
        "event": "NEW_NOTIFICATION",
        "id": 1,
        "data": json.dumps({"message": "A new notification"}),
    },
)
```

**channel**: The PostgreSQL channel to use for sending the message (The same you specified in the template above).

**sse_payload**: A Python dictionary containing all the details of the SSE event. For a complete list of available
options, refer to [this class definition](https://github.com/sysid/sse-starlette/blob/main/sse_starlette/sse.py#L50).

To keep things running smoothly, it's a good idea to avoid using overly lengthy channel names, excessively large
payloads for postgre `notify messages`, and excessively bulky data for SSE event payloads, as there are size limitations
for each of these aspects. If you find yourself needing to retrieve a hefty database object, consider sending just the
key and fetching the full data on the frontend using another request (such as an htmx request). While this extra request
may not be the most ideal solution, for simplicity's sake it's often a worthwhile trade-off.
At my workplace, we implemented a straightforward real-time notification system using this approach, successfully
transmitting all the necessary notification data without any issues. However, it's essential to be aware of the
potential risk of sending overly large data. For more in-depth information, you can refer to the following links:

- [Postgres Notify](https://www.postgresql.org/docs/15/sql-notify.html)
- [Postgres Listen](https://www.postgresql.org/docs/current/sql-listen.html)
- [Server Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)
- [Redis Pub/Sub](https://redis.io/topics/pubsub)

If for some reason you dont want or cannot installed this package, the code for sinding events for both postgres and
redis are quite simple, you can easily
copy paste them from below

### Postgres

```python
import json
from django.db import connection


def notify(channel: str, sse_payload: dict) -> None:
    with connection.cursor() as cursor:
        cursor.execute(f"NOTIFY {channel}, '{json.dumps(sse_payload)}'")
```

### Redis

```python
import json
import redis

REDIS_URL = "redis://localhost:6379/0"


def notify(channel: str, sse_payload: dict) -> None:
    r = redis.from_url(REDIS_URL)
    r.publish(channel=channel, message=json.dumps(sse_payload))
```
