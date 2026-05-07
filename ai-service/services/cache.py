import hashlib
import json
import os

import redis


class AiCache:
    def __init__(self, redis_url: str | None = None, ttl: int = 900):
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.ttl = ttl
        self._client = None
        try:
            self._client = redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
        except Exception:
            self._client = None
        self._hits = 0
        self._misses = 0

    def _normalize_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, key: str):
        if not self._client:
            self._misses += 1
            return None
        value = self._client.get(self._normalize_key(key))
        if value is None:
            self._misses += 1
            return None
        self._hits += 1
        try:
            return json.loads(value)
        except Exception:
            return None

    def set(self, key: str, value: dict):
        if not self._client:
            return
        self._client.set(self._normalize_key(key), json.dumps(value), ex=self.ttl)

    def stats(self) -> dict:
        return {
            "enabled": bool(self._client),
            "hits": self._hits,
            "misses": self._misses,
            "ttl_seconds": self.ttl,
        }
