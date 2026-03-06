"""
Data models for Idea Lab API (FastAPI/Pydantic V2)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TimeFrame(str, Enum):
    ONE_MONTH = "1_month"
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    ONE_YEAR = "1_year"


class WizardInput(BaseModel):
    """Input from the 5-step wizard"""
    industry: str
    target_audience: str
    skill_level: SkillLevel
    skills: List[str] = []
    budget: int = Field(..., ge=0)
    time_frame: TimeFrame
    interests: Optional[str] = None
    location: Optional[str] = None


class BusinessModelSnippet(BaseModel):
    """Business model canvas snippet for an idea"""
    revenue_streams: List[str]
    key_partners: List[str]
    cost_structure: List[str]
    value_proposition: str
    customer_segments: List[str]
    channels: List[str]


class IdeaScore(BaseModel):
    """Multi-dimensional score for an idea"""
    market_size: int = Field(..., ge=0, le=100)
    differentiation: int = Field(..., ge=0, le=100)
    execution_complexity: int = Field(..., ge=0, le=100)
    capital_intensity: int = Field(..., ge=0, le=100)
    overall: int = Field(..., ge=0, le=100)


class MVPFeature(BaseModel):
    """A feature for the minimum viable product"""
    name: str
    description: str
    priority: int = Field(..., ge=1, le=3)


class StartupIdea(BaseModel):
    """Complete startup idea with all details"""
    id: str
    name: str = "Untitled"
    tagline: str = ""
    description: str = ""
    industry: Optional[str] = "Software" # Default to Software for now, but nullable
    target_customer: str = ""
    problem_solved: str = ""
    mvp_features: List[MVPFeature] = []
    business_model: Optional[BusinessModelSnippet] = None
    moonshot_channel: str = ""
    estimated_initial_cost: int = 0
    score: Optional[Dict[str, Any]] = None


class IdeaGenerationRequest(BaseModel):
    """Request to generate ideas"""
    wizard_input: WizardInput
    num_ideas: int = Field(default=5, ge=1, le=10)
    contrarian_override: bool = Field(default=False, description="Allow ideas that defy conventional market wisdom")


class IdeaGenerationResponse(BaseModel):
    """Response with generated ideas"""
    ideas: List[StartupIdea]
    generation_id: str
    input_summary: str


class ValidationExperiment(BaseModel):
    """A validation experiment template"""
    name: str
    description: str
    estimated_time: str
    estimated_cost: int
    steps: List[str]
    success_metrics: List[str]


class MarketSignal(BaseModel):
    """Market research signal"""
    search_trend: Optional[int] = None
    competitor_count: Optional[int] = None
    news_sentiment: Optional[str] = None
    trending_topics: Optional[List[str]] = None
