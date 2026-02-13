"""
Google Autocomplete API Service
Deterministic keyword suggestion analysis
"""

import httpx
import logging
from typing import List, Dict, Optional
from functools import lru_cache
from services.redis_cache import cached

logger = logging.getLogger(__name__)


class GoogleAutocompleteService:
    """
    Google Autocomplete API integration
    FREE, no authentication needed
    """
    
    BASE_URL = "http://suggestqueries.google.com/complete/search"
    
    def __init__(self, cache=None):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.cache = cache  # Redis cache service
    
    @cached(prefix="autocomplete", ttl=21600)  # 6 hours - suggestions are stable
    async def get_suggestions(self, keyword: str, lang: str = "en") -> Dict:
        """
        Get autocomplete suggestions for a keyword
        
        Returns deterministic suggestion list
        More suggestions = higher search interest
        """
        try:
            params = {
                "client": "firefox",
                "q": keyword,
                "hl": lang
            }
            
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            # Response format: [query, [suggestions]]
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
            
            logger.info(f"Google Autocomplete: {len(suggestions)} suggestions for '{keyword}'")
            
            return {
                "keyword": keyword,
                "suggestions": suggestions,
                "suggestion_count": len(suggestions),
                "popularity_score": self._calculate_popularity(suggestions),
                "data_source": "Google Autocomplete"
            }
            
        except Exception as e:
            logger.error(f"Google Autocomplete API Error: {str(e)}")
            return self._get_fallback_data(keyword)
    
    def _calculate_popularity(self, suggestions: List[str]) -> int:
        """
        Estimate popularity from suggestion count
        More suggestions = more search activity
        
        Scale: 0-100
        """
        count = len(suggestions)
        
        # Heuristic: 0-2 suggestions = low, 3-6 = medium, 7+ = high
        if count == 0:
            return 10
        elif count <= 2:
            return 30
        elif count <= 6:
            return 60
        else:
            return 85
    
    def _get_fallback_data(self, keyword: str) -> Dict:
        """Fallback when API fails"""
        logger.warning(f"Using fallback data for autocomplete: {keyword}")
        return {
            "keyword": keyword,
            "suggestions": [],
            "suggestion_count": 0,
            "popularity_score": 50,
            "data_source": "Mock (API unavailable)"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
