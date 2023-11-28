from __future__ import annotations

import argparse

import structlog
import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Route

from . import listen
from ._logging import setup_logging
from .config import get_allowed_origins
from .config import get_debug_value
from .config import get_log_level


setup_logging(json_logs=False, log_level=get_log_level())

relay_logger = structlog.stdlib.get_logger("sse_relay_server")


async def sse(request: Request):
    channel = request.path_params.get("channel")
    relay_logger.info(f"New SSE connection to {channel}")
    return EventSourceResponse(listen(channel))


routes = [Route("/{channel}", endpoint=sse)]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=get_debug_value(), routes=routes, middleware=middleware)


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
    parser.add_argument("--workers", type=int)

    args = parser.parse_args()

    uvicorn.run("sse_relay_server.main:app", **args.__dict__)


if __name__ == "__main__":
    main()
