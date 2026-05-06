import pytest
import json
from services.cache_service import CacheService

def test_cache_miss_and_hit():
    cache = CacheService()
    # Mock redis client
    class MockRedis:
        def __init__(self):
            self.data = {}
        def get(self, key):
            return self.data.get(key)
        def setex(self, key, ttl, val):
            self.data[key] = val

    cache.client = MockRedis()
    cache.enabled = True
    
    # Test miss
    res = cache.get("sys", "user")
    assert res is None
    assert cache.misses == 1
    assert cache.hits == 0
    
    # Test set and hit
    payload = {"response": "test"}
    cache.set("sys", "user", payload)
    
    res = cache.get("sys", "user")
    assert res == payload
    assert cache.misses == 1
    assert cache.hits == 1

def test_cache_disabled():
    cache = CacheService()
    cache.enabled = False
    
    res = cache.get("sys", "user")
    assert res is None
    cache.set("sys", "user", {"test": "test"})
    assert cache.hits == 0
