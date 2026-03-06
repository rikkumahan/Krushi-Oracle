"""
Improved Dependency injection for grounded generators.
Provides factory functions with proper type hints and Azure API validation.
"""

import os
import logging
from typing import Optional

# Import REAL validators from existing services - ALL CORRECT CLASS NAMES
from verification.universal_validator import UniversalValidatorService
from services.idea_scorer_v2.engine import DeterministicScorerV2
from verification.tech_feasibility import TechFeasibilityService
from verification.unit_economics import UnitEconomicsSimulator
from verification.traffic_estimator import TrafficEstimatorService
from services.comparison.comparison_engine import ComparisonEngine
from services.explanatory.strategic_audit_agent import StrategicAuditAgent
from services.external.google_trends import GoogleTrendsService
from core.config import get_settings

logger = logging.getLogger(__name__)

# Singleton instances - REAL validators
_universal_validator: Optional[UniversalValidatorService] = None
_v2_scorer: Optional[DeterministicScorerV2] = None
_tech_checker: Optional[TechFeasibilityService] = None
_economics_sim: Optional[UnitEconomicsSimulator] = None
_traffic_est: Optional[TrafficEstimatorService] = None
_comparison_engine: Optional[ComparisonEngine] = None
_strategic_agent: Optional[StrategicAuditAgent] = None
_trends_service: Optional[GoogleTrendsService] = None

# Forward declarations for generators to avoid circular imports during type checking
# The actual imports will happen inside the factory functions or be handled by the router
_grounded_idea_gen = None
_grounded_landing_page = None
_grounded_canvas = None
_grounded_pitch = None

def get_api_key() -> Optional[str]:
    """
    Get API key for LLM (Azure or OpenAI).
    Returns None if no API key is configured (generators will use fallback mode).
    """
    settings = get_settings()
    
    # Priority: Azure OpenAI > Regular OpenAI
    if settings.AZURE_OPENAI_KEY:
        return settings.AZURE_OPENAI_KEY
    elif settings.OPENAI_API_KEY:
        return settings.OPENAI_API_KEY
    else:
        logger.warning("No LLM API key configured - generators will use fallback/stub mode")
        return None

# REAL validator factory functions
def get_universal_validator() -> UniversalValidatorService:
    global _universal_validator
    if _universal_validator is None:
        # UniversalValidatorService needs many dependencies - create with defaults
        from services.external.google_trends import GoogleTrendsService
        from services.external.google_autocomplete import GoogleAutocompleteService
        from services.external.youtube_data import YouTubeDataService
        from services.external.news_api import NewsAPIService
        from services.external.reddit_scraper import RedditScraperService
        from services.external.wikipedia_pageviews import WikipediaPageviewsService
        from services.external.software_scanner import SoftwareScannerService
        from services.external.healthcare_scanner import HealthcareScannerService
        from services.external.product_scanner import ProductScannerService
        from verification.execution_risk import ExecutionRiskAnalyzer
        
        _universal_validator = UniversalValidatorService(
            trends_service=GoogleTrendsService(),
            autocomplete_service=GoogleAutocompleteService(),
            youtube_service=YouTubeDataService(),
            news_service=NewsAPIService(),
            reddit_service=RedditScraperService(),
            wikipedia_service=WikipediaPageviewsService(),
            software_scanner=SoftwareScannerService(),
            healthcare_scanner=HealthcareScannerService(),
            product_scanner=ProductScannerService(),
            execution_analyzer=ExecutionRiskAnalyzer()
        )
    return _universal_validator

def get_v2_scorer() -> DeterministicScorerV2:
    global _v2_scorer
    if _v2_scorer is None:
        _v2_scorer = DeterministicScorerV2()
    return _v2_scorer

