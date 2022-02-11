from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from accept_language import parse_accept_language
from starlette.requests import Request
from googletrans import Translator, LANGUAGES

DEFAULT_LANG = "en"


class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        lang = parse_accept_language(request.headers.get("accept-language"))
        if len(lang) == 0:
            lang = DEFAULT_LANG
        lang = lang[0].language
        if lang not in LANGUAGES:
            raise HTTPException(status_code=422, detail="language_not_available")
        request.state.lang = lang
        return await call_next(request)
