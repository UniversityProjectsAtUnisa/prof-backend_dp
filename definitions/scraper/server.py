import asyncio

from grpclib.server import Server
from grpclib.utils import graceful_exit


class ScraperServer:
    def __init__(self, servicer, host="localhost", port=50051):
        self._servicer = servicer
        self._host = host
        self._port = port

    async def serve(self) -> None:
        server = Server([self._servicer])
        with graceful_exit([server]):
            await server.start(self._host, self._port)
            print(f'Serving on {self._host}:{self._port}')
            await server.wait_closed()

    def run(self):
        asyncio.run(self.serve())
