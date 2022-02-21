import logging
from definitions.scraper.server import ScraperServer
from config import LOGGING_FORMAT, LOGGING_LEVEL
from . import ScraperWikipediaIT
from .. import providers_port_mapping
from config import LOGGING_LEVEL

if __name__ == '__main__':
    logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
    ScraperServer(ScraperWikipediaIT(), port=providers_port_mapping["wikipediait"]).run()
