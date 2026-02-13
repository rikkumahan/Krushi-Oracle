
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from services.landing_page_generator import LandingPageGeneratorService, LandingPageRequest

@pytest.fixture
def mock_request():
    return LandingPageRequest(
        idea_name="CloudScan",
        tagline="Ultimate Security",
        description="AI-powered cloud security scanner",
        target_audience="DevOps Teams",
        features=["Auto-patching", "Threat Detection", "Real-time Monitoring"]
    )

@pytest.mark.asyncio
async def test_landing_page_pro_assembly(mock_request):
    service = LandingPageGeneratorService()
    service._client = MagicMock()
    
    # Mock Copywriting Response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
    {
        "hero": {
            "headline": "Secure Your Cloud in Seconds",
            "subheadline": "The future of automated security is here.",
            "cta_text": "Start Free Trial",
            "image_url": "tech security"
        },
        "features": {
            "title": "Why CloudScan?",
            "features": [
                {"title": "Auto-patching", "description": "Fix bugs while you sleep.", "icon": "fa-lock"}
            ]
        },
        "pricing": {
            "options": [
                {"name": "Free", "price": "$0", "description": "For side projects", "features": ["Basic"], "is_popular": false}
            ]
        },
        "footer_text": "Built for the modern web."
    }
    """
    service._client.chat.completions.create.return_value = mock_response
    
    response = await service.generate_page(mock_request)
    
    assert "<title>CloudScan</title>" in response.html_content
    assert "Secure Your Cloud in Seconds" in response.html_content
    assert "Why CloudScan?" in response.html_content
    assert "fa-lock" in response.html_content
    
    print("\n✅ Landing Page Pro Assembly Verified")

if __name__ == "__main__":
    asyncio.run(test_landing_page_pro_assembly(mock_request()))
