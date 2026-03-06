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
        from config.domain_defaults import get_domain_config
        
        # Step 1: Get keywords (user-provided or LLM-generated)
        keywords = await self._get_keywords(request)
        
        # Step 2: Get industry benchmark CPC
        domain_config = get_domain_config(request.industry)
        
        cpc = domain_config.get("cpc", 2.50)
        channels = domain_config.get("traffic_channels", ["Google Search", "Facebook"])
        confidence = 85 # Higher confidence now that we have extensive mapping
            
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
        """Get keywords from user input or LLM extraction. Targets 5 keywords to maximize Google Trends comparison."""
        if request.keywords and len(request.keywords) > 0:
            return request.keywords[:5]
        
        if not self.keyword_extractor:
            # Fallback: generate simple keywords (covers multiple angles)
            industry = request.industry.lower()
            audience = request.target_audience.lower()
            idea = request.idea_name.lower()
            return [
                f"{industry} software",
                idea,
                f"{industry} automation",
                f"ai {industry}",
                f"{audience} {industry}"
            ][:5]
        
        # Use LLM to extract 5 multi-angle keywords
        from services.external.keyword_extractor import KeywordExtractionRequest
        extraction_request = KeywordExtractionRequest(
            idea_name=request.idea_name,
            idea_description=request.idea_description,
            industry=request.industry,
            target_audience=request.target_audience,
            num_keywords=5  # Max for Google Trends comparison
        )
        
        result = await self.keyword_extractor.extract_keywords(extraction_request)
        return result.primary_keywords[:5]
    
    async def _analyze_keywords_trends(self, keywords: List[str]) -> Dict:
        """
        Fetch Google Trends data for all keywords in a SINGLE batched comparison call.
        This is the Gemini-style approach: one request, 5 keywords, rich comparative data.
        """
        if not keywords:
            return {
                "keywords_data": [],
                "average_market_interest": 50,
                "has_trending_keyword": False,
                "data_quality": "mock",
                "live_data_percentage": 0
            }
        
        try:
            # ONE batched API call to SerpApi for all 5 keywords simultaneously
            comparison = await self.trends.compare_keywords(keywords)
            scores = comparison.get("scores", {})
            winner = comparison.get("winner", keywords[0])
            data_source = comparison.get("data_source", "Mock")
            
            # Map the comparison scores back to the expected per-keyword schema
            trends_data = []
            for kw in keywords:
                score = scores.get(kw, 50)
                trends_data.append({
                    "keyword": kw,
                    "trend": "Rising" if kw == winner else "Stable",
                    "average_interest": score,
                    "current_interest": score,
                    "is_trending": kw == winner,
                    "data_source": data_source
                })
            
            avg_interest = sum(scores.values()) / len(scores) if scores else 50
            is_live = "SerpApi" in data_source
            
            return {
                "keywords_data": trends_data,
                "average_market_interest": int(avg_interest),
                "has_trending_keyword": True,  # There is always a winner in a comparison
                "winner_keyword": winner,
                "data_quality": "live" if is_live else "mock",
                "live_data_percentage": 100 if is_live else 0
            }
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Google Trends batch comparison failed: {e}. Using fallback.")
            # Graceful fallback: return neutral scores for all keywords
            trends_data = [{
                "keyword": kw, "trend": "Stable", "average_interest": 50,
                "current_interest": 50, "is_trending": False, "data_source": "Mock (Error)"
            } for kw in keywords]
            return {
                "keywords_data": trends_data,
                "average_market_interest": 50,
                "has_trending_keyword": False,
                "data_quality": "mock",
                "live_data_percentage": 0
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
