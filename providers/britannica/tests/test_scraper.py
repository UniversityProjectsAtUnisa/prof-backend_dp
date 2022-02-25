import asyncio
from grpclib import GRPCError
from grpclib.const import Status
import pytest

from definitions.scraper import ScrapeReply
from .. import ScraperBritannica


@pytest.fixture
def client():
    return ScraperBritannica()


@pytest.mark.asyncio
async def test_search_success(client: ScraperBritannica):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("/place/Alabama-state")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "en"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0

@pytest.mark.asyncio
async def test_search_disambiguous(client: ScraperBritannica):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("hello")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "en"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_disambiguous_link(client: ScraperBritannica):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://www.britannica.com/search?query=alabama")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "en"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_search_link(client: ScraperBritannica):
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://www.britannica.com/place/Alabama-state")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "en"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0
