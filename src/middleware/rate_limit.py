from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis

from src.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.client = None
        if self.settings.REDIS_ENABLED:
            try:
                self.client = redis.Redis.from_url(self.settings.REDIS_URL, decode_responses=True)
                self.client.ping()
            except Exception:
                self.client = None

    async def dispatch(self, request: Request, call_next):
        if not self.client:
            return await call_next(request)

        identifier = request.client.host if request.client else "anonymous"
        key = f"rate:{identifier}:{request.url.path}"
        try:
            current = self.client.incr(key)
            if current == 1:
                self.client.expire(key, self.settings.RATE_LIMIT_WINDOW_SECONDS)
            if current > self.settings.RATE_LIMIT_REQUESTS:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                )
        except Exception:
            return await call_next(request)

        return await call_next(request)
