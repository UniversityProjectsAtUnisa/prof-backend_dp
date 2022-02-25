from config import TRECCANI_PORT, WIKIPEDIA_EN_PORT, WIKIPEDIA_IT_PORT, BRITANNICA_PORT, SAPERE_PORT
from definitions.scraper import ScraperStub
from grpclib.client import Channel


def create_client(host, port) -> ScraperStub:
    channel = Channel(host, port)
    return ScraperStub(channel)


def close_client(stub: ScraperStub):
    stub.channel.close()


providers_port_mapping = {
    "britannica": BRITANNICA_PORT,
    "treccani": TRECCANI_PORT,
    "wikipediaen": WIKIPEDIA_EN_PORT,
    "wikipediait": WIKIPEDIA_IT_PORT,
    "sapere": SAPERE_PORT
}
