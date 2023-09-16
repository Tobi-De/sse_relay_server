from __future__ import annotations

import argparse

import uvicorn
from sse_starlette import ServerSentEvent
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Route

from .config import get_allowed_origins, get_debug_value
from .gateways import gateway

SSE_SERVER_DEBUG = get_debug_value()
ALLOWED_ORIGINS = get_allowed_origins()


async def generate_stop_event():
    # Set a high retry interval (e.g., 1 year in milliseconds)
    retry_interval = 365 * 24 * 60 * 60 * 1000
    yield ServerSentEvent(
        "Please stop, there is nothing here ;(",
        retry=retry_interval,
        comment="Shut down the connection",
    )


async def sse(request: Request):
    if channel := request.query_params.get("channel"):
        return EventSourceResponse(gateway.listen(channel))
    else:
        return EventSourceResponse(generate_stop_event())


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
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
    )

    args = parser.parse_args()

    uvicorn.run("sse_relay_server.main:app", **args.__dict__)


if __name__ == "__main__":
    main()
