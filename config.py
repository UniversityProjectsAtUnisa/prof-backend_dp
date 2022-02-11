from os import getenv, getcwd, path
from common.utils import get_env_variable
from dotenv import load_dotenv
env_path = path.join(getcwd(), '.env')
load_dotenv(dotenv_path=env_path)

SENTRY_DSN = get_env_variable("SENTRY_DSN")
DEFAULT_MAX_AGE = 5000
TRANSLATE_TIMEOUT = 10000