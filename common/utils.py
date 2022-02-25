from typing import Optional
from os import environ
import re


def sanitize_string(s: Optional[str]) -> Optional[str]:
    """Utility function to remove unwanted characters from strings

    Args:
        s (Optional[str]): the string to sanitize

    Returns:
        Optional[str]: the sanitized string
    """
    if s is None:
        return ""
    s = s.lower().strip()
    s = re.sub('[^A-Za-z0-9]+', ' ', s)
    return s


def get_env_variable(name: str, default=None) -> Optional[str]:
    """Utility function to retrieve values of environment variables.

    Args:
        name (str): the environment variable to retrieve
        default (str, optional): The default value if the environment variable is not defined. 
            Defaults to None.

    Returns:
        Optional[str]: The value of the retrieved environment variable
    """
    try:
        if default is not None:
            return environ.get(name, default)
        return environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        print(message)
        return ""
