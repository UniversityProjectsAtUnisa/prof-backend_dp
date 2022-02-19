import logging
from definitions.scraper.server import ScraperServer
from config import WIKIPEDIA_EN_PORT, LOGGING_FORMAT, LOGGING_LEVEL
from . import ScraperWikipediaEN
from config import LOGGING_LEVEL

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
    ScraperServer(ScraperWikipediaEN(), port=WIKIPEDIA_EN_PORT).run()
