"""
Grounded Generators Router
All endpoints use 100% validated data from deterministic validators
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from models.schemas import (
    IdeaGenerationRequest,
    IdeaGenerationResponse,
    StartupIdea
)
from services.grounded_idea_generator import GroundedIdeaGeneratorService
from services.grounded_landing_page_generator import (
    GroundedLandingPageGenerator,
    LandingPageRequest,
    LandingPageResponse
)
from services.grounded_canvas_generator import GroundedCanvasGenerator
from services.grounded_pitch_deck_generator import GroundedPitchDeckGenerator
from core.grounded_dependencies import (
    get_grounded_idea_generator,
    get_grounded_landing_page,
    get_grounded_canvas,
    get_grounded_pitch
)

router = APIRouter(prefix="/api/grounded", tags=["Grounded Generators"])

@router.post("/ideas/generate", response_model=IdeaGenerationResponse)
async def generate_grounded_ideas(
    request: IdeaGenerationRequest,
    service: GroundedIdeaGeneratorService = Depends(get_grounded_idea_generator)
):
    """
    Generate startup ideas with validation-in-the-loop.
    Only returns ideas that pass ALL 7 validators.
    
    Features:
    - Constraint extraction from user input
    - Market opportunity discovery via Google Trends
    - Competitive gap analysis via Smart Comparison
    - Real-time validation of each generated idea
    - 60%+ validation rate target
    """
    try:
        response = await service.generate_validated_ideas(
            wizard_input=request.wizard_input,
            num_ideas=request.num_ideas,
            contrarian_override=request.contrarian_override
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating grounded ideas: {str(e)}")

@router.post("/landing-page/generate", response_model=LandingPageResponse)
async def generate_grounded_landing_page(
    request: LandingPageRequest,
    service: GroundedLandingPageGenerator = Depends(get_grounded_landing_page)  # FIXED
):
    """
    Generate landing page grounded in ALL 7 validation results.
    
    Features:
    - Runs all 7 validators on user's idea
    - LLM generates copy USING validation data (not inventing)
    - Deterministic CRO validation (headline length, CTA format)
    - Template assembly with real statistics
    - 100% of stats from validation data
    """
    try:
        import traceback
        logging.info(f"Generating landing page for: {request.idea_name}")
        response = await service.generate_page(request)
        logging.info(f"Successfully generated landing page")
        return response
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        logging.error(f"Error generating grounded landing page: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)

@router.post("/canvas/generate")
async def generate_grounded_canvas(
    idea: StartupIdea,
    service: GroundedCanvasGenerator = Depends(get_grounded_canvas)  # FIXED
):
    """
    Generate Lean Canvas with each section grounded in specific validators.
    
    Features:
    - Problem: Reddit discussions (Universal Validator)
    - Customer Segments: Top keywords (Traffic Estimator)
    - UVP: Strategic positioning (Strategic Audit)
    - Solution: Tech stack (Tech Feasibility)
    - Channels: Traffic sources (Traffic Estimator)
    - Revenue: LTV/CAC (Unit Economics)
    - Costs: Burn rate (Unit Economics)
    - Metrics: MVS Score (V2 Scorer)
    - Advantage: Proof points (Smart Comparison)
    - 90%+ data-driven content
    """
    try:
        response = await service.generate_canvas(idea)
        return response
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        logging.error(f"Error generating grounded canvas: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)

@router.post("/canvas/html")
async def generate_grounded_canvas_html(
    idea: StartupIdea,
    service: GroundedCanvasGenerator = Depends(get_grounded_canvas)  # FIXED
):
    """Generate HTML version of grounded Lean Canvas"""
    try:
        html = await service.generate_html_canvas(idea)
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating canvas HTML: {str(e)}")

@router.post("/pitch/generate")
async def generate_grounded_pitch(
    idea: StartupIdea,
    service: GroundedPitchDeckGenerator = Depends(get_grounded_pitch)  # FIXED
):
    """
    Generate pitch deck with 100% numbers from validators.
    
    Features:
    - Deterministic TAM/SAM/SOM calculations
    - All numbers from validation data
    - LLM generates narrative only (5% of content)
    - 9 slides with complete source citations
    - 95%+ accuracy guarantee
    
    Slides:
    1. Title (MVS Score)
    2. Problem (Reddit data)
    3. Market (TAM/SAM/SOM)
    4. Solution (Tech stack)
    5. Traction (Validation scores)
    6. Business Model (Unit economics)
    7. Competition (Similar companies)
    8. Go-to-Market (Traffic channels)
    9. The Ask (Funding calculation)
    """
    try:
        response = await service.generate_pitch(idea)
        return response
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        logging.error(f"Error generating grounded pitch: {error_details}")
        raise HTTPException(status_code=500, detail=error_details)

@router.post("/pitch/html")
async def generate_grounded_pitch_html(
    idea: StartupIdea,
    service: GroundedPitchDeckGenerator = Depends(get_grounded_pitch)  # FIXED
):
    """Generate HTML version of grounded pitch deck"""
    try:
        html = await service.generate_html_pitch(idea)
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating pitch HTML: {str(e)}")
