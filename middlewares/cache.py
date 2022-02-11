from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

cache = {}
# Cosa usare come chiave della cache? Provider mancante ecc

# No cache skips
# maxage
class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        qp = request.query_params
        
