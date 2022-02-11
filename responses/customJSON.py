from fastapi.responses import JSONResponse
from typing import Any
from googletrans import Translator, LANGUAGES
import httpx

_t = Translator(timeout=httpx.Timeout(10000))


class TranslatedJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        # content['is_success'] = 'error' not in content
        # print(_t.translate(content, dest="en"))
        current = content["current_language"]
        requested = content["requested_language"]
        if not current!=requested:
          try:
              content['text'] = _t.translate(content["text"], requested).text
          except:
              pass
        return super().render(content)
