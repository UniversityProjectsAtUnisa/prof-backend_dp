from typing import List, Dict, Any
from googletrans import Translator
import httpx
from config import TRANSLATE_TIMEOUT
from log_config import init_logger
import logging

logger: logging.Logger = init_logger()
_t = Translator(timeout=httpx.Timeout(TRANSLATE_TIMEOUT))


def chunkize(long_text: str, characters=1024, sep=".") -> List[str]:
    """Function used to separate a long text in smaller chunks before translation.
    Each chunks is long at most 'characters' characters and ends with 'sep' character.

    Args:
        long_text (str): The text to separate in chunks
        characters (int, optional): The max length of each chunk. Defaults to 1024.
        sep (str, optional): The ending character of every chunk. Defaults to ".".

    Returns:
        List: _description_
    """
    if len(long_text) < characters:
        return [long_text]
    chunks = []
    i = 0
    j = characters
    while j < len(long_text):
        k = j
        while long_text[k] != sep and k > i:
            k -= 1
        if i == k:
            k = j
        chunks.append(long_text[i:k])
        i = k + 1
        j = min(i + characters, len(long_text))
    return chunks


def translate(content: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """Translate function that translates content to a desired language.
    The text to be translated must be in content['data']
    The language of the text must be in content['current_languange']

    Args:
        content (Dict[str, Any]): The content to be translated
        lang (str): The target language

    Returns:
        Dict[str, Any]: The content with translated data and current_language = lang
    """
    current = content["current_language"]
    requested = lang
    logger.info(f"TRANSLATION FROM {current} TO {requested}")

    if current != requested:
        chunks = chunkize(content["data"])
        try:
            translated_chunks = []
            for chunk in chunks:
                translated = _t.translate(chunk, dest=requested, src=current).text
                translated_chunks.append(translated)
            content = content.copy()
            content['current_language'] = requested
            content["data"] = "".join(translated_chunks)
        except Exception as e:
            logger.error(e)
        finally:
            return content
