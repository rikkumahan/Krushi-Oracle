"""
Export API Routes
Endpoints for generating Lean Canvas, One-Pager, and Pitch Outline
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict
from models.schemas import StartupIdea
from services.canvas_generator import canvas_generator

router = APIRouter()


@router.post("/lean-canvas")
async def generate_lean_canvas(idea: StartupIdea) -> Dict[str, str]:
    """Generate Lean Canvas JSON for an idea"""
    try:
        return canvas_generator.generate_lean_canvas(idea)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Canvas generation failed: {str(e)}")


@router.post("/lean-canvas-html", response_class=HTMLResponse)
async def generate_lean_canvas_html(idea: StartupIdea):
    """Generate Lean Canvas as HTML page"""
    try:
        return canvas_generator.generate_html_lean_canvas(idea)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML canvas generation failed: {str(e)}")


@router.post("/one-pager")
async def generate_one_pager(idea: StartupIdea) -> Dict[str, str]:
    """Generate one-page executive summary as markdown"""
    try:
        markdown = canvas_generator.generate_one_pager(idea)
        return {"format": "markdown", "content": markdown}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"One-pager generation failed: {str(e)}")


@router.post("/pitch-outline")
async def generate_pitch_outline(idea: StartupIdea) -> Dict[str, str]:
    """Generate 5-slide pitch deck outline"""
    try:
        return canvas_generator.generate_pitch_outline(idea)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pitch outline generation failed: {str(e)}")
