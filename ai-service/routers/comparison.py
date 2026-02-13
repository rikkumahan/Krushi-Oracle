from fastapi import APIRouter, HTTPException
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.comparison_schemas import ComparisonRequest, ComparisonResponse
from services.comparison.comparison_engine import ComparisonEngine

router = APIRouter(prefix="/api/v2/comparison", tags=["V2 Smart Comparison Search"])
engine = ComparisonEngine()

@router.post("/find-similar", response_model=ComparisonResponse)
async def find_similar_companies(request: ComparisonRequest):
    """
    Find 5 real-world startups similar to the provided idea and their outcomes.
    
    This endpoint uses a multi-stage pipeline:
    1. Keyword Extraction (LLM)
    2. Product Hunt Search (External API)
    3. Outcome Classification & Insight Generation (LLM)
    4. Similarity Ranking (Embeddings)
    """
    try:
             
        result = await engine.find_similar_companies(request)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in find_similar_companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))
