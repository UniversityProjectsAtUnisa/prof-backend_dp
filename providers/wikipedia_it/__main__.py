import logging
from definitions.scraper.server import ScraperServer
from config import WIKIPEDIA_IT_PORT, LOGGING_FORMAT, LOGGING_LEVEL
from . import ScraperWikipediaIT
from config import LOGGING_LEVEL

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
    ScraperServer(ScraperWikipediaIT(), port=WIKIPEDIA_IT_PORT).run()
