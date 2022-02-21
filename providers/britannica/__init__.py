import requests
from bs4 import BeautifulSoup as bs
from definitions.scraper import ScraperBase, ScrapeReply, DisamiguousLink
import logging
import sys


class ScraperBritannica(ScraperBase):
    _BASE_URL = "https://www.britannica.com"
    _SEARCH_URL = _BASE_URL + "/search?query="
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
            return False

        soup = bs(r.content, "lxml")

        container = soup.find("ul", class_="list-unstyled results")
        if not container:
            return False

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
            return False
        soup = bs(r.content, "lxml")

        paragraphs = soup.find('div', {"class": "topic-content"})
        result = ""
        for p in paragraphs.section.childGenerator():
            if p.name in ["p", "span"]:
                result += p.get_text()
        if result == "":
            return False
        return result

    def _short_scraping(self, url: str) -> str:
        r = requests.get(url)
        if r.status_code != 200:
            return False
        soup = bs(r.content, "lxml")

        paragraphs = soup.find('div', {"class": "topic-content"})
        result = ""
        for p in paragraphs.section.childGenerator():
            if p.name in ["p", "span"]:
                result += p.get_text()
        if result == "":
            return False
        return self._cut_to_grammar_point(result[:1024])

    async def search(self, text: str) -> ScrapeReply:
        logging.info("")

        r = None
        disambigous = True

        if self._is_url(text):
            if "seach.html" in text:
                r = self._short_scraping(self._BASE_URL+text)
                disambigous = False
            else:
                r = self._search_scraping(self._BASE_URL+text)
        else:
            r = self._search_scraping(self._SEARCH_URL+text)

        if not r:
            return #TODO: communicate error
        
        if disambigous:
            return ScrapeReply(
                language="en",
                disambiguous=True,
                data='',
                disambiguous_data=[DisamiguousLink(label=item.label, url=item.url) for item in r])
        return ScrapeReply(language="en", disambiguous=False, data=r)


    async def long_search(self, text: str) -> ScrapeReply:
        r = None
        disambigous = True

        if self._is_url(text):
            if "seach.html" in text:
                r = self._long_scraping(self._BASE_URL+text)
                disambigous = False
            else:
                r = self._search_scraping(self._BASE_URL+text)
        else:
            r = self._search_scraping(self._SEARCH_URL+text)

        if not r:
            return #TODO: communicate error
        
        if disambigous:
            return ScrapeReply(
                language="en",
                disambiguous=True,
                data='',
                disambiguous_data=[DisamiguousLink(label=item.label, url=item.url) for item in r])
        return ScrapeReply(language="en", disambiguous=False, data=r)
