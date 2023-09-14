import json

import uvicorn
import psycopg

from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.routing import Route
from .config import get_database_params, get_allowed_origins, get_debug_value


async def event_publisher(request: Request):
    aconnection = await psycopg.AsyncConnection.connect(
        **get_database_params(),
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
        allow_origins=get_allowed_origins(),
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
]

app = Starlette(debug=get_debug_value(), routes=routes, middleware=middleware)


if __name__ == "__main__":
    # pass arguments to uvicorn.run() here
    uvicorn.run("sse_relay_server.main:app", host="0.0.0.0", port=8001)
