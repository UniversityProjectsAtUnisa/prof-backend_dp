from doctest import ELLIPSIS_MARKER
import requests
from bs4 import BeautifulSoup as bs
from definitions.scraper import ScraperBase, ScrapeReply, DisamiguousLink
from urllib.parse import urljoin
from typing import Callable, Tuple

from grpclib.exceptions import GRPCError
from grpclib.const import Status


class ScraperBritannica(ScraperBase):
    _BASE_URL = "https://www.britannica.com"
    _SEARCH_QUERY = "/search?query="
    _SEARCH_URL = _BASE_URL + _SEARCH_QUERY

    def _is_url(self, text: str) -> bool:
        return "/" in text
    
    def _cut_to_grammar_point(self, sentences: str) -> str:
        for i in range(len(sentences)-1, 0, -1):
            if sentences[i] == ".":
                return sentences[:i + 1]
    
    def _sanitize_text(self, str: str) -> str:
        return str.replace("\r", "").replace("\n", "").replace("\t", "").strip()

    def _search_scraping(self, url: str) -> dict:
        r = requests.get(url)

        if r.status_code != 200:
            raise GRPCError(status=Status.INTERNAL, message="Request to provider failed")

        soup = bs(r.content, "lxml")

        container = soup.find("ul", class_="list-unstyled results")
        if not container:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")

        result = []
        for item in container.find_all("li"):
            title_section = item.find("a")
            desc = item.find("div")

            data = {}

            data["label"] = (self._sanitize_text(title_section.get_text()) + " - " + self._sanitize_text(desc.get_text()))[:150]
            data["url"]  = title_section["href"]

            result.append(data)
        
        return result

    def _long_scraping(self, url: str) -> str:
        r = requests.get(url)

        if r.status_code != 200:
            raise GRPCError(status=Status.INTERNAL, message="Request to provider failed")
        soup = bs(r.content, "lxml")

        paragraphs = soup.find('div', {"class": "topic-content"})
        result = ""
        for p in paragraphs.section.childGenerator():
            if p.name in ["p", "span"]:
                result += p.get_text()
        if result == "":
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        return result

    def _short_scraping(self, url: str) -> str:
        r = requests.get(url)
        if r.status_code != 200:
            raise GRPCError(status=Status.INTERNAL, message="Request to provider failed")
        soup = bs(r.content, "lxml")

        paragraphs = soup.find('div', {"class": "topic-content"})
        result = ""
        for p in paragraphs.section.childGenerator():
            if p.name in ["p", "span"]:
                result += p.get_text()
        if result == "":
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        return self._cut_to_grammar_point(result[:1024])

    def _choose_strategy(self, text:str, is_long:bool) -> Tuple[bool, Callable, str]:
        disambigous = True
        strategy = None
        param = ""

        if self._BASE_URL in text:
            if self._SEARCH_QUERY in text: #https://www.britannica.com/search?query=alabama
                strategy = self._search_scraping
                param = text
                disambigous = True
            else: #https://www.britannica.com/place/Alabama-state
                strategy = self._short_scraping if not is_long else self._long_scraping
                param=text
                disambigous = False
        else:
            if self._SEARCH_QUERY in text: #/search?query=alabama
                strategy = self._search_scraping
                param=f"{urljoin(self._BASE_URL, text)}"
                disambigous = True
            else: 
                if self._is_url(text): #/place/Alabama-state
                    strategy = self._short_scraping
                    param=f"{urljoin(self._BASE_URL, text)}"
                    disambigous = False
                else: #alabama
                    strategy = self._search_scraping
                    param=self._SEARCH_URL + text
                    disambigous = True

        return (disambigous, strategy, param)

    async def search(self, text: str) -> ScrapeReply:
        r = None
        disambigous, strategy, param = self._choose_strategy(text, False)

        r=strategy(param)

        if not r:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        
        if disambigous:
            return ScrapeReply(
                language="en",
                disambiguous=True,
                data='',
                disambiguous_data=[DisamiguousLink(label=f"{item['label']}", url=f"{urljoin(self._BASE_URL, item['url'])}") for item in r])
        return ScrapeReply(language="en", disambiguous=False, data=r)


    async def long_search(self, text: str) -> ScrapeReply:
        r = None
        disambigous, strategy, param = self._choose_strategy(text, True)

        r=strategy(param)

        if not r:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        
        if disambigous:
            return ScrapeReply(
                language="en",
                disambiguous=True,
                data='',
                disambiguous_data=[DisamiguousLink(label=item['label'], url=f"{urljoin(self._BASE_URL, item['url'])}") for item in r])
        return ScrapeReply(language="en", disambiguous=False, data=r)
