from functools import lru_cache
from fastapi import Depends
from core.config import Settings, get_settings
from services.idea_generator import IdeaGeneratorService
from verification.tech_feasibility import TechFeasibilityService
from services.landing_page_generator import LandingPageGeneratorService
from services.canvas_generator import CanvasGeneratorService
from verification.unit_economics import UnitEconomicsSimulator
from verification.traffic_estimator import TrafficEstimatorService
from services.external.google_trends import GoogleTrendsService
from services.external.keyword_extractor import KeywordExtractorService
from services.idea_scorer_v2.engine import DeterministicScorerV2
from services.idea_scorer_v2.mvs_calculator import MarketValidationScorer

# Note: FastAPI Pro pattern - Don't use @lru_cache with Depends() parameters
# FastAPI handles caching at the request level automatically

def get_idea_generator(settings: Settings = Depends(get_settings)) -> IdeaGeneratorService:
    return IdeaGeneratorService(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

def get_tech_feasibility_service(settings: Settings = Depends(get_settings)) -> TechFeasibilityService:
    return TechFeasibilityService(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

def get_landing_page_generator(settings: Settings = Depends(get_settings)) -> LandingPageGeneratorService:
    return LandingPageGeneratorService(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

@lru_cache
def get_unit_economics_service() -> UnitEconomicsSimulator:
    return UnitEconomicsSimulator()

@lru_cache
def get_google_trends_service() -> GoogleTrendsService:
    return GoogleTrendsService()

def get_keyword_extractor(settings: Settings = Depends(get_settings)) -> KeywordExtractorService:
    return KeywordExtractorService(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)

def get_traffic_estimator(
    trends: GoogleTrendsService = Depends(get_google_trends_service),
    keyword_extractor: KeywordExtractorService = Depends(get_keyword_extractor)
) -> TrafficEstimatorService:
    return TrafficEstimatorService(trends_service=trends, keyword_extractor=keyword_extractor)

@lru_cache
def get_canvas_generator() -> CanvasGeneratorService:
    return CanvasGeneratorService()

@lru_cache
def get_v2_scorer() -> DeterministicScorerV2:
    return DeterministicScorerV2()
