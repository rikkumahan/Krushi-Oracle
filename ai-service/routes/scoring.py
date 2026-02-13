"""
Scoring API Routes
Endpoints for idea scoring and ranking
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import StartupIdea, IdeaScore, WizardInput
from services.idea_scorer import idea_scorer

router = APIRouter()


@router.post("/score-idea", response_model=IdeaScore)
async def score_single_idea(idea: StartupIdea, wizard_input: WizardInput = None):
    """Score a single startup idea"""
    try:
        return idea_scorer.score_idea(idea, wizard_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.post("/score-batch", response_model=List[StartupIdea])
async def score_batch_ideas(ideas: List[StartupIdea], wizard_input: WizardInput = None):
    """Score multiple ideas and return sorted by score"""
    try:
        return idea_scorer.score_ideas_batch(ideas, wizard_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")


@router.get("/weights")
async def get_scoring_weights():
    """Get current scoring weights configuration"""
    return {
        "weights": idea_scorer.weights,
        "description": {
            "market_size": "TAM potential, growth rate, timing",
            "differentiation": "Uniqueness, competitive moat, innovation",
            "execution_complexity": "Ease of execution (higher = easier)",
            "capital_intensity": "Low capital needs (higher = cheaper)"
        }
    }
