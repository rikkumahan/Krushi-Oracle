"""
Redis Cache Utilities for IdeaLab Scoring V2

Production-ready Redis caching with:
- Connection pooling
- Safe error handling
- Pydantic serialization
- TTL management
- Key namespacing
"""

from typing import Optional, Any
from functools import lru_cache
import pickle
import logging
from enum import IntEnum

from redis import Redis
from redis.connection import ConnectionPool
from redis.exceptions import RedisError
from pydantic import BaseModel

from core.config import get_settings

logger = logging.getLogger(__name__)

# Fallback in-memory cache for development/test environments
_IN_MEMORY_CACHE = {}
_IN_MEMORY_EXPIRY = {} # Simple TTL tracking: {key: expiry_timestamp}


# ==================== TTL Constants ====================

class CacheTTL(IntEnum):
    """Standard TTL values in seconds"""
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    
    # Feature-specific
    SCORING_RESULT = 3600  # 1 hour - reasonable for idea scores
    EXPLANATION = 1800  # 30 min - LLM responses can be cached
    RATE_LIMIT = 60  # 1 minute


# ==================== Connection Management ====================

@lru_cache()
def get_redis_pool() -> Optional[ConnectionPool]:
    """
    Get singleton Redis connection pool.
    
    Returns None if Redis is not configured (graceful degradation).
    """
    settings = get_settings()
    
    if not settings.REDIS_HOST:
        logger.warning("Redis not configured - caching disabled")
        return None
    
    try:
        return ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            max_connections=50,
            decode_responses=False,  # Binary mode for pickle
            socket_connect_timeout=5,
            socket_timeout=5
        )
    except Exception as e:
        logger.error(f"Failed to create Redis pool: {e}")
        return None


def get_redis() -> Optional[Redis]:
    """
    Get Redis client with connection pooling.
    
    Returns None if Redis is not available (fail gracefully).
    """
    pool = get_redis_pool()
    if not pool:
        return None
    
    return Redis(connection_pool=pool)


# ==================== Key Management ====================

class CacheKey:
    """Centralized cache key management with namespacing"""
    
    PREFIX = "idealab:v2"
    
    @classmethod
    def scoring_result(cls, idea_name: str) -> str:
        """Key for scoring results"""
        # Sanitize idea name for Redis key
        safe_name = idea_name.replace(":", "_").replace(" ", "_")
        return f"{cls.PREFIX}:score:{safe_name}"
    
    @classmethod
    def explanation(cls, idea_name: str, question: str) -> str:
        """Key for explanation responses (with question hash)"""
        import hashlib
        question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        safe_name = idea_name.replace(":", "_").replace(" ", "_")
        return f"{cls.PREFIX}:explain:{safe_name}:{question_hash}"
    
    @classmethod
    def rate_limit(cls, user_id: str, endpoint: str) -> str:
        """Key for rate limiting"""
        return f"{cls.PREFIX}:ratelimit:{endpoint}:{user_id}"


# ==================== Safe Cache Operations ====================

def safe_cache_get(key: str, default: Any = None) -> Any:
    """
    Safely get value from cache.
    
    Returns default if cache miss or error.
    Never raises exceptions.
    """
    try:
        redis = get_redis()
        if not redis:
            # Fallback to in-memory
            val = _IN_MEMORY_CACHE.get(key, default)
            
            # Simple expiry check
            import time
            expiry = _IN_MEMORY_EXPIRY.get(key)
            if expiry and time.time() > expiry:
                _IN_MEMORY_CACHE.pop(key, None)
                _IN_MEMORY_EXPIRY.pop(key, None)
                return default
                
            return val
        
        data = redis.get(key)
        if data is None:
            return default
        
        return pickle.loads(data)
        
    except RedisError as e:
        logger.warning(f"Redis error on GET {key}: {e}. Falling back to in-memory.")
        # Fallback to in-memory on redis error
        return _IN_MEMORY_CACHE.get(key, default)
    except Exception as e:
        logger.error(f"Unexpected error on GET {key}: {e}")
        return default


def safe_cache_set(key: str, value: Any, ttl: int = CacheTTL.HOUR) -> bool:
    """
    Safely set value in cache.
    
    Returns True on success, False on failure.
    Never raises exceptions.
    """
    try:
        redis = get_redis()
        if not redis:
            # Fallback to in-memory
            _IN_MEMORY_CACHE[key] = value
            import time
            _IN_MEMORY_EXPIRY[key] = time.time() + ttl
            return True
        
        redis.setex(key, ttl, pickle.dumps(value))
        return True
        
    except RedisError as e:
        logger.warning(f"Redis error on SET {key}: {e}. Falling back to in-memory.")
        # Fallback to in-memory on redis error
        _IN_MEMORY_CACHE[key] = value
        import time
        _IN_MEMORY_EXPIRY[key] = time.time() + ttl
        return True
    except Exception as e:
        logger.error(f"Unexpected error on SET {key}: {e}")
        return False


def safe_cache_delete(key: str) -> bool:
    """
    Safely delete key from cache.
    
    Returns True on success, False on failure.
    """
    try:
        redis = get_redis()
        if not redis:
            return False
        
        redis.delete(key)
        return True
        
    except RedisError as e:
        logger.warning(f"Redis error on DELETE {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error on DELETE {key}: {e}")
        return False


# ==================== Pydantic Model Caching ====================

def cache_pydantic_model(key: str, model: BaseModel, ttl: int = CacheTTL.HOUR) -> bool:
    """
    Cache a Pydantic model as JSON.
    
    More efficient than pickle for Pydantic models.
    """
    try:
        redis = get_redis()
        if not redis:
            return False
        
        redis.setex(key, ttl, model.model_dump_json())
        return True
        
    except Exception as e:
        logger.error(f"Error caching Pydantic model {key}: {e}")
        return False


def get_pydantic_model(key: str, model_class: type[BaseModel]) -> Optional[BaseModel]:
    """
    Get a Pydantic model from cache.
    
    Returns None if not found or error.
    """
    try:
        redis = get_redis()
        if not redis:
            return None
        
        data = redis.get(key)
        if not data:
            return None
        
        return model_class.model_validate_json(data)
        
    except Exception as e:
        logger.error(f"Error retrieving Pydantic model {key}: {e}")
        return None


# ==================== Rate Limiting ====================

def check_rate_limit(key: str, limit: int, window: int = CacheTTL.MINUTE) -> bool:
    """
    Check if rate limit is exceeded.
    
    Args:
        key: Unique identifier (e.g., user_id + endpoint)
        limit: Maximum requests allowed
        window: Time window in seconds
    
    Returns:
        True if allowed (under limit), False if rate limited
    """
    try:
        redis = get_redis()
        if not redis:
            return True  # Allow if Redis unavailable
        
        current = redis.incr(key)
        
        # Set expiry on first request
        if current == 1:
            redis.expire(key, window)
        
        return current <= limit
        
    except Exception as e:
        logger.error(f"Error checking rate limit {key}: {e}")
        return True  # Fail open


# ==================== Health Check ====================

def redis_health_check() -> dict:
    """
    Check Redis connection health.
    
    Returns status dict for health endpoint.
    """
    try:
        redis = get_redis()
        if not redis:
            return {
                "status": "not_configured",
                "message": "Redis is not configured"
            }
        
        redis.ping()
        return {
            "status": "healthy",
            "service": "redis"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
