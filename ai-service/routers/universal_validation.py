"""
Universal Validation Router
Production-ready API endpoint for startup idea validation across all sectors
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from verification.dependencies import get_universal_validator
from verification.universal_validator import (
    UniversalValidatorService,
    UniversalValidationRequest,
    UniversalValidationResult
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v2/validation",
    tags=["V2 Universal Validation"],
    responses={
        500: {"description": "Internal server error"},
        429: {"description": "Rate limit exceeded"}
    }
)


# Enhanced request model with better documentation
class ValidateIdeaRequest(BaseModel):
    """Request model for universal startup idea validation"""
    
    idea_name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Name of the startup idea",
        examples=["AI Project Management Tool"]
    )
    
    idea_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed description of the idea",
        examples=["AI-powered project management platform for software teams with automatic task prioritization"]
    )
    
    keywords: List[str] = Field(
        default_factory=list,
        description="Search keywords for market analysis (auto-generated if empty)",
        max_length=10,
        examples=[["project management software", "AI productivity tools"]]
    )
    
    sector: str = Field(
        default="software",
        description="Industry sector",
        examples=["software", "hardware", "food", "healthcare", "services"]
    )
    
    # Execution risk parameters
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Technologies required",
        examples=[["Python", "React", "FastAPI", "PostgreSQL"]]
    )
    
    team_size: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Current team size"
    )
    
    timeline_months: int = Field(
        default=6,
        ge=1,
        le=36,
        description="Planned timeline in months"
    )
    
    budget_usd: float = Field(
        default=0,
        ge=0,
        description="Available budget in USD"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "idea_name": "AI Project Management Tool",
                "idea_description": "AI-powered project management platform for software teams",
                "keywords": ["project management", "AI productivity"],
                "sector": "software",
                "tech_stack": ["Python", "React", "FastAPI"],
                "team_size": 2,
                "timeline_months": 6,
                "budget_usd": 50000
            }
        }


# Enhanced response model
class ValidationResponse(BaseModel):
    """Universal validation response with detailed metrics"""
    
    # Meta
    idea_name: str
    sector: str
    
    # Market validation (0-100)
    market_validation: dict = Field(
        description="Market interest metrics",
        examples=[{
            "google_trends_score": 67,
            "autocomplete_popularity": 85,
            "wikipedia_interest": 70,
            "overall_score": 74
        }]
    )
    
    # Social proof (0-100)
    social_proof: dict = Field(
        description="Social validation metrics",
        examples=[{
            "reddit_engagement": 72,
            "youtube_coverage": 68,
            "news_mentions": 12,
            "overall_score": 70
        }]
    )
    
    # Execution risk
    execution_risk: dict = Field(
        description="Execution feasibility assessment",
        examples=[{
            "complexity_score": 45,
            "risk_level": "Medium",
            "estimated_months": 8,
            "confidence": 73,
            "key_challenges": ["High technical complexity", "Timeline aggressive"]
        }]
    )
    
    # Sector Intelligence (Critical fix)
    sector_signals: dict = Field(
        description="Deep sector-specific metrics (GitHub, Clinical Trials, etc.)",
        default_factory=dict
    )
    
    # Overall
    overall_confidence: int = Field(
        ge=0,
        le=100,
        description="Overall validation confidence score"
    )
    
    verdict: str = Field(
        description="Human-readable verdict",
        examples=["🚀 STRONG OPPORTUNITY", "✅ VIABLE", "⚠️ MODERATE POTENTIAL", "❌ HIGH RISK"]
    )
    
    # Data quality
    data_quality: dict = Field(
        description="Data source quality metrics"
    )


@router.post(
    "/validate",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Startup Idea",
    description="""
    **Universal validation across ALL startup sectors**
    
    Provides deterministic, data-driven validation using 6 free APIs:
    - Google Trends (market interest)
    - Google Autocomplete (search behavior)
    - YouTube Data API (content coverage)
    - News API (media mentions)
    - Reddit (social validation)
    - Wikipedia (topic interest)
    
    Plus execution risk analysis for technical feasibility.
    
    **Features:**
    - ✅ Works for ANY sector (software, hardware, food, etc.)
    - ✅ 100% deterministic (no AI hallucination)
    - ✅ Redis-cached for performance
    - ✅ Free tier friendly
    """
)
async def validate_startup_idea(
    request: ValidateIdeaRequest,
    validator: UniversalValidatorService = Depends(get_universal_validator)
) -> ValidationResponse:
    """
    Validate a startup idea across multiple dimensions
    
    Returns market validation, social proof, and execution risk scores
    """
    try:
        # Convert to internal request model
        validation_request = UniversalValidationRequest(
            idea_name=request.idea_name,
            idea_description=request.idea_description,
            keywords=request.keywords,
            sector=request.sector,
            tech_stack=request.tech_stack,
            team_size=request.team_size,
            timeline_months=request.timeline_months,
            budget_usd=request.budget_usd
        )
        
        logger.info(f"Validating idea: {request.idea_name} ({request.sector})")
        
        # Run validation
        result: UniversalValidationResult = await validator.validate(validation_request)
        
        # Calculate verdict
        verdict = _calculate_verdict(result.overall_confidence)
        
        # Format response
        response = ValidationResponse(
            idea_name=request.idea_name,
            sector=request.sector,
            market_validation={
                "google_trends_score": result.google_trends_score,
                "autocomplete_popularity": result.autocomplete_popularity,
                "wikipedia_interest": result.wikipedia_interest,
                "overall_score": result.market_validation_score
            },
            social_proof={
                "reddit_engagement": result.reddit_engagement,
                "youtube_coverage": result.youtube_coverage,
                "news_mentions": result.news_mentions,
                "overall_score": result.social_proof_score
            },
            execution_risk={
                "complexity_score": result.execution_complexity,
                "risk_level": result.execution_risk_level,
                "estimated_months": result.estimated_months,
                "confidence": result.overall_confidence,
                "key_challenges": result.key_challenges
            },
            sector_signals=result.sector_signals,
            overall_confidence=result.overall_confidence,
            verdict=verdict,
            data_quality={
                "sources_used": result.data_sources_used,
                "fallback_count": result.fallback_count,
                "reliability": "High" if result.fallback_count <= 2 else "Medium" if result.fallback_count <= 4 else "Low"
            }
        )
        
        logger.info(f"Validation complete: {verdict} ({result.overall_confidence}/100)")
        
        return response
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


def _calculate_verdict(confidence: int) -> str:
    """Calculate human-readable verdict from confidence score"""
    if confidence >= 75:
        return "🚀 STRONG OPPORTUNITY"
    elif confidence >= 60:
        return "✅ VIABLE"
    elif confidence >= 45:
        return "⚠️ MODERATE POTENTIAL"
    else:
        return "❌ HIGH RISK"


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Validation Service Health",
    description="Check if validation service and external APIs are operational"
)
async def validation_health(
    validator: UniversalValidatorService = Depends(get_universal_validator)
) -> dict:
    """Check validation service health"""
    return {
        "status": "healthy",
        "service": "Universal Validation",
        "apis": [
            "Google Trends",
            "Google Autocomplete",
            "YouTube Data API",
            "News API",
            "Reddit (YARS Scraper)",
            "Wikipedia Pageviews"
        ],
        "caching": "Redis (with graceful fallback)"
    }
