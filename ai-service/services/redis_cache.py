"""
Redis Cache Service
Centralized caching for external API responses
"""

import json
import logging
from typing import Optional, Any
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class RedisCacheService:
    """
    Redis-based caching layer for API responses
    Supports automatic serialization and TTL management
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Redis client with fallback"""
        try:
            import redis
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.client.ping()
            logger.info(f"Redis cache connected: {self.redis_url}")
        except Exception as e:
            logger.warning(f"Redis unavailable: {str(e)} - caching disabled")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value by key
        Returns None if not found or Redis unavailable
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set cached value with TTL (default 1 hour)
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds
        """
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {str(e)}")
            return False
    
    def delete(self, key: str):
        """Delete cached value"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern (e.g., 'youtube:*')"""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                count = self.client.delete(*keys)
                logger.info(f"Cleared {count} keys matching '{pattern}'")
                return count
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR error: {str(e)}")
            return 0
    
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate deterministic cache key from arguments
        
        Example:
            generate_key("youtube", keyword="AI", limit=10)
            -> "youtube:3a5f8b2c..."
        """
        # Combine all args and kwargs into a stable string
        parts = [str(arg) for arg in args]
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        combined = ":".join(parts)
        
        # Hash for consistent key length
        hash_value = hashlib.md5(combined.encode()).hexdigest()[:12]
        
        return f"{prefix}:{hash_value}"


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching async function results in Redis
    
    Usage:
        @cached(prefix="youtube", ttl=1800)
        async def search_videos(self, keyword: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Get cache service (assume it's on self)
            cache = getattr(self, 'cache', None)
            if not cache:
                # No cache available, call function directly
                return await func(self, *args, **kwargs)
            
            # Generate cache key
            cache_key = RedisCacheService.generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - call function
            result = await func(self, *args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Singleton instance
_cache_instance: Optional[RedisCacheService] = None


def get_cache_service(redis_url: str = None) -> RedisCacheService:
    """Get or create cache service singleton"""
    global _cache_instance
    
    if _cache_instance is None:
        from core.config import get_settings
        settings = get_settings()
        url = redis_url or settings.REDIS_URL
        _cache_instance = RedisCacheService(url)
    
    return _cache_instance
