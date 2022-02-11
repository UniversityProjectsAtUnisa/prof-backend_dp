from typing import Optional
from os import environ
import re


def sanitize_string(s: Optional[str]) -> Optional[str]:
    if s is None:
        return ""
    s = s.lower().strip()
    s = re.sub('[^A-Za-z0-9]+', ' ', s)
    return s



def get_env_variable(name):
    try:
        return environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        print(message)
        return ""