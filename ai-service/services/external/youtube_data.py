"""
YouTube Data API v3 Service
Deterministic video and engagement metrics
"""

import httpx
import logging
from typing import Dict, List, Optional
from core.config import get_settings
from services.redis_cache import cached

logger = logging.getLogger(__name__)


class YouTubeDataService:
    """
    YouTube Data API v3 integration
    FREE tier: 10,000 quota units/day
    """
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    def __init__(self, api_key: str = None, cache=None):
        settings = get_settings()
        self.api_key = api_key or settings.YOUTUBE_API_KEY
        self.client = httpx.AsyncClient(timeout=15.0)
        self.cache = cache  # Redis cache service
    
    @cached(prefix="youtube", ttl=10800)  # 3 hours - video counts change moderately
    async def search_videos(self, keyword: str, max_results: int = 10) -> Dict:
        """
        Search for videos by keyword
        
        Returns deterministic video count and view metrics
        Each search costs 100 quota units
        """
        if not self.api_key:
            logger.warning("No YouTube API key configured, using fallback")
            return self._get_fallback_data(keyword)
        
        try:
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "maxResults": max_results,
                "key": self.api_key,
                "order": "relevance"
            }
            
            response = await self.client.get(
                f"{self.BASE_URL}/search",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
            
            # Get video statistics (views, likes, comments)
            stats = await self._get_video_stats(video_ids) if video_ids else []
            
            total_views = sum(s.get("view_count", 0) for s in stats)
            avg_views = total_views / len(stats) if stats else 0
            
            logger.info(f"YouTube: Found {len(video_ids)} videos for '{keyword}'")
            
            return {
                "keyword": keyword,
                "video_count": len(video_ids),
                "total_views": total_views,
                "avg_views_per_video": int(avg_views),
                "engagement_score": self._calculate_engagement(stats),
                "data_source": "YouTube Data API v3"
            }
            
        except Exception as e:
            logger.error(f"YouTube API Error: {str(e)}")
            return self._get_fallback_data(keyword)
    
    async def _get_video_stats(self, video_ids: List[str]) -> List[Dict]:
        """
        Get statistics for multiple videos
        Costs 1 quota unit per request
        """
        try:
            params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": self.api_key
            }
            
            response = await self.client.get(
                f"{self.BASE_URL}/videos",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            stats = []
            for item in data.get("items", []):
                item_stats = item.get("statistics", {})
                stats.append({
                    "view_count": int(item_stats.get("viewCount", 0)),
                    "like_count": int(item_stats.get("likeCount", 0)),
                    "comment_count": int(item_stats.get("commentCount", 0))
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"YouTube video stats error: {str(e)}")
            return []
    
    def _calculate_engagement(self, stats: List[Dict]) -> int:
        """
        Calculate engagement score from video stats
        Scale: 0-100
        """
        if not stats:
            return 50
        
        # High view count + comments = high engagement
        avg_views = sum(s.get("view_count", 0) for s in stats) / len(stats)
        avg_comments = sum(s.get("comment_count", 0) for s in stats) / len(stats)
        
        # Heuristic scoring
        if avg_views > 100000:
            return 90
        elif avg_views > 10000:
            return 75
        elif avg_views > 1000:
            return 60
        else:
            return 40
    
    def _get_fallback_data(self, keyword: str) -> Dict:
        """Fallback when API fails or no key"""
        logger.warning(f"Using fallback data for YouTube: {keyword}")
        return {
            "keyword": keyword,
            "video_count": 0,
            "total_views": 0,
            "avg_views_per_video": 0,
            "engagement_score": 50,
            "data_source": "Mock (API unavailable)"
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
