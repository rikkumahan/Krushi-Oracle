from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class CompanyOutcome(str, Enum):
    ACQUIRED = "acquired"
    FAILED = "failed"
    GROWING = "growing"
    PIVOTED = "pivoted"
    UNKNOWN = "unknown"

class SimilarCompany(BaseModel):
    name: str
    description: str
    business_model: str  # "B2B SaaS", "Marketplace", etc.
    outcome: CompanyOutcome
    outcome_year: Optional[int] = None
    funding_raised_usd: Optional[int] = None
    exit_value_usd: Optional[int] = None
    founded_year: Optional[int] = None
    time_to_exit_years: Optional[float] = None
    key_lesson: str
    similarity_score: float = 0.0  # 0-100
    data_sources: List[str] = ["producthunt"]
    url: Optional[str] = None

class ComparisonRequest(BaseModel):
    idea_name: str
    idea_description: str
    target_market: str
    industry: Optional[str] = None

class ComparisonResponse(BaseModel):
    similar_companies: List[SimilarCompany]
    search_keywords: List[str]
    total_found: int
    data_quality_score: float  # How reliable is this data
