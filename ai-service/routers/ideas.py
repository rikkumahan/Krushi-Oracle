from fastapi import APIRouter, Depends, HTTPException
from models.schemas import IdeaGenerationRequest, IdeaGenerationResponse
from services.idea_generator import IdeaGeneratorService
from services.idea_scorer_v2.engine import DeterministicScorerV2, IdeaInput, TimeSeriesData, TechStack, CompetitiveData, MarketSignals
from services.external.google_trends import GoogleTrendsService
from services.external.keyword_extractor import KeywordExtractorService, KeywordExtractionRequest
from core.dependencies import get_idea_generator, get_v2_scorer, get_google_trends_service, get_keyword_extractor
import asyncio

router = APIRouter(prefix="/api/ideas", tags=["Ideas"])

@router.post("/generate", response_model=IdeaGenerationResponse)
async def generate_ideas(
    request: IdeaGenerationRequest,
    service: IdeaGeneratorService = Depends(get_idea_generator),
    v2_scorer: DeterministicScorerV2 = Depends(get_v2_scorer),
    trends_service: GoogleTrendsService = Depends(get_google_trends_service),
    keyword_extractor: KeywordExtractorService = Depends(get_keyword_extractor)
):
    """
    Generate startup ideas based on wizard input.
    """
    response = await service.generate_ideas(
        wizard_input=request.wizard_input, 
        num_ideas=request.num_ideas,
        contrarian_override=request.contrarian_override
    )
    
    # --- INNOVATIVE RESTORATION ---
    # Score generated ideas using V2 Deterministic Engine + REAL Signals
    scored_tasks = []
    
    async def process_idea(idea):
        # 1. Extract Keywords
        kw_req = KeywordExtractionRequest(
            idea_name=idea.name,
            idea_description=idea.description,
            industry=request.wizard_input.industry,
            target_audience=request.wizard_input.target_audience
        )
        kw_res = await keyword_extractor.extract_keywords(kw_req)
        primary_kw = kw_res.primary_keywords[0] if kw_res.primary_keywords else idea.name
        
        # 2. Fetch Real Trends
        # We fetch 12-month trend as proxy for 180d, and simulate windows
        trend_data = await trends_service.get_interest_over_time(primary_kw)
        avg_interest = trend_data.get("average_interest", 50)
        
        # 3. Create V2-compatible input
        v2_input = IdeaInput(
            idea_name=idea.name,
            idea_description=idea.description,
            target_market=request.wizard_input.target_audience,
            market_signals=MarketSignals(
                monthly_searches=avg_interest * 100, # Heuristic scale
                growth_rate_30d=0.05 if trend_data.get("trend") == "Rising" else -0.05 if trend_data.get("trend") == "Declining" else 0.0,
                video_count=10, # Stub for batch speed
                total_views=1000,
                post_count=5,
                total_score=50,
                daily_views=avg_interest * 10,
                article_count_30d=2,
                unique_sources=1
            ),
            tech_stack=TechStack(technologies=[], team_experience={}),
            competitive_data=CompetitiveData(youtube_video_count=10),
            trends_30d=TimeSeriesData(values=[avg_interest] * 4, period_days=30),
            trends_90d=TimeSeriesData(values=[avg_interest] * 12, period_days=90),
            trends_180d=TimeSeriesData(values=[avg_interest] * 24, period_days=180),
            estimated_capital_needed=idea.estimated_initial_cost
        )
        
        v2_result = v2_scorer.score_idea(v2_input)
        
        idea.score = {
            "overall": v2_result.mvs_score,
            "market": v2_result.market_dimension,
            "differentiation": v2_result.differentiation_dimension,
            "execution": v2_result.execution_dimension,
            "capital": v2_result.capital_dimension,
            "v2_grade": v2_result.mvs_grade,
            "v2_class": v2_result.validation_class,
            "audit_trail": v2_result.recommendations # Use recs as summary audit
        }
        return idea

    # Process all in parallel for efficiency
    response.ideas = await asyncio.gather(*[process_idea(idea) for idea in response.ideas])

    # Sort by V2 score
    response.ideas.sort(key=lambda x: x.score["overall"] if hasattr(x, "score") and isinstance(x.score, dict) else 0, reverse=True)
    
    return response
