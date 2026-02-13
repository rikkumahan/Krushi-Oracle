"""
Google Trends Service - Real-time market interest data
Provides trend analysis and search interest validation for startup ideas
"""

from pytrends.request import TrendReq
from typing import Dict, List, Optional
import asyncio
from functools import lru_cache
import pandas as pd

class GoogleTrendsService:
    """
    Fetches real-time market interest data from Google Trends.
    Uses pytrends library with async wrapper for non-blocking I/O.
    """
    
    def __init__(self, hl: str = 'en-US', tz: int = 360):
        """
        Initialize Google Trends client.
        
        Args:
            hl: Language (default: en-US)
            tz: Timezone offset in minutes (default: 360 for US Central)
        """
        self.hl = hl
        self.tz = tz
    
    def _get_client(self) -> TrendReq:
        """Get a fresh pytrends client instance"""
        return TrendReq(hl=self.hl, tz=self.tz, timeout=(10, 25))
    
    async def get_interest_over_time(
        self, 
        keyword: str, 
        timeframe: str = 'today 12-m'
    ) -> Dict:
        """
        Get search interest trend for a keyword over time.
        
        Args:
            keyword: Search term to analyze
            timeframe: Time period (e.g., 'today 12-m', 'today 3-m', 'today 5-y')
        
        Returns:
            {
                "trend": "Rising" | "Stable" | "Declining",
                "average_interest": int (0-100),
                "current_interest": int (0-100),
                "is_trending": bool
            }
        """
        def _fetch():
            try:
                pytrend = self._get_client()
                pytrend.build_payload([keyword], timeframe=timeframe)
                data = pytrend.interest_over_time()
                
                if data.empty or keyword not in data.columns:
                    return self._mock_response(keyword, "No data available")
                
                series = data[keyword]
                avg = int(series.mean())
                current = int(series.iloc[-1])
                first_half_avg = int(series.iloc[:len(series)//2].mean())
                second_half_avg = int(series.iloc[len(series)//2:].mean())
                
                # Determine trend
                if second_half_avg > first_half_avg * 1.2:
                    trend = "Rising"
                elif second_half_avg < first_half_avg * 0.8:
                    trend = "Declining"
                else:
                    trend = "Stable"
                
                return {
                    "trend": trend,
                    "average_interest": avg,
                    "current_interest": current,
                    "is_trending": current > avg * 1.3,
                    "data_source": "Google Trends (Live)"
                }
            except Exception as e:
                print(f"Google Trends API Error: {e}")
                return self._mock_response(keyword, str(e))
        
        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(_fetch)
    
    async def compare_keywords(
        self, 
        keywords: List[str], 
        timeframe: str = 'today 12-m'
    ) -> Dict:
        """
        Compare search interest for multiple keywords.
        
        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Time period
        
        Returns:
            {
                "keywords": [...],
                "winner": str,
                "scores": {"keyword1": 85, "keyword2": 42, ...}
            }
        """
        if len(keywords) > 5:
            keywords = keywords[:5]  # Google Trends limit
        
        def _fetch():
            try:
                pytrend = self._get_client()
                pytrend.build_payload(keywords, timeframe=timeframe)
                data = pytrend.interest_over_time()
                
                if data.empty:
                    return {"keywords": keywords, "winner": keywords[0], "scores": {k: 50 for k in keywords}}
                
                scores = {k: int(data[k].mean()) for k in keywords if k in data.columns}
                winner = max(scores, key=scores.get) if scores else keywords[0]
                
                return {
                    "keywords": keywords,
                    "winner": winner,
                    "scores": scores,
                    "data_source": "Google Trends (Live)"
                }
            except Exception as e:
                print(f"Google Trends Compare Error: {e}")
                return {"keywords": keywords, "winner": keywords[0], "scores": {k: 50 for k in keywords}}
        
        return await asyncio.to_thread(_fetch)
    
    async def get_related_queries(self, keyword: str) -> Dict:
        """
        Get related and rising search queries for a keyword.
        
        Args:
            keyword: Base keyword
        
        Returns:
            {
                "top": ["query1", "query2", ...],
                "rising": ["query3", "query4", ...]
            }
        """
        def _fetch():
            try:
                pytrend = self._get_client()
                pytrend.build_payload([keyword])
                related = pytrend.related_queries()
                
                if not related or keyword not in related:
                    return {"top": [], "rising": []}
                
                top_queries = []
                rising_queries = []
                
                if 'top' in related[keyword] and related[keyword]['top'] is not None:
                    top_queries = related[keyword]['top']['query'].head(5).tolist()
                
                if 'rising' in related[keyword] and related[keyword]['rising'] is not None:
                    rising_queries = related[keyword]['rising']['query'].head(5).tolist()
                
                return {
                    "top": top_queries,
                    "rising": rising_queries,
                    "data_source": "Google Trends (Live)"
                }
            except Exception as e:
                print(f"Google Trends Related Queries Error: {e}")
                return {"top": [], "rising": []}
        
        return await asyncio.to_thread(_fetch)
    
    def _mock_response(self, keyword: str, error: str = "") -> Dict:
        """Fallback response when API fails"""
        return {
            "trend": "Stable",
            "average_interest": 50,
            "current_interest": 50,
            "is_trending": False,
            "data_source": f"Mock (API unavailable: {error[:50]})"
        }
