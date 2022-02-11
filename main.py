from typing import Optional, Dict, Any
from fastapi import HTTPException, Header
from fastapi import FastAPI, status, Response, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from middlewares.sentry import SentryMiddleware
from middlewares.locale import LocaleMiddleware
from providers import PROVIDERS, is_valid_provider
from common import utils
from datetime import datetime
from translation import translate
from config import DEFAULT_MAX_AGE
from cache import cache

app = FastAPI()

# app.add_middleware(HTTPSRedirectMiddleware)
# app.add_middleware(SentryMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1)
app.add_middleware(LocaleMiddleware)


@app.get("/search", status_code=status.HTTP_200_OK)
async def search(req: Request, res: Response, q: str, long: bool = False, cache_control: Optional[str] = Header(None)):
    q = utils.sanitize_string(q)

    result = None
    if cache_control is None or not (cache_control.startswith("max-age=") or cache_control.startswith("no-cache")):
        result = cache.retrieve(q, long, req.state.lang, DEFAULT_MAX_AGE)
    elif cache_control.startswith("max-age="):
        result = cache.retrieve(q, long, req.state.lang, int(cache_control.replace("max-age=", "")))

    if result is None:
        # Retrieve from services

        result_provider = None
        for p in PROVIDERS:
            # iterate over providers
            try:
                result_provider = p
                result = {
                    "data": "Hello world",
                    "disambiguous": False,
                    "language": "en",
                }
            except:
                pass

        # Find result_provider
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="result_not_found")
        if result['disambiguous']:
            res.status_code = status.HTTP_409_CONFLICT
            return {"data": result['data'], "provider": result_provider}

        result = {
            "data": result["data"],
            "created_at": datetime.now(),
            "original_language": result["language"],
            "current_language": result["language"],
            "provider": result_provider
        }
        cache.add(result)
    if result["original_language"] != result["requested_language"]:
        result = translate(result)
        cache.add(result)
    return result


@app.get("/search/{provider}", status_code=status.HTTP_200_OK)
async def search_provider(req: Request, res: Response, q: str, provider: str, long: bool = False, cache_control: Optional[str] = Header(None)):
    [q, provider] = map(utils.sanitize_string, [q, provider])
    if not is_valid_provider(provider):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="provider_not_available")

    result = None
    if cache_control is None or not (cache_control.startswith("max-age=") or cache_control.startswith("no-cache")):
        result = cache.retrieve(q, long, req.state.lang, DEFAULT_MAX_AGE, provider)
    elif cache_control.startswith("max-age="):
        result = cache.retrieve(q, long, req.state.lang, int(cache_control.replace("max-age=", "")), provider)

    if result is None:
        # Retrieve from services
        result = {
            "data": "Hello world",
            "disambiguous": False,
            "language": "en",
        }
        # Find result_provider
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="result_not_found")
        if result['disambiguous']:
            res.status_code = status.HTTP_409_CONFLICT
            return {"data": result['data'], "provider": provider}

        result = {
            "data": result["data"],
            "created_at": datetime.now(),
            "original_language": result["language"],
            "current_language": result["language"],
            "provider": provider
        }
        cache.add(result)
    if result["original_language"] != result["requested_language"]:
        result = translate(result)
        cache.add(result)
    return result