def get_tech_checker() -> TechFeasibilityService:
    global _tech_checker
    if _tech_checker is None:
        settings = get_settings()
        _tech_checker = TechFeasibilityService(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    return _tech_checker

def get_economics_simulator() -> UnitEconomicsSimulator:
    global _economics_sim
    if _economics_sim is None:
        _economics_sim = UnitEconomicsSimulator()
    return _economics_sim

def get_traffic_estimator() -> TrafficEstimatorService:
    global _traffic_est
    if _traffic_est is None:
        _traffic_est = TrafficEstimatorService(
            trends_service=GoogleTrendsService(), # Create new instance if needed
            keyword_extractor=None  # Will use internal logic
        )
    return _traffic_est

def get_comparison_engine() -> ComparisonEngine:
    global _comparison_engine
    if _comparison_engine is None:
        _comparison_engine = ComparisonEngine()
    return _comparison_engine

def get_strategic_agent() -> StrategicAuditAgent:
    global _strategic_agent
    if _strategic_agent is None:
        _strategic_agent = StrategicAuditAgent()
    return _strategic_agent

def get_trends_service() -> GoogleTrendsService:
    global _trends_service
    if _trends_service is None:
        _trends_service = GoogleTrendsService()
    return _trends_service

def get_openai_client_dependency():
    """Get the standard OpenAI/Azure client"""
    from utils.openai_helper import get_openai_client
    return get_openai_client()

def get_model_name_dependency():
    """Get the standard OpenAI model/deployment name"""
    from utils.openai_helper import get_model_name
    return get_model_name()

# Grounded generator factory functions
def get_grounded_idea_generator():
    global _grounded_idea_gen
    if _grounded_idea_gen is None:
        from services.grounded_idea_generator import GroundedIdeaGeneratorService
        _grounded_idea_gen = GroundedIdeaGeneratorService(
            client=get_openai_client_dependency(),
            universal_validator=get_universal_validator(),
            v2_scorer=get_v2_scorer(),
            tech_feasibility=get_tech_checker(),
            economics_simulator=get_economics_simulator(),
            traffic_estimator=get_traffic_estimator(),
            comparison_engine=get_comparison_engine(),
            strategic_agent=get_strategic_agent(),
            trends_service=get_trends_service(),
            model=get_model_name_dependency()
        )
    return _grounded_idea_gen

def get_grounded_landing_page():
    global _grounded_landing_page
    if _grounded_landing_page is None:
        from services.grounded_landing_page_generator import GroundedLandingPageGenerator
        _grounded_landing_page = GroundedLandingPageGenerator(
            client=get_openai_client_dependency(),
            universal_validator=get_universal_validator(),
            v2_scorer=get_v2_scorer(),
            tech_feasibility=get_tech_checker(),
            economics_simulator=get_economics_simulator(),
            traffic_estimator=get_traffic_estimator(),
            comparison_engine=get_comparison_engine(),
            strategic_agent=get_strategic_agent(),
            model=get_model_name_dependency()
        )
    return _grounded_landing_page

def get_grounded_canvas():
    global _grounded_canvas
    if _grounded_canvas is None:
        from services.grounded_canvas_generator import GroundedCanvasGenerator
        _grounded_canvas = GroundedCanvasGenerator(
            client=get_openai_client_dependency(),
            universal_validator=get_universal_validator(),
            v2_scorer=get_v2_scorer(),
            tech_feasibility=get_tech_checker(),
            economics_simulator=get_economics_simulator(),
            traffic_estimator=get_traffic_estimator(),
            comparison_engine=get_comparison_engine(),
            strategic_agent=get_strategic_agent(),
            model=get_model_name_dependency()
        )
    return _grounded_canvas

def get_grounded_pitch():
    global _grounded_pitch
    if _grounded_pitch is None:
        from services.grounded_pitch_deck_generator import GroundedPitchDeckGenerator
        _grounded_pitch = GroundedPitchDeckGenerator(
            client=get_openai_client_dependency(),
            universal_validator=get_universal_validator(),
            v2_scorer=get_v2_scorer(),
            tech_feasibility=get_tech_checker(),
            economics_simulator=get_economics_simulator(),
            traffic_estimator=get_traffic_estimator(),
            comparison_engine=get_comparison_engine(),
            strategic_agent=get_strategic_agent(),
            model=get_model_name_dependency()
        )
    return _grounded_pitch
