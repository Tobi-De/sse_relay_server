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


# @app.middleware("http")
# async def logging_middleware(request: Request, call_next) -> Response:
#     structlog.contextvars.clear_contextvars()
#     # These context vars will be added to all log entries emitted during the request
#     request_id = correlation_id.get()
#     structlog.contextvars.bind_contextvars(request_id=request_id)

#     start_time = time.perf_counter_ns()
#     # If the call_next raises an error, we still want to return our own 500 response,
#     # so we can add headers to it (process time, request ID...)
#     response = Response(status_code=500)
#     try:
#         response = await call_next(request)
#     except Exception:
#         # TODO: Validate that we don't swallow exceptions (unit test?)
#         structlog.stdlib.get_logger("sse_relay_server").exception("Uncaught exception")
#         raise
#     finally:
#         process_time = time.perf_counter_ns() - start_time
#         status_code = response.status_code
#         url = get_path_with_query_string(request.scope)
#         client_host = request.client.host
#         client_port = request.client.port
#         http_method = request.method
#         http_version = request.scope["http_version"]
#         # Recreate the Uvicorn access log format, but add all parameters as structured information
#         relay_logger.info(
#             f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code}""",
#             http={
#                 "url": str(request.url),
#                 "status_code": status_code,
#                 "method": http_method,
#                 "request_id": request_id,
#                 "version": http_version,
#             },
#             network={"client": {"ip": client_host, "port": client_port}},
#             duration=process_time,
#         )
#         response.headers["X-Process-Time"] = str(process_time / 10**9)
#         return response


# app.add_middleware(CorrelationIdMiddleware)


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
