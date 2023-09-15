class PostgresGateway:
    async def listen(self, channel: str) -> None:
        pass

    def notify(self, channel: str, sse_payload: dict) -> None:
        pass
