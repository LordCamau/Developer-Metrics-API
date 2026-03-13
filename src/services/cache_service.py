import json
import redis

from src.core.config import get_settings


class CacheService:
    def __init__(self):
        self.settings = get_settings()
        self._client = None

    def _get_client(self):
        if not self.settings.REDIS_ENABLED:
            return None
        if self._client is None:
            try:
                self._client = redis.Redis.from_url(self.settings.REDIS_URL, decode_responses=True)
                self._client.ping()
            except Exception:
                self._client = None
        return self._client

    def get_json(self, key: str):
        client = self._get_client()
        if not client:
            return None
        try:
            value = client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    def set_json(self, key: str, value: dict, ttl_seconds: int | None = None):
        client = self._get_client()
        if not client:
            return
        try:
            ttl = ttl_seconds or self.settings.CACHE_TTL_SECONDS
            client.setex(key, ttl, json.dumps(value))
        except Exception:
            return
