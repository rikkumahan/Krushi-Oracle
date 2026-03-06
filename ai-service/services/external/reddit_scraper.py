"""
Reddit Scraper Service (YARS-based)
NO API credentials needed - web scraping approach
"""

import logging
import asyncio
from typing import Dict, List, Optional
from services.redis_cache import cached

logger = logging.getLogger(__name__)


class RedditScraperService:
    """
    Reddit scraping via YARS (Yet Another Reddit Scraper)
    NO authentication required - 100% FREE
    """
    
    def __init__(self, cache=None):
        self.cache = cache  # Redis cache service
        try:
            from services.external.yars import YARS
            self.scraper = YARS()
            self.available = True
            logger.info("YARS Reddit scraper initialized successfully")
        except ImportError as e:
            logger.warning(f"YARS not available: {str(e)}, using fallback")
            self.scraper = None
            self.available = False
    
    @cached(prefix="reddit", ttl=7200)  # 2 hours - Reddit discussion changes moderately
    async def search_discussions(
        self, 
        keyword: str, 
        subreddits: List[str] = None,
        limit: int = 100
    ) -> Dict:
        """
        Search Reddit for keyword mentions
        
        Uses YARS scraper - NO credentials needed
        Returns deterministic post/comment counts and engagement
        """
        if not self.available:
            logger.warning("YARS not available, using fallback")
            return self._get_fallback_data(keyword)
        
        try:
            # Method 1: Global Reddit search
            if not subreddits or len(subreddits) == 0:
                return await self._search_global(keyword, limit)
            
            # Method 2: Subreddit-specific search
            return await self._search_subreddits(keyword, subreddits, limit)
            
        except Exception as e:
            logger.error(f"Reddit scraper error: {str(e)}")
            return self._get_fallback_data(keyword)
    
    async def _search_global(self, keyword: str, limit: int) -> Dict:
        """Search all of Reddit for keyword"""
        try:
            # Use YARS search_reddit method (run in thread pool to avoid blocking)
            results = await asyncio.to_thread(self.scraper.search_reddit, keyword, limit=min(limit, 100))
            
            if not results:
                return self._get_fallback_data(keyword)
            
            # Parse results
            total_posts = len(results)
            total_score = sum(post.get("score", 0) for post in results)
            total_comments = sum(post.get("num_comments", 0) for post in results)
            
            avg_score = total_score / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0
            
            logger.info(f"YARS: Found {total_posts} posts for '{keyword}'")
            
            return {
                "keyword": keyword,
                "post_count": total_posts,
                "total_score": total_score,
                "avg_score": int(avg_score),
                "total_comments": total_comments,
                "avg_comments": int(avg_comments),
                "engagement_score": self._calculate_engagement(avg_score, avg_comments),
                "subreddits_searched": ["global"],
                "data_source": "Reddit (YARS Scraper)"
            }
            
        except Exception as e:
            logger.error(f"Global search error: {str(e)}")
            return self._get_fallback_data(keyword)
    
    async def _search_subreddits(self, keyword: str, subreddits: List[str], limit: int) -> Dict:
        """Search specific subreddits for keyword"""
        try:
            all_posts = []
            per_subreddit_limit = max(limit // len(subreddits), 10)
            
            # Fetch posts from each subreddit
            for subreddit in subreddits:
                try:
                    # Use fetch_subreddit_posts with search
                    posts = self.scraper.fetch_subreddit_posts(
                        subreddit=subreddit,
                        limit=per_subreddit_limit,
                        category="hot"  # or "new", "top"
                    )
                    
                    # Filter posts by keyword (basic text matching)
                    filtered = [
                        p for p in posts 
                        if keyword.lower() in p.get("title", "").lower() 
                        or keyword.lower() in p.get("body", "").lower()
                    ]
                    
                    all_posts.extend(filtered)
                    
                except Exception as e:
                    logger.warning(f"Error fetching from r/{subreddit}: {str(e)}")
                    continue
            
            if not all_posts:
                # Fallback to global search
                return await self._search_global(keyword, limit)
            
            # Aggregate metrics
            total_posts = len(all_posts)
            total_score = sum(post.get("score", 0) for post in all_posts)
            total_comments = sum(post.get("num_comments", 0) for post in all_posts)
            
            avg_score = total_score / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0
            
            logger.info(f"YARS: Found {total_posts} posts across {len(subreddits)} subreddits")
            
            return {
                "keyword": keyword,
                "post_count": total_posts,
                "total_score": total_score,
                "avg_score": int(avg_score),
                "total_comments": total_comments,
                "avg_comments": int(avg_comments),
                "engagement_score": self._calculate_engagement(avg_score, avg_comments),
                "subreddits_searched": subreddits,
                "data_source": "Reddit (YARS Scraper)"
            }
            
        except Exception as e:
            logger.error(f"Subreddit search error: {str(e)}")
            return self._get_fallback_data(keyword)
    
    def _calculate_engagement(self, avg_score: float, avg_comments: float) -> int:
        """
        Calculate community engagement score
        High scores + many comments = active discussion
        
        Scale: 0-100
        """
        # Weighted scoring
        score_points = min(avg_score / 10, 50)  # Max 50 points from upvotes
        comment_points = min(avg_comments / 5, 50)  # Max 50 points from comments
        
        total = int(score_points + comment_points)
        return min(total, 100)
    
    def _get_fallback_data(self, keyword: str) -> Dict:
        """Fallback when scraper fails"""
        logger.warning(f"Using fallback data for Reddit: {keyword}")
        return {
            "keyword": keyword,
            "post_count": 0,
            "total_score": 0,
            "avg_score": 0,
            "total_comments": 0,
            "avg_comments": 0,
            "engagement_score": 50,
            "subreddits_searched": [],
            "data_source": "Mock (Scraper unavailable)"
        }
    
    async def close(self):
        """Close scraper (no-op for YARS)"""
        pass
