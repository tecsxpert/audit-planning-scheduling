import json
import hashlib
import redis
import logging
from services.config import settings

LOGGER = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.enabled = bool(settings.redis_url)
        self.client = redis.Redis.from_url(settings.redis_url) if self.enabled else None
        self.ttl = 900  # 15 minutes
        self.hits = 0
        self.misses = 0

    def _generate_key(self, system_prompt: str, user_prompt: str) -> str:
        content = f"{system_prompt}|{user_prompt}".encode('utf-8')
        digest = hashlib.sha256(content).hexdigest()
        return f"ai_cache:{digest}"

    def get(self, system_prompt: str, user_prompt: str) -> dict | None:
        if not self.enabled:
            return None
            
        key = self._generate_key(system_prompt, user_prompt)
        try:
            cached = self.client.get(key)
            if cached:
                self.hits += 1
                return json.loads(cached)
        except Exception as e:
            LOGGER.warning("Redis get failed: %s", e)
            
        self.misses += 1
        return None

    def set(self, system_prompt: str, user_prompt: str, response: dict) -> None:
        if not self.enabled:
            return
            
        key = self._generate_key(system_prompt, user_prompt)
        try:
            self.client.setex(key, self.ttl, json.dumps(response))
        except Exception as e:
            LOGGER.warning("Redis set failed: %s", e)

cache_service = CacheService()
