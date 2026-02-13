
import pytest
from unittest.mock import MagicMock
from models.schemas import StartupIdea, BusinessModelSnippet, MVPFeature
from services.canvas_generator import CanvasGeneratorService

@pytest.fixture
def mock_idea():
    return StartupIdea(
        id="test-id", # Add ID as it is required
        name="TestIdea",
        description="A test startup",
        problem_solved="Solving testing",
        target_customer="Developers",
        business_model=BusinessModelSnippet(
            revenue_streams=["SaaS"],
            channels=["Web"],
            cost_structure=["Hosting"],
            value_proposition="Faster testing",
            key_partners=["Suppliers"],
            customer_segments=["Developers"]
        ),
        mvp_features=[]
    )

def test_canvas_generator_fallback(mock_idea):
    # Test fallback when no client is present
    service = CanvasGeneratorService()
    service.client = None # Force fallback
    
    canvas = service.generate_lean_canvas(mock_idea)
    
    assert canvas["problem"] == "Solving testing"
    assert "revenue_streams" in canvas
    print("\n✅ Canvas Fallback Logic Verified")

def test_canvas_generator_llm(mock_idea):
    # Test LLM integration with Mock
    service = CanvasGeneratorService()
    service.client = MagicMock()
    
    # Mock Response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"problem": "AI Generated Problem", "solution": "AI Solution"}'
    service.client.chat.completions.create.return_value = mock_response
    
    canvas = service.generate_lean_canvas(mock_idea)
    
    assert canvas["problem"] == "AI Generated Problem"
    assert canvas["solution"] == "AI Solution"
    print("\n✅ Canvas LLM Logic Verified")

