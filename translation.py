from fastapi.responses import JSONResponse
from typing import Any
from googletrans import Translator, LANGUAGES
import httpx

_t = Translator(timeout=httpx.Timeout(10000))


def translate(content):
    current = content["current_language"]
    requested = content["requested_language"]
    if not current != requested:
        try:
            translated_text = _t.translate(content["text"], requested).text
            content = content.copy()
            content["text"] = translated_text
        finally:
            return content
