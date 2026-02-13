"""
Ideas API Routes
Endpoints for idea generation and management
"""

from fastapi import APIRouter, HTTPException
from models.schemas import (
    IdeaGenerationRequest, 
    IdeaGenerationResponse, 
    WizardInput,
    MarketSignal
)
from services.idea_generator import idea_generator
from services.idea_scorer import idea_scorer
from services.market_signals import market_signals

router = APIRouter()


@router.post("/generate", response_model=IdeaGenerationResponse)
async def generate_ideas(request: IdeaGenerationRequest):
    """Generate startup ideas based on wizard input"""
    try:
        response = idea_generator.generate_ideas(
            request.wizard_input, 
            request.num_ideas
        )
        
        # Score all generated ideas
        response.ideas = idea_scorer.score_ideas_batch(
            response.ideas, 
            request.wizard_input
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Idea generation failed: {str(e)}")


@router.post("/validate")
async def validate_wizard_input(wizard_input: WizardInput):
    """Validate wizard input before generation"""
    errors = []
    
    if wizard_input.budget < 100:
        errors.append("Budget should be at least $100")
    
    if len(wizard_input.industry) < 2:
        errors.append("Please specify a valid industry")
    
    if len(wizard_input.target_audience) < 3:
        errors.append("Please specify your target audience")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    return {"valid": True, "message": "Input validated successfully"}


@router.post("/market-signals", response_model=MarketSignal)
async def get_market_signals(keywords: list[str], region: str = "US"):
    """Get market research signals for keywords"""
    if not keywords:
        raise HTTPException(status_code=400, detail="At least one keyword required")
    
    return market_signals.get_market_signals(keywords, region)
