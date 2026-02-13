from fastapi import APIRouter, Depends, HTTPException
from services.landing_page_generator import LandingPageGeneratorService, LandingPageRequest, LandingPageResponse
from services.canvas_generator import CanvasGeneratorService
from models.schemas import StartupIdea
from core.dependencies import get_landing_page_generator, get_canvas_generator
from typing import Dict

router = APIRouter(prefix="/api/v2/assets", tags=["V2 Assets"])

@router.post("/landing-page", response_model=LandingPageResponse)
async def generate_landing_page(
    request: LandingPageRequest,
    service: LandingPageGeneratorService = Depends(get_landing_page_generator)
):
    """
    Generate a single-file HTML landing page.
    """
    return await service.generate_page(request)

@router.post("/lean-canvas")
async def generate_lean_canvas(
    idea: StartupIdea,
    service: CanvasGeneratorService = Depends(get_canvas_generator)
):
    """
    Generate a Lean Canvas (JSON and HTML) for a startup idea.
    """
    try:
        canvas_data = service.generate_lean_canvas(idea)
        html_view = service.generate_html_lean_canvas(idea)
        return {
            "canvas_data": canvas_data,
            "html_view": html_view
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pitch-deck")
async def generate_pitch_deck(
    idea: StartupIdea,
    service: CanvasGeneratorService = Depends(get_canvas_generator)
):
    """
    Generate a 5-slide pitch deck outline.
    """
    try:
        return service.generate_pitch_outline(idea)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
