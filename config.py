from os import getcwd, path
from common.utils import get_env_variable
from dotenv import load_dotenv
import logging
env_path = path.join(getcwd(), '.env')
load_dotenv(dotenv_path=env_path)

SENTRY_DSN = get_env_variable("SENTRY_DSN")
MARCO_PORT = get_env_variable("MARCO_PORT")
TRECCANI_PORT = get_env_variable("TRECCANI_PORT")
WIKIPEDIA_EN_PORT = get_env_variable("WIKIPEDIA_EN_PORT")
WIKIPEDIA_IT_PORT = get_env_variable("WIKIPEDIA_IT_PORT")
UVICORN_LOGGING_FORMAT = get_env_variable("UVICORN_LOGGING_FORMAT")
LOGGING_FORMAT = get_env_variable("LOGGING_FORMAT")
_LOGGING_LEVEL = get_env_variable("LOGGING_LEVEL", "WARNING")
LOGGING_LEVEL = getattr(logging, _LOGGING_LEVEL.upper())
DEFAULT_MAX_AGE = 5000
TRANSLATE_TIMEOUT = 10000