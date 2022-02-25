import asyncio
from grpclib import GRPCError
from grpclib.const import Status
import pytest

from definitions.scraper import ScrapeReply
from .. import ScraperTreccani


@pytest.fixture
def client():
    return ScraperTreccani()


@pytest.mark.asyncio
async def test_search_success(client: ScraperTreccani):
    """ Tests the successful search of a word. """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("consonante")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "it"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0


@pytest.mark.asyncio
async def test_search_failed(client: ScraperTreccani):
    """ Tests the failed search of a word. """
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("fhjashd")

        assert excinfo.value.status == Status.NOT_FOUND


@pytest.mark.asyncio
async def test_search_disambiguous(client: ScraperTreccani):
    """ Tests the search of a disambiguos word """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("ciao")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "it"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_disambiguous_link(client: ScraperTreccani):
    """ Tests the search of a disambiguos link """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://www.treccani.it/vocabolario/ricerca/ciao/")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == True
        assert res.language == "it"
        assert len(res.data) == 0
        assert len(res.disambiguous_data) != 0


@pytest.mark.asyncio
async def test_search_link(client: ScraperTreccani):
    """ Tests the successful search of a link. """
    requests = [client.search, client.long_search]
    for req in requests:
        res = await req("https://www.treccani.it/vocabolario/consonante/")
        assert isinstance(res, ScrapeReply)
        assert res.disambiguous == False
        assert res.language == "it"
        assert len(res.data) != 0
        assert len(res.disambiguous_data) == 0
        
@pytest.mark.asyncio
async def test_search_link_failed(client: ScraperTreccani):
    """ Tests the failed search of a link. """
    requests = [client.search, client.long_search]
    for req in requests:
        with pytest.raises(GRPCError) as excinfo:
            await req("https://www.treccani.it/vocabolario/ricerca/gggk/")

        assert excinfo.value.status == Status.NOT_FOUND
        
        
        
