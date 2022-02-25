import asyncio
from grpclib import GRPCError
from grpclib.const import Status
import pytest

from definitions.scraper import ScrapeReply
from .. import ScraperSapereIT


@pytest.fixture
def client():
    return ScraperSapereIT()


@pytest.mark.asyncio
async def test_search_success(client: ScraperSapereIT):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("/enciclopedia/ci%C3%A0o.html")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "it"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_failed(client: ScraperSapereIT):
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("ahdimdhpa")

        assert excinfo.value.status == Status.NOT_FOUND


@pytest.mark.asyncio
async def test_search_disambiguous(client: ScraperSapereIT):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("ciao")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "it"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_disambiguous_link(client: ScraperSapereIT):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://www.sapere.it/sapere/search.html?q1=ciao")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "it"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_search_link(client: ScraperSapereIT):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://www.sapere.it/enciclopedia/ci%C3%A0o.html")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "it"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_link_failed(client: ScraperSapereIT):
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("https://www.sapere.it/sapere/search.html?q1=ahdimdhpa")

        assert excinfo.value.status == Status.NOT_FOUND
        
        
