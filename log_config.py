import logging, uvicorn
from config import LOGGING_LEVEL, UVICORN_LOGGING_FORMAT


def init_logger(name="logger"):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
    console_formatter = uvicorn.logging.ColourizedFormatter(
        UVICORN_LOGGING_FORMAT,
        style="{", use_colors=True)
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)
    logger.setLevel(LOGGING_LEVEL)
    return logger