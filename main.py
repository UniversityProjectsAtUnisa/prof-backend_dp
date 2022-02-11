from collections import defaultdict
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header
from asgi_tools import response
from fastapi import APIRouter, FastAPI, status, Response, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from middlewares.sentry import SentryMiddleware
from middlewares.cache import CacheMiddleware
from middlewares.locale import LocaleMiddleware, DEFAULT_LANG
from middlewares.qp_string_sanitizer import QPStringSanitizerMiddleware
from routes.translation import TranslatedRoute
from providers import PROVIDERS, is_valid_provider
from responses.customJSON import TranslatedJSONResponse
from common import utils
from datetime import datetime
from translation import translate
from config import DEFAULT_MAX_AGE

app = FastAPI()
# router = APIRouter()
# router = APIRouter(route_class=TranslatedRoute)

# app.add_middleware(HTTPSRedirectMiddleware)
# app.add_middleware(SentryMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1)
app.add_middleware(LocaleMiddleware)
# app.add_middleware(QPStringSanitizerMiddleware)
# app.add_middleware(CacheMiddleware)

# TODO: Magari fare due endpoint (/search e /search/{provider})
# /search cercherebbe tra trutti i provider finché non viene trovato un risultato
#


def nested_dict(): return defaultdict(nested_dict)


cache = nested_dict()


def retrieve_from_cache(q: str, provider: str, long: bool, lang: str, maxage: Optional[int] = None) -> Dict[str, Any]:
    # {q:provider:long:lang:{data:"", created_at:"", original_language:"", current_language="", provider=""}}
    mindate = None
    if maxage is not None:
        mindate = datetime.now() - datetime.timedelta(seconds=maxage)
    if q not in cache:
        return None
    values = []
    if provider == "":
        for v in cache[q].values():
            if long in v:
                values.append(v[long])
        if len(values) == 0:
            return None
    else:
        if provider not in cache[q] or long not in cache[q][provider]:
            return None
        values = [cache[q][provider][long]]

    for v in values:
        if lang not in v:
            continue
        if mindate is not None and v[lang]["created_at"] >= mindate:
            return v[lang]

    for v in values:
        for lang, res in v.items():
            if mindate is not None and res["original_language"] == res["current_language"] and res["created_at"] >= mindate:
                return res

    return None


def clear_cache(seconds: int):
    maxdate = datetime.now() - datetime.timedelta(seconds=seconds)
    for q in cache.values():
        for provider in q.values():
            for long in provider.values():
                for lang in long.values():
                    if lang["created_at"] < maxdate:
                        del long[lang]


def add_to_cache(q: str, provider: str, long: bool, lang: str, data: Dict[str, Any]):
    old_data = cache[q][provider][long][lang]
    cache[q][provider][long][lang] = data
    return old_data


# @app.get("/search", status_code=status.HTTP_200_OK, response_class=TranslatedJSONResponse)
@app.get("/search", status_code=status.HTTP_200_OK)
def root(req: Request, res: Response, q: str, provider: str = None, long: bool = False, cache_control: Optional[str] = Header(None)):
    [q, provider] = map(utils.sanitize_string, [q, provider])
    if provider != "" and not is_valid_provider(provider):
        raise HTTPException(status_code=422, detail="provider_not_available")

    result = None
    if cache_control is None or not (cache_control.startswith("max-age=") or cache_control.startswith("no-cache")):
        result, result_provider = retrieve_from_cache(
            q, provider, long, req.state.lang, DEFAULT_MAX_AGE)
    elif cache_control.startswith("max-age="):
        result, result_provider = retrieve_from_cache(q, provider, long, req.state.lang, int(
            cache_control.replace("max-age=", "")))

    if result is None:
        # Retrieve from services
        result = {
            "data": "Hello world",
            "language": "en",
        }
        # create new omogeneous result before adding to cache
        add_to_cache(result)
    if result["original_language"] != result["requested_language"]:
        result = translate(result)
        add_to_cache(result)
    return result

    # return it so that TranslatedJSONResponse translates it
    # Remove TranslatedJSONResponse to cache translated responses too
    return result
    #
    # if q not in cache or:

    return {
        "current_language": "en",
        "original_language": "en",
        "requested_language": req.state.lang,
        "text": q
    }
    providers = pick_valid_providers(provider.split(" "))

    for p in providers:
        found = p.search(q, long)
        if found is not None:
            return found

    return {"message": "resource_unavailable"}

    return {
        "q": q,
        "provider": provider,
        "long": long
    }

# app.include_router(router)
