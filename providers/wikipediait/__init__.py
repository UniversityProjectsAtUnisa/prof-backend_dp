from definitions.scraper import ScraperBase, ScrapeReply, DisamiguousLink
import logging
import requests
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
from grpclib.exceptions import GRPCError
from grpclib.const import Status


class ScraperWikipediaIT(ScraperBase):

    def _clean(self, text: str) -> str:
        cleanstring = text
        cleanstring = re.sub('[A-Z]{1}?<=\.', '', cleanstring)
        cleanstring = re.sub('\.?=[A-Z]', '', cleanstring)
        cleanstring = re.sub('\[\d+\]', '', cleanstring)
        cleanstring = re.sub("\s?[\(\[].*?[\)\]]", "", text)
        cleanstring.replace(" .", ".")
        cleanstring.replace(" ,", ".")
        cleanstring = re.sub("\)", "", cleanstring)
        return cleanstring

    def _get_may_refer_to_list(self, soup: BeautifulSoup) -> list:
        list_li = soup.find('div', {'class': 'mw-parser-output'}).find_all('li', class_=None)
        absolute_url = 'https://it.wikipedia.org'
        final_map = {}
        final_list = []
        for item in list_li:
            child = item.find("a")
            if not ((child.has_attr('class') and child['class'][0] == 'mw-disambig') or ('wiktionary' in child['href'] and child['href'] is not None)):
                url = (absolute_url + child.get('href'))
                final_map = DisamiguousLink(label=item.text, url=url)
                final_list.append(final_map)
        return final_list


    def _get_summary(self, soup: BeautifulSoup) -> str:
        first_paragraph = soup.find('div', {'class': 'mw-parser-output'}).find_all('p', limit=5, recursive=False)
        summary = None
        for p in first_paragraph:
            if len(p.text) > 5:
                summary = p.text
                break
        return self._clean(summary)

    def _create_soup(self, text: str) -> BeautifulSoup:
        if 'it.wikipedia.org' in text:
            endpoint = text
        else:
            text = text.strip().lower().split()
            prefix = f'https://it.wikipedia.org/wiki/'
            query = "_".join(text)
            processed_query = '_'.join(query.split())
            endpoint = f'{prefix}{processed_query}'
        req = requests.get(endpoint)

        if req.status_code != 200:
            raise GRPCError(status=Status.NOT_FOUND, message="Text not found")

        soup = BeautifulSoup(req.text, 'html.parser')
        return soup

    def _is_disambiguous(self, soup: BeautifulSoup) -> bool:
        table_disambiguity = soup.find('table', {'class': 'avviso-disambigua'})
        return table_disambiguity is not None

    async def search(self, text: str) -> ScrapeReply:
        soup = self._create_soup(text)
        if self._is_disambiguous(soup):
            disambiguous_link = self._get_may_refer_to_list(soup)
            return ScrapeReply(language="it", disambiguous=True, disambiguous_data=disambiguous_link)
        summary = self._get_summary(soup)
        if summary is None:
            raise GRPCError(status=Status.NOT_FOUND, message="Summary not found")
        return ScrapeReply(language="it", disambiguous=False, data=summary)

    async def long_search(self, text: str) -> ScrapeReply:
        soup = self._create_soup(text)
        if self._is_disambiguous(soup):
            disambiguous_link = self._get_may_refer_to_list(soup)
            return ScrapeReply(language="it", disambiguous=True, disambiguous_data=disambiguous_link)
        
        total = soup.find('div', {'class': 'mw-parser-output'})
        result = ""
        for t in total.childGenerator():
            if t.name == "h2" and t.find('span', attrs={"id": ["Note"]}):
                break
            if t.name in ["p", "h2", "h3", "ul"]:
                result += t.get_text() + "\n\n"
        data = self._clean(result)
        return ScrapeReply(language="it", disambiguous=False, data=data)
