from definitions.scraper import ScraperBase, ScrapeReply, DisamiguousLink
import logging
import sys
import requests
from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from unicodedata import category, normalize
import sys
import unicodedata


class ScraperTreccani(ScraperBase):

    def _scrape_treccani(self, soup: BeautifulSoup) -> str:
        summary = soup.find('div', {'class': 'module-article-full_content'})
        if summary is None:
            for_page_with_vedi_altro = soup.find('div', {'class': 'abstract'})
            return for_page_with_vedi_altro
        return summary

    def _disambiguity_page(self, search_term, soup: BeautifulSoup) -> list:
        url_base = 'https://www.treccani.it'
        final_list = []
        final_map = {}
        h2 = soup.find_all('h2', {'class': 'search_preview-title'})
        for h in h2:
            h_good = "".join(c for c in h.text.strip() if unicodedata.category(c) not in ["No", "Lo"])
            h_good = ''.join(c for c in normalize('NFD', h_good) if category(c) != 'Mn')
            if h_good == search_term or search_term in h_good:
                child = h.find('a')
                url_final = url_base + child.get('href')
                final_map = {'label': h.text.strip(), 'url': url_final}
                final_list.append(final_map)
        logging.info('Il termine inserito può avere diversi significati: \n')
        return final_list

    async def search(self, text: str) -> ScrapeReply:
        possible_disambiguity = False
        endpoint = text
        if 'www.treccani.it' in text:
            if 'www.treccani.it/vocabolario/ricerca' in text:
                possible_disambiguity = True
            else:
                text = ''.join(c for c in normalize('NFD', text) if category(c) != 'Mn')
                text = text.strip().lower().split()
                prefix = f'https://www.treccani.it/vocabolario/ricerca/'
                query = "_".join(text)
                processed_query = '_'.join(query.split())
                endpoint = f'{prefix}{processed_query}'
                possible_disambiguity = True
            req = requests.get(endpoint)
            soup = BeautifulSoup(req.text, 'html.parser')
            if possible_disambiguity == False:
                summary = self._scrape_treccani(soup)
                summary = summary.text.strip()
                return ScrapeReply(language="it", disambiguous=False, data=summary)
            else:
                if 'www.treccani' in text:
                    text = text.replace('https://www.treccani.it/vocabolario/ricerca/', '')
                    text = text.replace('/', '')
                else:
                    text = ' '.join(word for word in text)
                h2 = soup.find_all('h2', {'class': 'search_preview-title'})
                i = 0
                for h in h2:
                    h = "".join(c for c in h.text.strip() if unicodedata.category(c) not in ["No", "Lo"])
                    h = ''.join(c for c in normalize('NFD', h) if category(c) != 'Mn')
                    if (text in h or text == h):
                        i = i+1
                if i == 1:
                    prefix = f'https://www.treccani.it/vocabolario/'
                    if len(text.split()) > 1:
                        text = text.replace(" ", "-") + ('_%28Neologismi%29/')
                    endpoint = f'{prefix}{text}'
                    req = requests.get(endpoint)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    if req.status_code != 200:
                        raise RequestException(f'Il Professore non ha trovato la pagina: {endpoint}.\n Effettua un altra richiesta.')
                    summary = self._scrape_treccani(soup)
                    summary = summary.text.strip()
                    return ScrapeReply(language="it", disambiguous=False, data=summary)
                elif i == 0:
                    raise RequestException(f'Il Professore non ha trovato la pagina: {endpoint}.\n Effettua un altra richiesta.')
                else:
                    disambiguous_link = self._disambiguity_page(text, soup)
                    return ScrapeReply(language="it", disambiguous=True, data=disambiguous_link)

    async def long_search(self, text: str) -> ScrapeReply:
        return await self.search(text)
