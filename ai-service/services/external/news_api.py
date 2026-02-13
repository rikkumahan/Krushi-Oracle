"""
News API Service
Deterministic news article and trend analysis
"""

import httpx
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from core.config import get_settings
from services.redis_cache import cached

logger = logging.getLogger(__name__)


class NewsAPIService:
    """
    News API integration (newsapi.org)
    FREE tier: 100 requests/day, 1 month history
    """
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str = None, cache=None):
        settings = get_settings()
        self.api_key = api_key or getattr(settings, 'NEWS_API_KEY', None)
        self.client = httpx.AsyncClient(timeout=15.0)
        self.cache = cache  # Redis cache service
    
    @cached(prefix="news", ttl=3600)  # 1 hour - news changes frequently
    async def search_articles(self, keyword: str, days_back: int = 30) -> Dict:
        """
        Search news articles by keyword
        
        Returns article count and source diversity
        Deterministic for same time range
        """
        if not self.api_key:
            logger.warning("No News API key configured, using fallback")
            return self._get_fallback_data(keyword)
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            params = {
                "q": keyword,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": to_date.strftime("%Y-%m-%d"),
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": 100,
                "apiKey": self.api_key
            }
            
            response = await self.client.get(
                f"{self.BASE_URL}/everything",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            total_results = data.get("totalResults", 0)
            
            # Source diversity (unique news outlets)
            sources = set(article["source"]["name"] for article in articles)
            
            logger.info(f"News API: Found {total_results} articles for '{keyword}'")
            
            return {
                "keyword": keyword,
                "article_count": total_results,
                "sources_count": len(sources),
                "diversity_score": self._calculate_diversity(len(sources)),
                "time_range_days": days_back,
                "data_source": "News API"
            }
            
        except Exception as e:
            logger.error(f"News API Error: {str(e)}")
            return self._get_fallback_data(keyword)
    
    def _calculate_diversity(self, source_count: int) -> int:
        """
        Calculate media coverage diversity
        More sources = broader interest
        
        Scale: 0-100
        """
        if source_count >= 20:
            return 90
        elif source_count >= 10:
            return 75
        elif source_count >= 5:
            return 60
        elif source_count >= 2:
            return 40
        else:
            return 20
    
    def _get_fallback_data(self, keyword: str) -> Dict:
        """Fallback when API fails"""
        logger.warning(f"Using fallback data for News API: {keyword}")
        return {
            "keyword": keyword,
            "article_count": 0,
            "sources_count": 0,
            "diversity_score": 50,
            "time_range_days": 30,
            "data_source": "Mock (API unavailable)"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
