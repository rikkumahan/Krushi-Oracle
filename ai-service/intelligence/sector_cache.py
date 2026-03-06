from typing import Dict, Optional
import os
import json
from utils.redis_cache import cache_db

class SectorCache:
    """
    SQLite-backed Cache for Sector Intelligence.
    """
    
    def __init__(self):
        self.db = cache_db

    def get_sector_data(self, sector: str) -> Optional[Dict]:
        """Retrieve cached sector data"""
        key = f"sector:{sector.lower()}"
        
        data = self.db.get(key)
        if data:
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                pass
                
        return None

    def set_sector_data(self, sector: str, data: Dict, ttl: int = 3600):
        """Cache sector data"""
        key = f"sector:{sector.lower()}"
        try:
            self.db.set(key, json.dumps(data).encode('utf-8'), ttl)
        except Exception:
            pass

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
