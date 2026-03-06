"""
SQLite-backed Cache Service (formerly Redis)
Centralized caching for external API responses
"""

import json
import logging
from typing import Optional, Any
from functools import wraps
import hashlib

from utils.redis_cache import cache_db

logger = logging.getLogger(__name__)

class RedisCacheService:
    """
    Drop-in replacement for RedisCacheService, now backed by SQLite
    Supports automatic serialization and TTL management
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url # Kept for API compatibility
        self.db = cache_db
        logger.info(f"SQLite cache connected: cache.sqlite")
    
    def get(self, key: str) -> Optional[Any]:
        value_bytes = self.db.get(key)
        if value_bytes:
            try:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value_bytes.decode('utf-8'))
            except Exception as e:
                logger.error(f"JSON decode error for key {key}: {e}")
                return None
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            serialized = json.dumps(value).encode('utf-8')
            self.db.set(key, serialized, ttl)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache SET error: {str(e)}")
            return False
    
    def delete(self, key: str):
        result = self.db.delete(key)
        if result:
            logger.debug(f"Cache DELETE: {key}")
        return result
    
    def clear_pattern(self, pattern: str):
        count = self.db.clear_pattern(pattern)
        logger.info(f"Cleared {count} keys matching '{pattern}'")
        return count
    
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        parts = [str(arg) for arg in args]
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        combined = ":".join(parts)
        hash_value = hashlib.md5(combined.encode()).hexdigest()[:12]
        return f"{prefix}:{hash_value}"


def cached(prefix: str, ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache = getattr(self, 'cache', None)
            if not cache:
                return await func(self, *args, **kwargs)
            
            cache_key = RedisCacheService.generate_key(prefix, *args, **kwargs)
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = await func(self, *args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator


# Singleton instance
_cache_instance: Optional[RedisCacheService] = None

def get_cache_service(redis_url: str = None) -> RedisCacheService:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCacheService(redis_url)
    return _cache_instance
