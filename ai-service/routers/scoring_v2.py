"""
FastAPI Router for Scoring Engine V2

Endpoints:
- POST /api/v2/score-idea: Run deterministic scorer
- POST /api/v2/explain-score: Query Strategic Audit Agent

Following fastapi-pro best practices:
- Async-first design
- Pydantic models for validation
- Proper error handling
- OpenAPI documentation
- Dependency injection
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from services.idea_scorer_v2.engine import (
    DeterministicScorerV2,
    IdeaInput,
    ScoringResult
)
from services.idea_scorer_v2.signal_fusion import MarketSignals
from services.idea_scorer_v2.momentum_analyzer import TimeSeriesData
from services.idea_scorer_v2.competition_mapper import CompetitiveData
from services.idea_scorer_v2.tech_analyzer import TechStack, Technology, TechCategory, TechStackAnalyzer
from services.explanatory.strategic_audit_agent import (
    StrategicAuditAgent,
    AuditQuery,
    ExplanationResponse
)

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2", tags=["Scoring V2"])


# ==================== Request/Response Models ====================

class TechStackInput(BaseModel):
    """Tech stack input for API"""
    technologies: List[str] = Field(..., description="List of technology names (e.g., ['React', 'FastAPI'])")
    team_experience: Dict[str, str] = Field(
        default_factory=dict,
        description="Team experience levels: {tech_name: 'EXPERT|FAMILIAR|BEGINNER|NONE'}"
    )


class IdeaScoreRequest(BaseModel):
    """Request body for scoring an idea"""
    
    # Idea meta
    idea_name: str = Field(..., description="Name of the startup idea", min_length=1, max_length=200)
    idea_description: str = Field(..., description="Brief description", min_length=10, max_length=1000)
    target_market: str = Field(..., description="Target market/customer segment", min_length=3, max_length=500)
    
    # Market signals
    monthly_searches: int = Field(..., description="Google Trends monthly searches", ge=0, le=10_000_000)
    growth_rate_30d: float = Field(0.0, description="30-day growth rate (decimal, e.g., 0.15 for +15%)", ge=-1.0, le=10.0)
    
    # Social signals
    youtube_video_count: int = Field(0, description="Number of YouTube videos", ge=0)
    youtube_total_views: int = Field(0, description="Total YouTube views", ge=0)
    reddit_post_count: int = Field(0, description="Number of Reddit posts", ge=0)
    reddit_total_score: int = Field(0, description="Total Reddit score", ge=0)
    
    # News signals
    wikipedia_daily_views: int = Field(0, description="Daily Wikipedia views", ge=0)
    news_articles_30d: int = Field(0, description="News articles in last 30 days", ge=0)
    news_unique_sources: int = Field(0, description="Unique news sources", ge=0)
    
    # Time-series data (simplified - will use single value for all windows)
    trend_values_30d: Optional[List[float]] = Field(None, description="30-day trend values")
    trend_values_90d: Optional[List[float]] = Field(None, description="90-day trend values")  
    trend_values_180d: Optional[List[float]] = Field(None, description="180-day trend values")
    
    # Competitive data
    competitor_count: int = Field(0, description="Number of direct competitors", ge=0, le=10000)
    top_player_market_shares: List[float] = Field(
        default_factory=list,
        description="Market shares of top players (as percentages, each 0-100)"
    )
    new_entrants_12m: int = Field(0, description="New entrants in last 12 months", ge=0, le=10000)
    exits_12m: int = Field(0, description="Exits in last 12 months", ge=0, le=10000)
    substitute_count: int = Field(0, description="Number of substitute products", ge=0, le=1000)
    
    @field_validator("top_player_market_shares")
    @classmethod
    def validate_market_shares(cls, v: List[float]) -> List[float]:
        """Validate market shares sum to ≤100% and each is 0-100"""
        if not v:  # Empty list is valid
            return v
        
        # Check individual values
        for share in v:
            if share < 0 or share > 100:
                raise ValueError(f"Each market share must be 0-100%, got {share}%")
        
        # Check total
        total = sum(v)
        if total > 100:
            raise ValueError(f"Market shares sum to {total}%, must be ≤100%")
        
        return v
    
    # Tech stack
    tech_stack: TechStackInput = Field(..., description="Technology stack")
    
    # Capital
    estimated_capital_needed: Optional[int] = Field(None, description="Estimated capital needed (USD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "idea_name": "AI Meal Planner for Busy Professionals",
                "idea_description": "Personalized meal plans with grocery lists and recipe videos",
                "target_market": "Busy professionals aged 25-45",
                "monthly_searches": 25000,
                "growth_rate_30d": 0.15,
                "youtube_video_count": 350,
                "youtube_total_views": 1800000,
                "reddit_post_count": 120,
                "reddit_total_score": 2400,
                "wikipedia_daily_views": 850,
                "news_articles_30d": 45,
                "news_unique_sources": 12,
                "competitor_count": 25,
                "top_player_market_shares": [30, 20, 15, 10, 5],
                "new_entrants_12m": 8,
                "exits_12m": 3,
                "substitute_count": 12,
                "tech_stack": {
                    "technologies": ["Next.js", "FastAPI", "PostgreSQL", "Prisma", "Vercel"],
                    "team_experience": {
                        "Next.js": "FAMILIAR",
                        "FastAPI": "FAMILIAR",
                        "PostgreSQL": "BEGINNER",
                        "Prisma": "FAMILIAR",
                        "Vercel": "EXPERT"
                    }
                },
                "estimated_capital_needed": 150000
            }
        }


class IdeaScoreResponse(BaseModel):
    """Response from scoring endpoint"""
    success: bool
    mvs_score: int
    mvs_grade: str
    validation_class: str
    recommendations: List[str]
    dimension_scores: Dict[str, int]
    audit_trail_url: Optional[str] = None


class ExplainRequest(BaseModel):
    """Request to explain a score"""
    idea_name: str = Field(..., description="Name of the idea (must match scored idea)")
    question: str = Field(..., description="Question about the score")
    session_id: Optional[str] = Field(None, description="Session ID for conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "idea_name": "AI Meal Planner for Busy Professionals",
                "question": "Why is my market score 71/100? Explain like a VC."
            }
        }


# ==================== Dependency Injection ====================

def get_scorer() -> DeterministicScorerV2:
    """Dependency: Get scoring engine instance"""
    return DeterministicScorerV2()


def get_agent() -> StrategicAuditAgent:
    """Dependency: Get Strategic Audit Agent instance"""
    return StrategicAuditAgent()


# ==================== Cache Layer (Redis with graceful degradation) ====================

from utils.redis_cache import (
    safe_cache_get,
    safe_cache_set,
    CacheKey,
    CacheTTL,
    redis_health_check
)

# Note: No in-memory fallback - Redis utilities fail gracefully
# If Redis is unavailable, safe_cache_get returns None and safe_cache_set returns False
# The application continues to work, just without caching


# ==================== Endpoints ====================

@router.post("/score-idea", response_model=IdeaScoreResponse)
async def score_idea(
    request: IdeaScoreRequest,
    scorer: DeterministicScorerV2 = Depends(get_scorer)
):
    """
    Score a startup idea using the deterministic scoring engine.
    
    Returns MVS score, dimension breakdown, and recommendations.
    100% deterministic - no LLM in computation path.
    """
    try:
        logger.info(f"Scoring idea: {request.idea_name}")
        
        # Build market signals
        signals = MarketSignals(
            monthly_searches=request.monthly_searches,
            growth_rate_30d=request.growth_rate_30d,
            video_count=request.youtube_video_count,
            total_views=request.youtube_total_views,
            post_count=request.reddit_post_count,
            total_score=request.reddit_total_score,
            daily_views=request.wikipedia_daily_views,
            article_count_30d=request.news_articles_30d,
            unique_sources=request.news_unique_sources
        )
        
        # Build time-series data (use defaults if not provided)
        def create_trend_data(values: Optional[List[float]], period: int) -> TimeSeriesData:
            if values:
                return TimeSeriesData(values=values, period_days=period)
            else:
                # Generate simple upward trend based on growth rate
                base = 100
                growth_per_point = request.growth_rate_30d / 7  # Weekly growth
                num_points = period // 7
                trend = [base * (1 + growth_per_point) ** i for i in range(num_points)]
                return TimeSeriesData(values=trend, period_days=period)
        
        trends_30d = create_trend_data(request.trend_values_30d, 30)
        trends_90d = create_trend_data(request.trend_values_90d, 90)
        trends_180d = create_trend_data(request.trend_values_180d, 180)
        
        # Build competitive data
        comp_data = CompetitiveData(
            commercial_entity_count=request.competitor_count,
            top_player_market_shares=request.top_player_market_shares,
            new_entrants_12m=request.new_entrants_12m,
            exits_12m=request.exits_12m,
            substitute_count=request.substitute_count,
            youtube_video_count=request.youtube_video_count,
            blog_post_count=0  # Not provided in simple API
        )
        
        # Build tech stack
        tech_db = TechStackAnalyzer.TECH_DB
        technologies = []
        for tech_name in request.tech_stack.technologies:
            if tech_name in tech_db:
                technologies.append(tech_db[tech_name])
            else:
                # Unknown tech - create default
                technologies.append(
                    Technology(tech_name, TechCategory.BACKEND, 5, "STABLE", 2)
                )
        
        tech_stack = TechStack(
            technologies=technologies,
            team_experience=request.tech_stack.team_experience
        )
        
        # Build idea input
        idea = IdeaInput(
            idea_name=request.idea_name,
            idea_description=request.idea_description,
            target_market=request.target_market,
            market_signals=signals,
            trends_30d=trends_30d,
            trends_90d=trends_90d,
            trends_180d=trends_180d,
            competitive_data=comp_data,
            tech_stack=tech_stack,
            estimated_capital_needed=request.estimated_capital_needed
        )
        
        # Score the idea
        result = scorer.score_idea(idea)
        
        # Cache result for explanation endpoint (Redis with graceful degradation)
        cache_key = CacheKey.scoring_result(request.idea_name)
        cached = safe_cache_set(cache_key, result, ttl=CacheTTL.SCORING_RESULT)
        
        if not cached:
            logger.warning(f"Failed to cache result for {request.idea_name} - Redis may be unavailable")
        
        logger.info(f"Scored {request.idea_name}: MVS={result.mvs_score}/100")
        
        return IdeaScoreResponse(
            success=True,
            mvs_score=result.mvs_score,
            mvs_grade=result.mvs_grade,
            validation_class=result.validation_class,
            recommendations=result.recommendations,
            dimension_scores={
                "market": result.market_dimension,
                "differentiation": result.differentiation_dimension,
                "execution": result.execution_dimension,
                "capital": result.capital_dimension
            }
        )
        
    except Exception as e:
        logger.error(f"Error scoring idea: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.post("/explain-score", response_model=ExplanationResponse)
async def explain_score(
    request: ExplainRequest,
    agent: StrategicAuditAgent = Depends(get_agent)
):
    """
    Get strategic explanation of a score using the Strategic Audit Agent.
    
    Uses LLM with deterministic tools to provide VC-level insights.
    """
    try:
        logger.info(f"Explaining score for: {request.idea_name}")
        
        # Get cached scoring result from Redis
        cache_key = CacheKey.scoring_result(request.idea_name)
        result = safe_cache_get(cache_key)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No scoring result found for '{request.idea_name}'. Please score the idea first using /api/v2/score-idea."
            )
        
        # Query agent
        query = AuditQuery(
            question=request.question,
            session_id=request.session_id
        )
        
        explanation = await agent.explain(result, query)
        
        logger.info(f"Generated explanation using {len(explanation.tools_used)} tools")
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining score: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = redis_health_check()
    
    return {
        "status": "healthy",
        "service": "IdeaLab Scoring V2",
        "version": "2.0-deterministic",
        "timestamp": datetime.utcnow().isoformat(),
        "cache": redis_status
    }
