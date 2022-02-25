import requests
from bs4 import BeautifulSoup as bs
import re

from definitions.scraper import ScraperBase, ScrapeReply, DisamiguousLink
import logging
from urllib.parse import urljoin

from typing import Callable, Tuple, List, Dict
from grpclib.exceptions import GRPCError
from grpclib.const import Status

class ScraperSapereIT(ScraperBase):
    _BASE_URL = "https://www.sapere.it"
    _SEARCH_QUERY = "/sapere/search.html?q1="
    _SEARCH_URL = _BASE_URL + _SEARCH_QUERY

    def _is_url(self, text: str) -> bool:
        """ Verify if a string is an url.

        Args:
            text: the string that will be verified

        Return:
            A boolean where if it is True mean that the input text is an url, False otherwise
        """
        return "/" in text
    
    def _cut_to_grammar_point(self, sentences: str) -> str:
        """ Cut the input string to the last grammar point.

        Args:
            sentences: the string that will be cutted

        Return:
            The cutted string
        """
        for i in range(len(sentences)-1, 0, -1):
            if sentences[i] == ".":
                return sentences[:i + 1]
    
    def _sanitize_text(self, str: str) -> str:
        """ Clean the input text from special characters.

        Args:
            sentences: the string that will be cleaned

        Return:
            The cleaned string
        """
        return str.replace("\r", " ").replace("\n", " ").replace("\t", "").strip()

    def _search_scraping(self, url: str) -> List[Dict[str, str]]:
        """ The scrape function used to search on provider.

        Args:
            url: the url of the searching page

        Raises:
            GRPCError: An exception to communicate two types of error: Result not found and internal error

        Return:
            A list of dict where every dict as a label that rappresent a disambigous search and short description, and url of the disambigous search
        """
        r = requests.get(url)

        if r.status_code != 200:
            raise GRPCError(status=Status.INTERNAL, message="Request to provider failed")

        soup = bs(r.content, "lxml")

        container = soup.find("ul", class_="search-results-list")
        if not container:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")

        result = []
        for item in container.find_all("li"):
            title_section = item.find("a")

            data = {}

            data["label"] = (self._sanitize_text(title_section["title"]) + " - " + self._sanitize_text(item.article.p.get_text()))[:150]
            data["url"]  = title_section["href"]

            result.append(data)
        
        return result

    def _long_scraping(self, url: str) -> str:
        """ The scrape function used to get a long description of a item on provider.

        Args:
            url: the url of the item page
        
        Raises:
            GRPCError: An exception to communicate two types of error: Result not found and internal error

        Return:
            A string that contains a long description of item
        """
        r = requests.get(url)

        if r.status_code != 200:
            raise GRPCError(status=Status.INTERNAL, message="Request to provider failed")
        soup = bs(r.content, "lxml")

        paragraphs = soup.findAll('div', {"id": re.compile('^p')})
        logging.info(len(paragraphs))

        if len(paragraphs) == 0:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        
        result = "" 
        for i, paragraph in enumerate(paragraphs):
            for p in paragraph.childGenerator():
                if p.name in ["p", "h2"]:
                    result+=p.getText()  + ("\n\n" if p.name == "h1" else "\n")
        result = result[:-2]
        
        if result == "":
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")

        return result

    def _short_scraping(self, url: str) -> str:
        """ The scrape function used to get a short description of a item on provider.

        Args:
            url: the url of the item page
        
        Raises:
            GRPCError: An exception to communicate two types of error: Result not found and internal error

        Return:
            A string that contains a short description of item
        """

        r = requests.get(url)

        if r.status_code != 200:
            raise GRPCError(status=Status.INTERNAL, message="Request to provider failed")

        soup = bs(r.content, "lxml")

        paragraphs = soup.findAll('div', {"id": re.compile('^p')})
        sub_result = ""

        if len(paragraphs) == 0:
            desc = soup.find('div', {"itemprop": "description"})
            if desc is None:
                raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
            sub_result = self._sanitize_text(desc.get_text())
        else:
            sub_result = paragraphs[0].p.get_text()
        result = self._cut_to_grammar_point(sub_result[:1024])
        if result == "":
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        return result

    def _choose_strategy(self, text:str, is_long:bool) -> Tuple[bool, Callable, str]:
        """ Used to decide, with respect to the input text and if the search is long, the scraping function to be used.

        Args:
            text: the input text of search
            is_long: if the seearch will be a long search ir not

        Return:
            A tuple with:
                disambigous: if the search will be disambigous or not
                strategy: the scraping function that will be used
                param: the param of the scraping function
        """
        disambigous = True
        strategy = None
        param = ""

        if self._BASE_URL in text:
            if self._SEARCH_QUERY in text: #https://www.sapere.it/sapere/search.html?q1=alabama
                strategy = self._search_scraping
                param = text
                disambigous = True
            else: #https://www.sapere.it/enciclopedia/Alabama+%28Stato%29.html
                strategy = self._short_scraping if not is_long else self._long_scraping
                param=text
                disambigous = False
        else:
            if self._SEARCH_QUERY in text: #/search.html?q1=alabama
                strategy = self._search_scraping
                param=f"{urljoin(self._BASE_URL, text)}"
                disambigous = True
            else: 
                if self._is_url(text): #/enciclopedia/Alabama+%28Stato%29.html
                    strategy = self._short_scraping
                    param=f"{urljoin(self._BASE_URL, text)}"
                    disambigous = False
                else: #alabama
                    strategy = self._search_scraping
                    param=self._SEARCH_URL + text
                    disambigous = True
        logging.info(param)

        return (disambigous, strategy, param)

    async def search(self, text: str) -> ScrapeReply:
        """ The interface fuction to make a search called from outside.

        Args:
            text: a string that rappresent what the clien are searching. It can be an url or a simple sentence
        
        Raises:
            GRPCError: if the result is not found
        
        Return:
            A ScrapeReply object with:
                language: the language of search
                disambigous: if the search is diambigous
                data: the result of search if disambigous is False
                disambigous_data: the result of search if disambigous is True
        """
        r = None
        disambigous, strategy, param = self._choose_strategy(text, False)

        r=strategy(param)

        logging.info(f'r={r}')

        if not r:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        
        if disambigous:
            return ScrapeReply(
                language="it",
                disambiguous=True,
                data='',
                disambiguous_data=[DisamiguousLink(label=f"{item['label']}", url=f"{urljoin(self._BASE_URL, item['url'])}") for item in r])
        return ScrapeReply(language="it", disambiguous=False, data=r)


    async def long_search(self, text: str) -> ScrapeReply:
        """ The interface fuction to make a long search called from outside.

        Args:
            text: a string that rappresent what the clien are searching. It can be an url or a simple sentence
        
        Raises:
            GRPCError: if the result is not found
        
        Return:
            A ScrapeReply object with:
                language: the language of search
                disambigous: if the search is diambigous
                data: the result of search if disambigous is False
                disambigous_data: the result of search if disambigous is True
        """
        r = None
        disambigous, strategy, param = self._choose_strategy(text, True)

        r=strategy(param)

        if not r:
            raise GRPCError(status=Status.NOT_FOUND, message="Result not found")
        
        if disambigous:
            return ScrapeReply(
                language="it",
                disambiguous=True,
                data='',
                disambiguous_data=[DisamiguousLink(label=f"{item['label']}", url=f"{urljoin(self._BASE_URL, item['url'])}") for item in r])
        return ScrapeReply(language="it", disambiguous=False, data=r)