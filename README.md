# sse-relay-server (wip)

For some background https://github.com/Tobi-De/sse_server_postgres_listen_notify

Originally designed for Django, now a simple, standalone Server-Sent Events relay service, ideal for Django projects seeking straightforward real-time capabilities without the need for Daphne and async Django setup.

![SSE relay message transmission diagram](diagram.png)

## Installation

As a package
```sh
pip install sse-relay-server
```
As a container
```sh
docker pull ghcr.io/tobi-de/sse_relay_server:main
```
