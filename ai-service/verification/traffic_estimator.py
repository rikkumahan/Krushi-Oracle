from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from services.external.google_trends import GoogleTrendsService
from services.external.keyword_extractor import KeywordExtractorService

class TrafficEstimateRequest(BaseModel):
    # Idea details for keyword extraction
    idea_name: str = Field(..., description="Name of the startup idea")
    idea_description: str = Field(..., description="Description of what the idea does")
    industry: str
    target_audience: str
    budget: float = Field(..., ge=100, description="Monthly Ad Budget")
    
    # Optional: User can provide keywords or let LLM generate them
    keywords: Optional[List[str]] = Field(None, description="Optional: Provide specific keywords to analyze")
    cpc_override: Optional[float] = None

class TrafficEstimateResponse(BaseModel):
    estimated_cpc: float
    estimated_clicks: int
    confidence_score: int # 0-100 based on data quality
    search_volume_trend: str # "Stable", "Rising", "Declining"
    recommended_channels: list[str]
    keywords_analyzed: List[str] = []  # Keywords used for trend analysis
    trend_insights: Dict = {}  # Aggregated Google Trends data

class TrafficEstimatorService:
    """
    Estimates traffic potential using:
    1. LLM-powered keyword extraction from idea descriptions
    2. Google Trends analysis for multiple keywords
    3. Industry benchmark data
    """
    
    # Industry CPC Benchmarks (Source: WordStream/HubSpot 2024)
    BENCHMARKS = {
        "saas": {"cpc": 5.00, "channels": ["LinkedIn", "Google Search"]},
        "fintech": {"cpc": 8.50, "channels": ["Google Search", "Affiliate"]},
        "edtech": {"cpc": 3.20, "channels": ["Facebook", "YouTube"]},
        "ecommerce": {"cpc": 1.10, "channels": ["Instagram", "Google Shopping"]},
        "health": {"cpc": 4.50, "channels": ["Google Search", "Facebook"]},
        "ai tools": {"cpc": 2.50, "channels": ["Twitter", "ProductHunt"]},
        "b2b services": {"cpc": 6.00, "channels": ["LinkedIn", "Email"]},
    }
    
    DEFAULT_CPC = 3.50

    def __init__(
        self, 
        trends_service: Optional[GoogleTrendsService] = None,
        keyword_extractor: Optional[KeywordExtractorService] = None
    ):
        self.trends = trends_service or GoogleTrendsService()
        self.keyword_extractor = keyword_extractor

    async def estimate_traffic(self, request: TrafficEstimateRequest) -> TrafficEstimateResponse:
        """
        Estimate traffic with intelligent keyword extraction and multi-keyword trend analysis.
        """
        # Step 1: Get keywords (user-provided or LLM-generated)
        keywords = await self._get_keywords(request)
        
        # Step 2: Get industry benchmark CPC
        key = request.industry.lower()
        data = next((v for k, v in self.BENCHMARKS.items() if k in key), None)
        
        if not data:
            cpc = self.DEFAULT_CPC
            channels = ["Google Search", "Facebook"]
            confidence = 40
        else:
            cpc = data["cpc"]
            channels = data["channels"]
            confidence = 85
            
        if request.cpc_override:
            cpc = request.cpc_override
            confidence = 95
        
        # Step 3: Fetch Google Trends for all keywords and aggregate
        trend_insights = await self._analyze_keywords_trends(keywords)
        
        # Step 4: Determine overall trend direction and volume
        trend_direction = self._aggregate_trend_direction(trend_insights)
        total_search_volume = trend_insights.get("average_market_interest", 50) * 1000 # Rough proxy for now
        
        # Step 5: Impression Share Logic (Constraint-based)
        ctr_benchmark = 0.04  # 4% CTR average
        market_click_inventory = total_search_volume * ctr_benchmark
        
        naive_clicks = int(request.budget / cpc)
        
        # Apply market constraints
        if naive_clicks > market_click_inventory:
            estimated_clicks = int(market_click_inventory)
            impression_share = 100
            saturation_warning = "Budget exceeds market inventory. You will saturate this niche."
        else:
            estimated_clicks = naive_clicks
            impression_share = int((estimated_clicks / market_click_inventory) * 100) if market_click_inventory > 0 else 0
            saturation_warning = None

        # Step 6: Adjust confidence based on data quality
        if trend_insights.get("data_quality") == "live":
            confidence = min(confidence + 15, 100)
        
        return TrafficEstimateResponse(
            estimated_cpc=cpc,
            estimated_clicks=estimated_clicks,
            confidence_score=confidence,
            search_volume_trend=trend_direction,
            recommended_channels=channels,
            keywords_analyzed=keywords,
            trend_insights={
                **trend_insights,
                "impression_share": f"{impression_share}%",
                "market_saturation_warning": saturation_warning
            }
        )
    
    async def _get_keywords(self, request: TrafficEstimateRequest) -> List[str]:
        """Get keywords from user input or LLM extraction"""
        if request.keywords and len(request.keywords) > 0:
            return request.keywords[:5]  # Use provided keywords
        
        if not self.keyword_extractor:
            # Fallback: generate simple keywords
            return [
                f"{request.industry.lower()} software",
                request.idea_name.lower(),
                f"{request.target_audience.lower()} {request.industry.lower()}"
            ][:3]
        
        # Use LLM to extract keywords
        from services.external.keyword_extractor import KeywordExtractionRequest
        extraction_request = KeywordExtractionRequest(
            idea_name=request.idea_name,
            idea_description=request.idea_description,
            industry=request.industry,
            target_audience=request.target_audience,
            num_keywords=3
        )
        
        result = await self.keyword_extractor.extract_keywords(extraction_request)
        return result.primary_keywords
    
    async def _analyze_keywords_trends(self, keywords: List[str]) -> Dict:
        """Fetch and aggregate Google Trends data for multiple keywords"""
        trends_data = []
        
        for keyword in keywords:
            try:
                trend_info = await self.trends.get_interest_over_time(keyword)
                trends_data.append({
                    "keyword": keyword,
                    "trend": trend_info.get("trend", "Stable"),
                    "average_interest": trend_info.get("average_interest", 0),
                    "current_interest": trend_info.get("current_interest", 0),
                    "is_trending": trend_info.get("is_trending", False),
                    "data_source": trend_info.get("data_source", "Mock")
                })
            except Exception as e:
                print(f"Failed to fetch trends for '{keyword}': {e}")
                trends_data.append({
                    "keyword": keyword,
                    "trend": "Stable",
                    "average_interest": 50,
                    "current_interest": 50,
                    "is_trending": False,
                    "data_source": "Mock (Error)"
                })
        
        # Aggregate insights
        avg_interest = sum(t["average_interest"] for t in trends_data) / len(trends_data) if trends_data else 0
        any_trending = any(t["is_trending"] for t in trends_data)
        live_data_count = sum(1 for t in trends_data if "Live" in t["data_source"])
        
        return {
            "keywords_data": trends_data,
            "average_market_interest": int(avg_interest),
            "has_trending_keyword": any_trending,
            "data_quality": "live" if live_data_count > 0 else "mock",
            "live_data_percentage": int((live_data_count / len(trends_data)) * 100) if trends_data else 0
        }
    
    def _aggregate_trend_direction(self, trend_insights: Dict) -> str:
        """Determine overall trend from multiple keywords"""
        keywords_data = trend_insights.get("keywords_data", [])
        
        if not keywords_data:
            return "Stable"
        
        rising_count = sum(1 for k in keywords_data if k["trend"] == "Rising")
        declining_count = sum(1 for k in keywords_data if k["trend"] == "Declining")
        
        if rising_count > len(keywords_data) / 2:
            return "Rising"
        elif declining_count > len(keywords_data) / 2:
            return "Declining"
        else:
            return "Stable"
