
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from verification.universal_validator import UniversalValidatorService, UniversalValidationRequest
from services.external.software_scanner import SoftwareScannerService

@pytest.mark.asyncio
async def test_sector_signals_flow():
    # Mock dependencies
    mock_trends = AsyncMock()
    mock_trends.get_interest_over_time.return_value = {"average_interest": 50, "growth_rate": 0.1}
    
    mock_autocomplete = AsyncMock()
    mock_autocomplete.get_suggestions.return_value = {"popularity_score": 60}
    
    mock_youtube = AsyncMock()
    mock_youtube.search_videos.return_value = {"video_count": 50, "engagement_score": 70}
    
    mock_news = AsyncMock()
    mock_news.search_articles.return_value = {"article_count": 10, "source_diversity": 3}
    
    mock_reddit = AsyncMock()
    mock_reddit.search_discussions.return_value = {"post_count": 20, "engagement_score": 60}
    
    mock_wikipedia = AsyncMock()
    mock_wikipedia.get_pageviews.return_value = {"daily_views": 500, "interest_score": 65}
    
    # Mock Software Scanner (The critical part)
    mock_software = AsyncMock()
    mock_software.scan_market.return_value = {
        "repo_count": 15000,
        "saturation": "High",
        "data_source": "Mock GitHub"
    }
    
    mock_healthcare = AsyncMock()
    mock_product = AsyncMock()
    mock_execution = MagicMock() # Execution analyzer is synchronous or uses internal logic

    # Initialize Service
    service = UniversalValidatorService(
        trends_service=mock_trends,
        autocomplete_service=mock_autocomplete,
        youtube_service=mock_youtube,
        news_service=mock_news,
        reddit_service=mock_reddit,
        wikipedia_service=mock_wikipedia,
        software_scanner=mock_software,
        healthcare_scanner=mock_healthcare,
        product_scanner=mock_product,
        execution_analyzer=mock_execution
    )

    request = UniversalValidationRequest(
        idea_name="Test SaaS",
        idea_description="A test SaaS platform",
        keywords=["simulated"],
        sector="software"
    )

    # Run Validation
    result = await service.validate(request)

    # ASSERTIONS
    print("\n--- Sector Signals Verification ---")
    print(f"Sector: {result.sector}")
    print(f"Signals: {result.sector_signals}")

    assert result.sector == "software"
    assert "repo_count" in result.sector_signals
    assert result.sector_signals["repo_count"] == 15000
    assert result.sector_signals["saturation"] == "High"
    assert "momentum" in result.sector_signals
    
    print("✅ TEST PASSED: Sector signals correctly propagated.")

if __name__ == "__main__":
    asyncio.run(test_sector_signals_flow())
