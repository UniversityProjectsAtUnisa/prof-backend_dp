from fastapi.responses import JSONResponse
from typing import Any
from googletrans import Translator, LANGUAGES
import httpx
from config import TRANSLATE_TIMEOUT
from log_config import init_logger
import logging

logger: logging.Logger = init_logger()
_t = Translator(timeout=httpx.Timeout(TRANSLATE_TIMEOUT))


def chunkize(long_text, characters=1024, sep="."):
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


def translate(content, lang):
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
