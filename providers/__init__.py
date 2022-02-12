from config import MARCO_PORT
from definitions.scraper import ScraperStub
from grpclib.client import Channel


def create_client(host, port) -> ScraperStub:
    channel = Channel(host, port)
    return ScraperStub(channel)


def close_client(stub: ScraperStub):
    stub.channel.close()


providers_port_mapping = {
    "marco": MARCO_PORT
}

