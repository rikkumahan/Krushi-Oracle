from typing import Dict, Optional
import os
import json
try:
    import redis
except ImportError:
    redis = None

class SectorCache:
    """
    Simulated Redis Cache for Sector Intelligence.
    In Turbo Sprint, we might just use an in-memory dictionary if Redis isn't up.
    """
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None
        if redis:
            try:
                self.client = redis.from_url(self.redis_url, decode_responses=True)
                self.client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory cache.")
                self.client = None
        
        # In-memory fallback
        self._local_cache = {}

    def get_sector_data(self, sector: str) -> Optional[Dict]:
        """Retrieve cached sector data"""
        key = f"sector:{sector.lower()}"
        
        # 1. Try Redis
        if self.client:
            try:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                pass
        
        # 2. Try Local Memory
        return self._local_cache.get(key)

    def set_sector_data(self, sector: str, data: Dict, ttl: int = 3600):
        """Cache sector data"""
        key = f"sector:{sector.lower()}"
        
        # 1. Write to Redis
        if self.client:
            try:
                self.client.setex(key, ttl, json.dumps(data))
            except Exception:
                pass
        
        # 2. Write to Local Memory
        self._local_cache[key] = data

    def get_mock_intelligence(self, sector: str) -> Dict:
        """
        Returns hardcoded intelligence for known sectors (MVP).
        """
        defaults = {
            "market_growth": 0.05,
            "competitor_density": "Medium",
            "avg_valuation_seed": 2000000,
            "typical_cac": 100.0
        }
        
        mocks = {
            "edtech": {
                "market_growth": 0.12, 
                "competitor_density": "High", 
                "avg_valuation_seed": 3500000, 
                "typical_cac": 85.0
            },
            "fintech": {
                "market_growth": 0.18, 
                "competitor_density": "Very High", 
                "avg_valuation_seed": 5000000, 
                "typical_cac": 250.0
            },
             "ai tool": {
                "market_growth": 0.40, 
                "competitor_density": "Exploding", 
                "avg_valuation_seed": 8000000, 
                "typical_cac": 45.0
            }
        }
        
        return mocks.get(sector.lower(), defaults)
