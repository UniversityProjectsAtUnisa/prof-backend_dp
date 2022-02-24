# import asyncio
# import pytest

# from definitions.scraper import ScrapeReply
# from .. import Marco

# @pytest.fixture
# def client():
#     return Marco()


# @pytest.mark.asyncio
# async def test_long_search_success(client: Marco):
#     res = await client.long_search("ciao")
#     assert isinstance(res, ScrapeReply)
#     assert res.disambiguous == False
#     assert res.language == "it"
#     assert len(res.disambiguous_data) == 0


# @pytest.mark.asyncio
# async def test_long_search_failed(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_long_search_disambiguous(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_search_success(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_search_failed(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_search_disambiguous(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_disambiguous_link(client: Marco):
#     """both long and short"""
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_search_link(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# @pytest.mark.asyncio
# async def test_long_search_link(client: Marco):
#     res = await client.long_search("ciao")
#     print(res)
#     assert True


# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_long_search_success(Marco()))