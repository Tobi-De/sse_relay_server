from sse_relay_server.config import get_gateway_params


def _select_gateway():
    return get_gateway_params()["gateway"]


gateway = _select_gateway()
