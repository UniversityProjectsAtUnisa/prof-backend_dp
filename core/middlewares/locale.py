from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from accept_language import parse_accept_language
from starlette.requests import Request
from googletrans import Translator, LANGUAGES

DEFAULT_LANG = "en"


class LocaleMiddleware(BaseHTTPMiddleware):
    """Middleware that parses the value received in accept-language http header
    in order to extract the requested value.
    After parsing passes that value in request.state.lang
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        lang = parse_accept_language(request.headers.get("accept-language"))
        if len(lang) == 0:
            lang = DEFAULT_LANG
        else:
            lang = lang[0].language
        if lang not in LANGUAGES:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"language_{lang}_not_available")
        request.state.lang = lang
        return await call_next(request)
