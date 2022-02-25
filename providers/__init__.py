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

_providers_priority = {
    "it": ["wikipediait", "treccani", "sapere", "wikipediaen", "britannica"],
    "en": ["wikipediaen", "britannica", "wikipediait", "sapere", "treccani"]
}


def provide_by_language(providers, lang):
    if lang in _providers_priority:
        for p in _providers_priority[lang]:
            yield p, providers[p]
    else:
        for p in providers_port_mapping:
            yield p, providers[p]
