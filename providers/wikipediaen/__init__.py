from definitions.scraper import ScraperBase, ScrapeReply
import logging
import sys
import requests
from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import sys
import re


class ScraperWikipediaEN(ScraperBase):
    
    def _clean(self,text:str) -> str:    
        cleanstring = text
        cleanstring = re.sub('[A-Z]{1}?<=\.', '', cleanstring)
        cleanstring = re.sub('\.?=[A-Z]', '', cleanstring)
        cleanstring = re.sub('\[\d+\]', '', cleanstring)
        cleanstring = re.sub("\s?[\(\[].*?[\)\]]","",text)
        cleanstring.replace(" .",".")
        cleanstring.replace(" ,",".")
        cleanstring = re.sub("\)","",cleanstring)
        return cleanstring
    
    def _get_may_refer_to_list(soup: BeautifulSoup) -> list:
        total = soup.find('div', {'class': 'mw-parser-output'})
        absolute_url = 'https://en.wikipedia.org'
        final_map = {}
        final_list = []
        for item in total.childGenerator():
            if item.name == "h2" and item.find('span',attrs={"id":["See_also"]}):
                break
            if item.name == "ul":
                li = item.find_all('li')
                for l in li:
                    child =l.find("a")
                    if not ((child.has_attr('class') and child['class'][0]=='mw-disambig') or
                        ('wiktionary' in child['href'] and child['href'] is not None) or 
                        child.has_attr('class') and child['class'][0]=='mw-redirect'):
                        url =(absolute_url + child.get('href'))          
                        final_map={"label" : l.text, 'url':url}
                        final_list.append(final_map)
        return final_list
             

    def _complete_scraping(self,soup:BeautifulSoup):
        total = soup.find('div', {'class': 'mw-parser-output'})
        result = ""        
        for t in total.childGenerator():
            if t.name == "h2" and t.find('span',attrs={"id":["See_also"]}):
                break
            if t.name in ["p", "h2", "h3", "ul","h4"]:
                result += t.get_text() + "\n\n"
        return self._clean(result)      
     
    
    
    async def search(self, text: str) -> ScrapeReply:
        if 'en.wikipedia.org' in text:
            endpoint = text
        else:
            text = text.strip().lower().split()   
            prefix = f'https://en.wikipedia.org/wiki/'
            query = "_".join(text)
            processed_query = '_'.join(query.split())
            endpoint = f'{prefix}{processed_query}'
        req = requests.get(endpoint)
        if req.status_code != 200:
            raise RequestException(f'The Professor could not find the page: {endpoint}.\n Please, make another request.') 
        soup = BeautifulSoup(req.text, 'html.parser')
        first_paragraph = soup.find('div', {'class': 'mw-parser-output'}).find_all('p', limit=5, recursive=False) 
        summary = 'Could not find summary'
        for p in first_paragraph:
            if len(p.text) > 5:
                summary = self._clean(p.text)
        if 'may refer to' in summary:
            logging.info('The term can have several meanings: \n')
            disambiguoslink = self._get_may_refer_to_list(soup)
            return ScrapeReply(language="en", disambiguous=True, data = disambiguoslink)
        return ScrapeReply(language="en", disambiguous=False, data=summary)
            

    async def long_search(self, text: str) -> ScrapeReply:
        result = self._complete_scraping()
        return ScrapeReply(language="it", disambiguos=False, data = result)
    
