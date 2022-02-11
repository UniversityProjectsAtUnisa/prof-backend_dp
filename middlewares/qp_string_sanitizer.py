from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from common import utils


class QPStringSanitizerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        qp = request.query_params
        print(qp.__dict__)
        for k in request.query_params:
            if isinstance(qp[k], str):
                request.query_params[k] = utils.sanitize_string(qp[k])
        return await call_next(request)
