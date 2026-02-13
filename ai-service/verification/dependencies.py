"""
Dependency injection for universal validator services
Provides singleton instances with Redis caching
"""

from functools import lru_cache
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
from verification.universal_validator import UniversalValidatorService
from services.redis_cache import get_cache_service


@lru_cache()
def get_universal_validator() -> UniversalValidatorService:
    """
    Get or create UniversalValidatorService singleton
    All services are initialized with Redis caching (where supported)
    """
    # Get cache service
    cache = get_cache_service()
    
    # Initialize all services
    trends = GoogleTrendsService()
    autocomplete = GoogleAutocompleteService(cache=cache)
    youtube = YouTubeDataService(cache=cache)
    news = NewsAPIService(cache=cache)
    reddit = RedditScraperService(cache=cache)
    wikipedia = WikipediaPageviewsService(cache=cache)
    
    # Sector Scanners
    software = SoftwareScannerService()
    healthcare = HealthcareScannerService()
    product = ProductScannerService()
    
    execution = ExecutionRiskAnalyzer()
    
    # Create validator with all dependencies
    validator = UniversalValidatorService(
        trends_service=trends,
        autocomplete_service=autocomplete,
        youtube_service=youtube,
        news_service=news,
        reddit_service=reddit,
        wikipedia_service=wikipedia,
        software_scanner=software,
        healthcare_scanner=healthcare,
        product_scanner=product,
        execution_analyzer=execution
    )
    
    return validator
