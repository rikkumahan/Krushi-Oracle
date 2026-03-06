"""
Wikipedia Pageviews API Service
Deterministic topic interest analysis
"""

import httpx
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from services.redis_cache import cached

logger = logging.getLogger(__name__)


class WikipediaPageviewsService:
    """
    Wikipedia Pageviews API (Wikimedia)
    100% FREE, no authentication
    """
    
    BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
    
    def __init__(self, cache=None):
        headers = {
            "User-Agent": "NovaIdeaLab/1.0 (https://nova.io; dev@nova.io) httpx/0.27.0"
        }
        self.client = httpx.AsyncClient(timeout=10.0, headers=headers)
        self.cache = cache  # Redis cache service
    
    @cached(prefix="wikipedia", ttl=43200)  # 12 hours - pageviews are historical
    async def get_pageviews(self, topic: str, days_back: int = 30) -> Dict:
        """
        Get Wikipedia pageview counts for a topic
        
        Returns exact view counts (deterministic)
        Topic must be Wikipedia article title
        """
        try:
            # Format topic for Wikipedia (spaces → underscores)
            article_title = topic.replace(" ", "_")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            url = (
                f"{self.BASE_URL}/per-article/en.wikipedia/all-access/"
                f"all-agents/{article_title}/daily/"
                f"{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
            )
            
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Sum up daily views
            items = data.get("items", [])
            total_views = sum(item["views"] for item in items)
            avg_daily_views = total_views / len(items) if items else 0
            
            # Calculate trend (last week vs previous week)
            trend = self._calculate_trend(items)
            
            logger.info(f"Wikipedia: {total_views} views for '{topic}' ({days_back} days)")
            
            return {
                "topic": topic,
                "total_views": total_views,
                "avg_daily_views": int(avg_daily_views),
                "trend": trend,
                "interest_score": self._calculate_interest(avg_daily_views),
                "time_range_days": days_back,
                "data_source": "Wikipedia Pageviews API"
            }
            
        except Exception as e:
            logger.error(f"Wikipedia API Error: {str(e)}")
            return self._get_fallback_data(topic)
    
    def _calculate_trend(self, items: list) -> str:
        """
        Calculate trend direction
        Compare last 7 days vs previous 7 days
        """
        if len(items) < 14:
            return "Stable"
        
        recent_week = sum(item["views"] for item in items[-7:])
        previous_week = sum(item["views"] for item in items[-14:-7])
        
        if recent_week > previous_week * 1.1:
            return "Rising"
        elif recent_week < previous_week * 0.9:
            return "Declining"
        else:
            return "Stable"
    
    def _calculate_interest(self, avg_daily_views: float) -> int:
        """
        Convert pageviews to interest score
        Scale: 0-100
        """
        if avg_daily_views > 10000:
            return 95
        elif avg_daily_views > 5000:
            return 85
        elif avg_daily_views > 1000:
            return 70
        elif avg_daily_views > 500:
            return 60
        elif avg_daily_views > 100:
            return 45
        else:
            return 30
    
    def _get_fallback_data(self, topic: str) -> Dict:
        """Fallback when API fails"""
        logger.warning(f"Using fallback data for Wikipedia: {topic}")
        return {
            "topic": topic,
            "total_views": 0,
            "avg_daily_views": 0,
            "trend": "Unknown",
            "interest_score": 50,
            "time_range_days": 30,
            "data_source": "Mock (API unavailable)"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
