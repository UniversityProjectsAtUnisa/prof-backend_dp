from fastapi.responses import JSONResponse
from typing import Any
from googletrans import Translator, LANGUAGES
import httpx
from config import TRANSLATE_TIMEOUT

_t = Translator(timeout=httpx.Timeout(TRANSLATE_TIMEOUT))


def chunkize(long_text, characters=1024, sep="."):
    chunks = []
    i = 0
    j = min(characters, len(long_text))
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


def translate(content):
    current = content["current_language"]
    requested = content["requested_language"]

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
        finally:
            return content
