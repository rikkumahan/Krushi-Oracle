
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from verification.traffic_estimator import TrafficEstimatorService, TrafficEstimateRequest, TrafficEstimateResponse

@pytest.mark.asyncio
async def test_traffic_impression_share():
    # Mock Trends Service
    mock_trends = AsyncMock()
    # Mocking a niche market: 10,000 searches/month
    mock_trends.get_interest_over_time.return_value = {
        "average_interest": 10, # 10 * 1000 = 10,000 volume
        "trend": "Rising",
        "data_source": "Mock Live"
    }
    
    estimator = TrafficEstimatorService(trends_service=mock_trends)
    
    # CASE 1: Low Budget (Should capture small share)
    # CPC ~$5.00 (SaaS). Budget $1000 -> 200 clicks.
    # Inventory: 10,000 * 4% CTR = 400 clicks.
    # Share: 200/400 = 50%
    req_low = TrafficEstimateRequest(
        idea_name="Test SaaS",
        idea_description="Test",
        industry="saas",
        target_audience="Developers",
        budget=1000.0
    )
    
    res_low = await estimator.estimate_traffic(req_low)
    print("\n--- Low Budget Test ---")
    print(f"Budget: ${req_low.budget}")
    print(f"Clicks: {res_low.estimated_clicks}")
    print(f"Share: {res_low.trend_insights['impression_share']}")
    print(f"Warning: {res_low.trend_insights.get('market_saturation_warning')}")
    
    assert res_low.estimated_clicks == 200
    assert res_low.trend_insights['impression_share'] == "50%"
    assert res_low.trend_insights.get('market_saturation_warning') is None

    # CASE 2: High Budget (Should Saturate)
    # Budget $5000 -> 1000 clicks (naive).
    # Inventory: 400 clicks.
    # Should cap at 400.
    req_high = TrafficEstimateRequest(
        idea_name="Test SaaS",
        idea_description="Test",
        industry="saas",
        target_audience="Developers",
        budget=5000.0
    )
    
    res_high = await estimator.estimate_traffic(req_high)
    print("\n--- High Budget Test (Saturation) ---")
    print(f"Budget: ${req_high.budget}")
    print(f"Clicks: {res_high.estimated_clicks} (Expected Cap: 400)")
    print(f"Share: {res_high.trend_insights['impression_share']}")
    print(f"Warning: {res_high.trend_insights.get('market_saturation_warning')}")
    
    assert res_high.estimated_clicks == 400
    assert res_high.trend_insights['impression_share'] == "100%"
    assert res_high.trend_insights.get('market_saturation_warning') is not None
    
    print("\n✅ TEST PASSED: Impression Share logic works.")

if __name__ == "__main__":
    asyncio.run(test_traffic_impression_share())
