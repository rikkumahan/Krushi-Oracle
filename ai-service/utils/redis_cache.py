"""
Redis Cache Utilities for IdeaLab Scoring V2
(Now backed by SQLite for simplified local deployment)
"""

from typing import Optional, Any
import pickle
import logging
from enum import IntEnum
import sqlite3
import time
import threading

from pydantic import BaseModel
from core.config import get_settings

logger = logging.getLogger(__name__)

# ==================== TTL Constants ====================

class CacheTTL(IntEnum):
    """Standard TTL values in seconds"""
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    
    # Feature-specific
    SCORING_RESULT = 3600  # 1 hour
    EXPLANATION = 1800  # 30 min
    RATE_LIMIT = 60  # 1 minute


# ==================== Key Management ====================

class CacheKey:
    """Centralized cache key management with namespacing"""
    
    PREFIX = "idealab:v2"
    
    @classmethod
    def scoring_result(cls, idea_name: str) -> str:
        safe_name = idea_name.replace(":", "_").replace(" ", "_")
        return f"{cls.PREFIX}:score:{safe_name}"
    
    @classmethod
    def explanation(cls, idea_name: str, question: str) -> str:
        import hashlib
        question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        safe_name = idea_name.replace(":", "_").replace(" ", "_")
        return f"{cls.PREFIX}:explain:{safe_name}:{question_hash}"
    
    @classmethod
    def rate_limit(cls, user_id: str, endpoint: str) -> str:
        return f"{cls.PREFIX}:ratelimit:{endpoint}:{user_id}"


# ==================== SQLite Backend ====================

class SQLiteCacheBackend:
    def __init__(self, db_path="cache.sqlite"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    @property
    def conn(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = sqlite3.connect(self.db_path, timeout=10)
        return self._local.conn

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            conn.execute('PRAGMA synchronous=NORMAL;')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    expire_at REAL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_expire ON cache(expire_at)')
        conn.close()

    def get(self, key: str) -> Optional[bytes]:
        cursor = self.conn.execute('SELECT value, expire_at FROM cache WHERE key = ?', (key,))
        row = cursor.fetchone()
        if row:
            value, expire_at = row
            if expire_at is None or expire_at > time.time():
                return value
            else:
                self.delete(key)
        return None

    def set(self, key: str, value: bytes, ttl: int = None):
        expire_at = time.time() + ttl if ttl else None
        with self.conn:
            self.conn.execute(
                'INSERT OR REPLACE INTO cache (key, value, expire_at) VALUES (?, ?, ?)',
                (key, value, expire_at)
            )

    def delete(self, key: str) -> bool:
        with self.conn:
            cursor = self.conn.execute('DELETE FROM cache WHERE key = ?', (key,))
            return cursor.rowcount > 0
            
    def clear_pattern(self, pattern: str) -> int:
        db_pattern = pattern.replace('*', '%')
        with self.conn:
            cursor = self.conn.execute('DELETE FROM cache WHERE key LIKE ?', (db_pattern,))
            return cursor.rowcount

    def incr(self, key: str) -> int:
        with self.conn:
            cursor = self.conn.execute('SELECT value, expire_at FROM cache WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row and (row[1] is None or row[1] > time.time()):
                try:
                    val = int(row[0].decode('utf-8')) + 1
                except ValueError:
                    val = 1
            else:
                val = 1
            expire_at = row[1] if row else None
            self.conn.execute(
                'INSERT OR REPLACE INTO cache (key, value, expire_at) VALUES (?, ?, ?)',
                (key, str(val).encode('utf-8'), expire_at)
            )
            return val

    def expire(self, key: str, ttl: int):
        with self.conn:
            cursor = self.conn.execute('SELECT value FROM cache WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                expire_at = time.time() + ttl
                self.conn.execute(
                    'UPDATE cache SET expire_at = ? WHERE key = ?',
                    (expire_at, key)
                )

# Shared SQLite Backend Instance
cache_db = SQLiteCacheBackend()


# ==================== Safe Cache Operations ====================

def safe_cache_get(key: str, default: Any = None) -> Any:
    try:
        data = cache_db.get(key)
        if data is None:
            return default
        return pickle.loads(data)
    except Exception as e:
        logger.error(f"Unexpected error on GET {key}: {e}")
        return default


def safe_cache_set(key: str, value: Any, ttl: int = CacheTTL.HOUR) -> bool:
    try:
        cache_db.set(key, pickle.dumps(value), ttl)
        return True
    except Exception as e:
        logger.error(f"Unexpected error on SET {key}: {e}")
        return False


def safe_cache_delete(key: str) -> bool:
    try:
        return cache_db.delete(key)
    except Exception as e:
        logger.error(f"Unexpected error on DELETE {key}: {e}")
        return False


# ==================== Pydantic Model Caching ====================

def cache_pydantic_model(key: str, model: BaseModel, ttl: int = CacheTTL.HOUR) -> bool:
    try:
        cache_db.set(key, model.model_dump_json().encode('utf-8'), ttl)
        return True
    except Exception as e:
        logger.error(f"Error caching Pydantic model {key}: {e}")
        return False


def get_pydantic_model(key: str, model_class: type[BaseModel]) -> Optional[BaseModel]:
    try:
        data = cache_db.get(key)
        if not data:
            return None
        return model_class.model_validate_json(data.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error retrieving Pydantic model {key}: {e}")
        return None


# ==================== Rate Limiting ====================

def check_rate_limit(key: str, limit: int, window: int = CacheTTL.MINUTE) -> bool:
    try:
        current = cache_db.incr(key)
        if current == 1:
            cache_db.expire(key, window)
        return current <= limit
    except Exception as e:
        logger.error(f"Error checking rate limit {key}: {e}")
        return True  # Fail open


# ==================== Health Check ====================

def redis_health_check() -> dict:
    try:
        # Just check if we can touch the DB
        cache_db.conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "sqlite_cache"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
