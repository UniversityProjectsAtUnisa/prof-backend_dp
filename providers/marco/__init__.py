from definitions.scraper import ScraperBase, ScrapeReply, DisamiguousLink
import logging


class Marco(ScraperBase):
    async def search(self, text: str) -> ScrapeReply:
        logging.info("RICEVUTO!")
        return ScrapeReply(language="it", disambiguous=False, data=f'ciao ciao. ciao ciao '*500)

    async def long_search(self, text: str) -> ScrapeReply:
        logging.info("RICEVUTO!")
        return ScrapeReply(language="it", disambiguous=True, data=f'{text} è molto molto molto bello',
                           disambiguous_data=[DisamiguousLink(label=f"{text} 1", url="https://www.google.com/images")] * 3)

