"""
Google Trends Service (SerpApi) - Real-time market interest data
Provides trend analysis and search interest validation for startup ideas using SerpApi
"""

import httpx
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from core.config import get_settings

logger = logging.getLogger(__name__)

class GoogleTrendsService:
    """
    Fetches real-time market interest data using SerpApi Google Trends engine.
    """
    
    BASE_URL = "https://serpapi.com/search.json"
    
    def __init__(self, hl: str = 'en', tz: int = 360, api_key: Optional[str] = None):
        """
        Initialize Google Trends client.
        
        Args:
            hl: Language (default: en)
            tz: Timezone offset in minutes (default: 360 for US Central)
            api_key: SerpApi Key (defaults to SERPAPI_KEY env var)
        """
        self.hl = hl
        self.tz = tz
        settings = get_settings()
        self.api_key = api_key or settings.SERPAPI_KEY or os.getenv("SERPAPI_KEY")
        self.client = httpx.AsyncClient(timeout=15.0)
    
    def _check_api_key(self):
        if not self.api_key:
            raise ValueError("SERPAPI_KEY is not set. Please add it to your .env file.")

    async def _generate_trends_keyword(self, text: str) -> str:
        """
        Uses LLM to intelligently extract the best 1-3 word search query for Google Trends.
        Falls back to basic sanitization if the LLM fails.
        """
        import asyncio
        # If it's already a short phrase, no need for LLM
        if len(text.split()) <= 3:
            return self._sanitize_keyword(text)
            
        try:
            from utils.openai_helper import get_openai_client, get_model_name
            client = get_openai_client()
            if not client:
                return self._sanitize_keyword(text)
                
            def _fetch_keyword():
                return client.chat.completions.create(
                    model=get_model_name(),
                    messages=[
                        {"role": "system", "content": "You are a Google Trends expert. Extract the absolute best 1-3 word core search term from the user's input. Respond WITH THE SEARCH TERM ONLY, nothing else. No punctuation, no quotes."},
                        {"role": "user", "content": f"Extract Google Trends keyword for this market/audience: {text}"}
                    ],
                    temperature=0.3,
                    max_tokens=20
                )
                
            response = await asyncio.to_thread(_fetch_keyword)
            
            result = response.choices[0].message.content.strip()
            # Clean up the LLM output just in case
            return self._sanitize_keyword(result)
        except Exception as e:
            logger.warning(f"LLM keyword extraction failed: {e}. Falling back to basic regex.")
            return self._sanitize_keyword(text)

    def _sanitize_keyword(self, keyword: str) -> str:
        """
        Sanitizes and shortens long, complex keywords to prevent SerpApi/Google Trends 
        400 Bad Request errors. Google Trends favors short, broad search terms (1-4 words).
        """
        import re
        
        if not keyword:
            return "startup"
            
        # 1. Lowercase and remove basic punctuation
        clean = keyword.lower()
        clean = re.sub(r'[^a-z0-9\s-]', ' ', clean)
        
        # 2. Remove common stop words and generic filler words that dilute trends
        stop_words = {'and', 'or', 'for', 'with', 'the', 'a', 'an', 'in', 'on', 'at', 
                     'to', 'of', 'software', 'app', 'platform', 'service', 'professionals', 
                     'users', 'system', 'solution', 'tech', 'technology', 'startup'}
        
        words = [w for w in clean.split() if w and w not in stop_words]
        
        # If we stripped everything, revert to the original (just cleaned)
        if not words:
            words = [w for w in clean.split() if w]
            
        # 3. Truncate to max 4 words (Google Trends limit for good data)
        shortened = " ".join(words[:4])
        
        # 4. Hard character limit (just in case)
        if len(shortened) > 40:
            shortened = shortened[:40].rsplit(' ', 1)[0]
            
        return shortened or "startup"

    async def get_interest_over_time(
        self, 
        keyword: str, 
        timeframe: str = 'today 12-m'
    ) -> Dict:
        """Get search interest trend for a single keyword over time."""
        
        original_keyword = keyword
        keyword = self._sanitize_keyword(keyword)  # Fast regex — no LLM needed here, keywords are already pre-generated upstream
        
        try:
            self._check_api_key()
            
            params = {
                "engine": "google_trends",
                "q": keyword,
                "data_type": "TIMESERIES",
                "hl": self.hl,
                "tz": str(self.tz),
                "date": timeframe,
                "api_key": self.api_key
            }
            
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            # SerpApi format
            timeline = data.get("interest_over_time", {}).get("timeline_data", [])
            
            if not timeline:
                return self._mock_response(keyword, "No timeline data available")
                
            # Extract values
            values = []
            for item in timeline:
                extracted = item.get("values", [])
                if extracted:
                    # 'extracted_value' could be a string or int. 
                    val_str = extracted[0].get("extracted_value", 0)
                    try:
                        val = int(val_str)
                        values.append(val)
                    except (ValueError, TypeError):
                        pass

            if not values:
                return self._mock_response(keyword, "No valid values extracted")
                
            avg = sum(values) // len(values)
            current = values[-1]
            mid = len(values) // 2
            first_half_avg = sum(values[:mid]) // len(values[:mid]) if mid > 0 else avg
            second_half_avg = sum(values[mid:]) // len(values[mid:]) if mid < len(values) else avg
            
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
                "data_source": "SerpApi Google Trends"
            }
            
        except httpx.HTTPStatusError as e:
            logger.warning(f"SerpApi Google Trends Error for {keyword}: {e}. Response: {e.response.text}. Using fallback data.")
            return self._mock_response(keyword, str(e))
        except Exception as e:
            logger.warning(f"SerpApi Google Trends Error for {keyword}: {e}. Using fallback data.")
            return self._mock_response(keyword, str(e))
            
    async def compare_keywords(
        self, 
        keywords: List[str], 
        timeframe: str = 'today 12-m'
    ) -> Dict:
        """Compare search interest for multiple keywords."""
        if len(keywords) > 5:
            keywords = keywords[:5]
            
        original_keywords = keywords
        
        sanitized_keywords = []
        for k in keywords:
            sanitized = await self._generate_trends_keyword(k)
            sanitized_keywords.append(sanitized)
            
        unique_sanitized = list(set(sanitized_keywords))
            
        try:
            self._check_api_key()
            
            params = {
                "engine": "google_trends",
                "q": ",".join(unique_sanitized),
                "data_type": "TIMESERIES",
                "hl": self.hl,
                "tz": str(self.tz),
                "date": timeframe,
                "api_key": self.api_key
            }
            
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            timeline = data.get("interest_over_time", {}).get("timeline_data", [])
            
            if not timeline:
                return {"keywords": keywords, "winner": keywords[0], "scores": {k: 50 for k in keywords}}
                
            # Initialize sum and count per keyword
            totals = {k: {"sum": 0, "count": 0} for k in unique_sanitized}
            
            for item in timeline:
                vals = item.get("values", [])
                for val_obj in vals:
                    q = val_obj.get("query")
                    val_str = val_obj.get("extracted_value", 0)
                    if q in totals:
                        try:
                            totals[q]["sum"] += int(val_str)
                            totals[q]["count"] += 1
                        except (ValueError, TypeError):
                            pass
                            
            scores = {}
            for orig, sanitized in zip(original_keywords, sanitized_keywords):
                if totals[sanitized]["count"] > 0:
                    scores[orig] = totals[sanitized]["sum"] // totals[sanitized]["count"]
                else:
                    scores[orig] = 0
            
            winner = max(scores, key=scores.get) if scores else original_keywords[0]
            
            return {
                "keywords": keywords,
                "winner": winner,
                "scores": scores,
                "data_source": "SerpApi Google Trends"
            }
            
        except httpx.HTTPStatusError as e:
            logger.warning(f"SerpApi Compare Error for {keywords}: {e}. Response: {e.response.text}. Using fallback data.")
            return {"keywords": original_keywords, "winner": original_keywords[0], "scores": {k: 50 for k in original_keywords}}
        except Exception as e:
            logger.warning(f"SerpApi Compare Error for {keywords}: {e}. Using fallback data.")
            return {"keywords": original_keywords, "winner": original_keywords[0], "scores": {k: 50 for k in original_keywords}}

    async def get_related_queries(self, keyword: str) -> Dict:
        """Get related and rising search queries for a keyword."""
        
        original_keyword = keyword
        keyword = self._sanitize_keyword(keyword)  # Fast regex — no LLM needed
        
        try:
            self._check_api_key()
            
            params = {
                "engine": "google_trends",
                "q": keyword,
                "data_type": "RELATED_QUERIES",
                "hl": self.hl,
                "tz": str(self.tz),
                "api_key": self.api_key
            }
            
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            related = data.get("related_queries", {})
            top_queries = []
            rising_queries = []
            
            for item in related.get("top", [])[:5]:
                q = item.get("query")
                if q:
                    top_queries.append(q)
                    
            for item in related.get("rising", [])[:5]:
                q = item.get("query")
                if q:
                    rising_queries.append(q)
            
            return {
                "top": top_queries,
                "rising": rising_queries,
                "data_source": "SerpApi Google Trends"
            }
            
        except httpx.HTTPStatusError as e:
            logger.warning(f"SerpApi Related Queries Error for {original_keyword}: {e}. Response: {e.response.text}. Using fallback data.")
            return {"top": [], "rising": []}
        except Exception as e:
            logger.warning(f"SerpApi Related Queries Error for {original_keyword}: {e}. Using fallback data.")
            return {"top": [], "rising": []}

    def _mock_response(self, keyword: str, error: str = "") -> Dict:
        """Fallback response when API fails"""
        return {
            "trend": "Stable",
            "average_interest": 50,
            "current_interest": 50,
            "is_trending": False,
            "data_source": f"Mock (SerpApi unavailable: {error[:50]})"
        }
        
    async def close(self):
        await self.client.aclose()
