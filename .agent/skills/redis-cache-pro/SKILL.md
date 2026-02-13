---
name: redis-cache-pro
description: Redis caching patterns for FastAPI applications. Covers connection pooling, serialization, TTL strategies, and production deployment. Use when implementing caching, session storage, or rate limiting.
metadata:
  model: opus
---

# Redis Cache Pro Skill

Expert Redis integration for FastAPI applications with production-ready patterns.

## When to Use
- Implementing caching layers
- Session storage
- Rate limiting
- Pub/Sub messaging
- Leaderboards/counters

## Core Patterns

### 1. Connection Management

```python
from redis import Redis
from redis.connection import ConnectionPool
from functools import lru_cache

@lru_cache()
def get_redis_pool() -> ConnectionPool:
    """Singleton connection pool"""
    return ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        max_connections=50,
        decode_responses=False  # Binary for pickle
    )

def get_redis() -> Redis:
    """Get Redis client with pooling"""
    return Redis(connection_pool=get_redis_pool())
```

### 2. Serialization Strategies

**For Pydantic Models:**
```python
import json
from pydantic import BaseModel

def cache_pydantic(key: str, model: BaseModel, ttl: int = 3600):
    redis = get_redis()
    redis.setex(key, ttl, model.model_dump_json())

def get_pydantic(key: str, model_class: type[BaseModel]):
    redis = get_redis()
    data = redis.get(key)
    if not data:
        return None
    return model_class.model_validate_json(data)
```

**For Complex Objects:**
```python
import pickle

def cache_object(key: str, obj: Any, ttl: int = 3600):
    redis = get_redis()
    redis.setex(key, ttl, pickle.dumps(obj))

def get_object(key: str):
    redis = get_redis()
    data = redis.get(key)
    if not data:
        return None
    return pickle.loads(data)
```

### 3. TTL Strategies

```python
from enum import IntEnum

class CacheTTL(IntEnum):
    """Standard TTL values"""
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    
    # Feature-specific
    SCORING_RESULT = 3600  # 1 hour
    SESSION = 86400  # 1 day
    RATE_LIMIT = 60  # 1 minute
```

### 4. Cache-Aside Pattern

```python
from typing import Optional, Callable

async def get_or_compute(
    key: str,
    compute_fn: Callable,
    ttl: int = 3600,
    serializer=pickle
) -> Any:
    """
    Cache-aside pattern with async support.
    
    1. Try cache
    2. If miss, compute
    3. Store in cache
    4. Return result
    """
    redis = get_redis()
    
    # Try cache
    cached = redis.get(key)
    if cached:
        return serializer.loads(cached)
    
    # Compute
    result = await compute_fn() if asyncio.iscoroutinefunction(compute_fn) else compute_fn()
    
    # Cache
    redis.setex(key, ttl, serializer.dumps(result))
    
    return result
```

### 5. Namespace Keys

```python
class CacheKey:
    """Centralized key management"""
    
    @staticmethod
    def scoring_result(idea_name: str) -> str:
        return f"score:v2:{idea_name}"
    
    @staticmethod
    def explanation(idea_name: str, question_hash: str) -> str:
        return f"explain:v2:{idea_name}:{question_hash}"
    
    @staticmethod
    def rate_limit(user_id: str, endpoint: str) -> str:
        return f"ratelimit:{endpoint}:{user_id}"
```

### 6. Error Handling

```python
from redis.exceptions import RedisError, ConnectionError
import logging

logger = logging.getLogger(__name__)

def safe_cache_get(key: str, default=None):
    """Safe cache read with fallback"""
    try:
        redis = get_redis()
        data = redis.get(key)
        if data:
            return pickle.loads(data)
    except RedisError as e:
        logger.warning(f"Redis error on GET {key}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error on GET {key}: {e}")
    
    return default

def safe_cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Safe cache write"""
    try:
        redis = get_redis()
        redis.setex(key, ttl, pickle.dumps(value))
        return True
    except RedisError as e:
        logger.warning(f"Redis error on SET {key}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error on SET {key}: {e}")
        return False
```

### 7. FastAPI Dependency

```python
from fastapi import Depends

async def get_cache_client() -> Redis:
    """FastAPI dependency for Redis"""
    return get_redis()

# Usage in route
@router.post("/example")
async def example(cache: Redis = Depends(get_cache_client)):
    cache.get("key")
```

## Production Deployment

### Docker Compose
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  redis_data:
```

### Environment Variables
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Optional
REDIS_SSL=false
```

### Health Check
```python
@router.get("/health/redis")
async def redis_health():
    try:
        redis = get_redis()
        redis.ping()
        return {"status": "healthy", "service": "redis"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Advanced Patterns

### Rate Limiting
```python
def check_rate_limit(key: str, limit: int, window: int) -> bool:
    """
    Token bucket rate limiting.
    
    Args:
        key: Unique identifier (e.g., user_id)
        limit: Max requests
        window: Time window in seconds
    
    Returns:
        True if allowed, False if rate limited
    """
    redis = get_redis()
    
    current = redis.incr(key)
    
    if current == 1:
        redis.expire(key, window)
    
    return current <= limit
```

### Distributed Locks
```python
from redis.lock import Lock

def with_distributed_lock(key: str, timeout: int = 10):
    """Distributed lock decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            redis = get_redis()
            lock = Lock(redis, key, timeout=timeout)
            
            if lock.acquire(blocking=False):
                try:
                    return await func(*args, **kwargs)
                finally:
                    lock.release()
            else:
                raise RuntimeError(f"Could not acquire lock: {key}")
        
        return wrapper
    return decorator
```

## Migration from In-Memory

```python
# Before (in-memory)
cache: Dict[str, Any] = {}

# After (Redis)
from utils.redis_cache import safe_cache_get, safe_cache_set, CacheKey

# Get
result = safe_cache_get(CacheKey.scoring_result(idea_name))

# Set
safe_cache_set(
    CacheKey.scoring_result(idea_name),
    scoring_result,
    ttl=CacheTTL.SCORING_RESULT
)
```

## Testing

```python
import pytest
from fakeredis import FakeRedis

@pytest.fixture
def mock_redis():
    return FakeRedis()

def test_cache_set_get(mock_redis):
    safe_cache_set("key", "value", mock_redis)
    assert safe_cache_get("key", mock_redis) == "value"
```

## Cost Optimization

- Use TTLs aggressively
- Set `maxmemory-policy` to `allkeys-lru`
- Monitor memory usage
- Consider Redis Cloud free tier (30MB)

## When NOT to Use Redis

- For persistent data (use PostgreSQL)
- For large files (use S3)
- For <100 req/sec (in-memory might be fine)
