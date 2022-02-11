from fastapi.responses import JSONResponse
from typing import Any
from googletrans import Translator, LANGUAGES
import httpx
from config import TRANSLATE_TIMEOUT

_t = Translator(timeout=httpx.Timeout(TRANSLATE_TIMEOUT))


def translate(content):
    current = content["current_language"]
    requested = content["requested_language"]
    if current != requested:
        try:
            translated_text = _t.translate(content["data"], dest=requested, src=current).text
            content = content.copy()
            content['current_language'] = requested
            content["data"] = translated_text
        finally:
            return content
