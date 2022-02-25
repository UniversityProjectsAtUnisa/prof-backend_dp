import asyncio
from grpclib import GRPCError
from grpclib.const import Status
import pytest

from definitions.scraper import ScrapeReply
from .. import ScraperWikipediaIT


@pytest.fixture
def client():
    return ScraperWikipediaIT()


@pytest.mark.asyncio
async def test_search_success(client: ScraperWikipediaIT):
    """ Tests the successful search of a word. """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("ciao")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "it"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_failed(client: ScraperWikipediaIT):
    """ Tests the failed search of a word. """
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("fhjashd")

        assert excinfo.value.status == Status.NOT_FOUND


@pytest.mark.asyncio
async def test_search_disambiguous(client: ScraperWikipediaIT):
    """ Tests the search of a disambiguos word """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("asd")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "it"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_disambiguous_link(client: ScraperWikipediaIT):
    """ Tests the search of a disambiguos link """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://it.wikipedia.org/wiki/Maria")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "it"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_search_link(client: ScraperWikipediaIT):
    """ Tests the successful search of a link. """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://it.wikipedia.org/wiki/Ciao")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "it"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_link_failed(client: ScraperWikipediaIT):
    """ Tests the failed search of a link. """
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("https://it.wikipedia.org/wiki/fhjashd")

        assert excinfo.value.status == Status.NOT_FOUND