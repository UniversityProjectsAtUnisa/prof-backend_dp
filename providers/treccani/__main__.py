import logging
from definitions.scraper.server import ScraperServer
from config import TRECCANI_PORT, LOGGING_FORMAT, LOGGING_LEVEL
from . import ScraperTreccani
from config import LOGGING_LEVEL

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
    ScraperServer(ScraperTreccani(), port=TRECCANI_PORT).run()
