from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from models.schemas import IdeaGenerationRequest, IdeaGenerationResponse
from verification.unit_economics import UnitEconomicsSimulator, UnitEconomicsInput
from services.idea_scorer_v2.tech_analyzer import TechStackAnalyzer, TechStack, Technology, TechCategory
from verification.traffic_estimator import TrafficEstimatorService, TrafficEstimateRequest, TrafficEstimateResponse
from core.dependencies import get_unit_economics_service, get_v2_scorer, get_traffic_estimator, get_keyword_extractor
from services.external.keyword_extractor import KeywordExtractorService
import logging
import traceback

# Configure logging per Python Pro best practices
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/verification", tags=["V2 Verification"])

@router.post("/economics")
async def check_unit_economics(
    inputs: UnitEconomicsInput,
    service: UnitEconomicsSimulator = Depends(get_unit_economics_service)
):
    """
    Innovative Assessment: Deterministic Unit Economics Simulator.
    """
    return service.calculate(inputs)

class TechFeasibilityRequest(BaseModel):
    idea_name: str
    description: str

@router.post("/feasibility")
async def check_tech_feasibility(
    request: TechFeasibilityRequest,
    v2_analyzer: TechStackAnalyzer = Depends(lambda: TechStackAnalyzer()),
    keyword_extractor: KeywordExtractorService = Depends(get_keyword_extractor)
):
    """
    Innovative Assessment: Uses LLM for tech extraction + V2 Deterministic Interaction Matrix.
    """
    idea_name = request.idea_name
    description = request.description
    # 1. Extract technologies from description using professional extractor
    tech_names = await keyword_extractor.extract_keywords(f"{idea_name}: {description}")
    
    # 2. Map to V2 Technology objects
    tech_db = TechStackAnalyzer.TECH_DB
    technologies = []
    for name in tech_names[:5]: # Limit to top 5
        if name in tech_db:
            technologies.append(tech_db[name])
        else:
            # Create heuristic tech object if not in DB
            technologies.append(Technology(name, TechCategory.BACKEND, 5, "STABLE", 2))
            
    # 3. Use V2 professional interaction matrix
    stack = TechStack(technologies=technologies, team_experience={t.name: "FAMILIAR" for t in technologies})
    v2_result = v2_analyzer.analyze_stack(stack)
    
    return {
        "idea_name": idea_name,
        "execution_score": v2_result.get("execution_score", 50),
        "complexity_rating": v2_result.get("complexity_rating", "Medium"),
        "technologies_analyzed": [t.name for t in technologies],
        "risk_factors": v2_result.get("risk_factors", []),
        "synergy_bonus": v2_result.get("synergy_bonus", 0),
        "innovation_level": "V2 Deterministic"
    }

@router.post("/traffic", response_model=TrafficEstimateResponse)
async def estimate_traffic(
    request: TrafficEstimateRequest,
    service: TrafficEstimatorService = Depends(get_traffic_estimator)
):
    """
    Estimate ad traffic volume based on budget + Google Trends data + LLM keyword extraction.
    """
    try:
        logger.info(f"Traffic estimation request: {request.idea_name}")
        result = await service.estimate_traffic(request)
        logger.info(f"Traffic estimation successful for: {request.idea_name}")
        return result
    except Exception as e:
        logger.error(f"Traffic estimation failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Traffic estimation error: {str(e)}"
        )
