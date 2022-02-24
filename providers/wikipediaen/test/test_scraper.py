import asyncio
from grpclib import GRPCError
from grpclib.const import Status
import pytest

from definitions.scraper import ScrapeReply
from .. import ScraperWikipediaEN


@pytest.fixture
def client():
    return ScraperWikipediaEN()


@pytest.mark.asyncio
async def test_search_success(client: ScraperWikipediaEN):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("hello")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "en"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_failed(client: ScraperWikipediaEN):
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("fhjashd")

        assert excinfo.value.status == Status.NOT_FOUND


@pytest.mark.asyncio
async def test_search_disambiguous(client: ScraperWikipediaEN):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("marie")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "en"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_disambiguous_link(client: ScraperWikipediaEN):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://en.wikipedia.org/wiki/Marie")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "en"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_search_link(client: ScraperWikipediaEN):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://en.wikipedia.org/wiki/Hello")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "en"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_link_failed(client: ScraperWikipediaEN):
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("https://en.wikipedia.org/wiki/fhjashd")

        assert excinfo.value.status == Status.NOT_FOUND
        
        
