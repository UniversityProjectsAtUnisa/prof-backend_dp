import logging, uvicorn
from logging import Logger
from config import LOGGING_LEVEL, UVICORN_LOGGING_FORMAT


def init_logger(name="logger") -> Logger:
    """Function to initialize a custom logger

    Args:
        name (str, optional): The name of the custom logger. Defaults to "logger".

    Returns:
        Logger: the initialized logger
    """
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