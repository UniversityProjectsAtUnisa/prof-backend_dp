from fastapi import HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from accept_language import parse_accept_language
from starlette.requests import Request
from googletrans import Translator, LANGUAGES
from fastapi.routing import APIRoute
from typing import Callable
import json
from starlette.responses import JSONResponse


_default_lang = "en"

_translator = Translator(timeout=10000)

# If header contains lang
# detects language. If wrong translates it


class TranslatedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            lang = parse_accept_language(
                request.headers.get("accept-language"))
            if len(lang) == 0:
                lang = _default_lang
            lang = lang[0].language
            if lang not in LANGUAGES:
                raise HTTPException(
                    status_code=422, detail="language_not_available")
            res: Response = await original_route_handler(request)
            # return res
            print(await res())
            try:
                return _translator.translate(res.body, lang)
            except:
                return res

        return custom_route_handler
