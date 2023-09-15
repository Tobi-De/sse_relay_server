import json

import uvicorn
import psycopg
import argparse

from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Route
from .config import get_database_params, get_allowed_origins, get_debug_value


DATABASE_PARAMS = get_database_params()
SSE_SERVER_DEBUG = get_debug_value()
ALLOWED_ORIGINS = get_allowed_origins()


async def event_publisher(request: Request):
    aconnection = await psycopg.AsyncConnection.connect(
        **DATABASE_PARAMS,
        autocommit=True,
    )
    channel = request.query_params.get("channel")
    if not channel:
        return

    async with aconnection.cursor() as acursor:
        await acursor.execute(f"LISTEN {channel}")
        generator = aconnection.notifies()
        async for notify_message in generator:
            print(json.loads(notify_message.payload))
            yield ServerSentEvent(**json.loads(notify_message.payload))


async def sse(request: Request):
    return EventSourceResponse(event_publisher(request))


routes = [Route("/", endpoint=sse)]


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=SSE_SERVER_DEBUG, routes=routes, middleware=middleware)


def main():
    parser = argparse.ArgumentParser(
        prog="sse-relay-server",
        description="Relay server for SSE events",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="server host",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="server port",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="enable auto-reload",
        default=False,
    )
    parser.add_argument("--workers", type=int)

    args = parser.parse_args()

    uvicorn.run("sse_relay_server.main:app", **args.__dict__)


if __name__ == "__main__":
    main()
