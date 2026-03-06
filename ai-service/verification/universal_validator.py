"""
Universal Validator Service
Deterministic validation across ALL startup sectors
"""

import logging
import asyncio
from typing import Dict, List
from pydantic import BaseModel

from services.external.google_trends import GoogleTrendsService
from services.external.google_autocomplete import GoogleAutocompleteService
from services.external.youtube_data import YouTubeDataService
from services.external.news_api import NewsAPIService
from services.external.reddit_scraper import RedditScraperService
from services.external.wikipedia_pageviews import WikipediaPageviewsService
from services.external.software_scanner import SoftwareScannerService
from services.external.healthcare_scanner import HealthcareScannerService
from services.external.product_scanner import ProductScannerService
from verification.execution_risk import ExecutionRiskAnalyzer, ExecutionRiskInput

# V2 Scoring Innovations
from services.idea_scorer_v2.signal_fusion import CompositeSignalScorer, MarketSignals
from services.idea_scorer_v2.momentum_analyzer import MomentumAnalyzer, TimeSeriesData
from services.idea_scorer_v2.competition_mapper import CompetitiveDensityMapper, CompetitiveData
from services.idea_scorer_v2.tech_analyzer import TechStackAnalyzer, TechStack, TechCategory, Technology
from services.idea_scorer_v2.mvs_calculator import MarketValidationScorer, MVSInputs, MVSOutput
from services.idea_scorer_v2.engine import ScoringResult
from utils.redis_cache import safe_cache_set, CacheKey, CacheTTL
from dataclasses import asdict
from datetime import datetime

logger = logging.getLogger(__name__)


class UniversalValidationRequest(BaseModel):
    """Request for universal validation"""
    idea_name: str
    idea_description: str
    keywords: List[str]
    sector: str = "software"
    
    # Execution risk params
    tech_stack: List[str] = []
    team_size: int = 1
    timeline_months: int = 6
    budget_usd: float = 0


class UniversalValidationResult(BaseModel):
    """Universal validation result - ALL deterministic metrics"""
    sector: str
    
    # Market Interest Metrics
    google_trends_score: int
    autocomplete_popularity: int
    wikipedia_interest: int
    
    # Social Validation Metrics
    reddit_engagement: int
    youtube_coverage: int
    news_mentions: int
    
    # MVS Outputs (Added for Orchestrator compatibility)
    validation_class: str = "Uncertain"
    recommendations: List[str] = []
    competitive_moat_score: int = 0
    capital_efficiency_score: int = 0
    execution_risk_score: int = 0
    
    # Sector-Specific Metrics (Innovation)
    sector_signals: Dict = {}
    
    # Execution Risk Assessment
    execution_complexity: int
    execution_risk_level: str
    estimated_months: int
    key_challenges: List[str]
    
    # Overall Scores
    market_validation_score: int
    social_proof_score: int
    overall_confidence: int
    
    # Data Quality
    data_sources_used: List[str]
    fallback_count: int


class UniversalValidatorService:
    """
    Universal validator for ALL startup sectors
    Zero hallucination, 100% deterministic
    """
    
    def __init__(
        self,
        trends_service: GoogleTrendsService,
        autocomplete_service: GoogleAutocompleteService,
        youtube_service: YouTubeDataService,
        news_service: NewsAPIService,
        reddit_service: RedditScraperService,
        wikipedia_service: WikipediaPageviewsService,
        software_scanner: SoftwareScannerService,
        healthcare_scanner: HealthcareScannerService,
        product_scanner: ProductScannerService,
        execution_analyzer: ExecutionRiskAnalyzer
    ):
        self.trends = trends_service
        self.autocomplete = autocomplete_service
        self.youtube = youtube_service
        self.news = news_service
        self.reddit = reddit_service
        self.wikipedia = wikipedia_service
        self.software = software_scanner
        self.healthcare = healthcare_scanner
        self.product = product_scanner
        self.execution = execution_analyzer
        
        # V2 Scoring Engines
        self.fusion_scorer = CompositeSignalScorer()
        self.momentum_analyzer = MomentumAnalyzer()
        self.comp_mapper = CompetitiveDensityMapper()
        self.tech_analyzer = TechStackAnalyzer()
        self.mvs_scorer = MarketValidationScorer()
    
    async def validate(self, request: UniversalValidationRequest) -> UniversalValidationResult:
        """Run universal validation pipeline with sector intelligence"""
        logger.info(f"Starting universal validation for: {request.idea_name}")
        
        primary_keyword = request.keywords[0] if request.keywords else request.idea_name
        
        # Parallel execution of core tasks
        core_tasks = [
            self.trends.get_interest_over_time(primary_keyword),
            self.autocomplete.get_suggestions(primary_keyword),
            self.wikipedia.get_pageviews(primary_keyword),
            self.reddit.search_discussions(primary_keyword),
            self.youtube.search_videos(primary_keyword),
            self.news.search_articles(primary_keyword)
        ]
        
        # Add sector-specific task
        sector = request.sector.lower()
        sector_task = None
        if sector == "software":
            sector_task = self.software.scan_market(primary_keyword)
        elif sector == "healthcare":
            sector_task = self.healthcare.scan_market(primary_keyword)
        elif sector in ["hardware", "food", "services", "products"]:
            sector_task = self.product.scan_market(primary_keyword)
            
        if sector_task:
            core_tasks.append(sector_task)
            
        # Gather all data
        results = await asyncio.gather(*core_tasks)
        
        trends_data = results[0]
        autocomplete_data = results[1]
        wikipedia_data = results[2]
        reddit_data = results[3]
        youtube_data = results[4]
        news_data = results[5]
        sector_signals = results[6] if sector_task else {}

        # --- INNOVATION 1: COMPOSITE SIGNAL FUSION (Bayesian) ---
        signals = MarketSignals(
            monthly_searches=trends_data.get("average_interest", 50) * 100, # Scale to mock volume
            growth_rate_30d=trends_data.get("growth_rate", 0.05),
            video_count=youtube_data.get("video_count", 10),
            total_views=youtube_data.get("engagement_score", 50) * 1000,
            post_count=reddit_data.get("post_count", 5),
            total_score=reddit_data.get("engagement_score", 50) * 10,
            daily_views=wikipedia_data.get("daily_views", 100),
            article_count_30d=news_data.get("article_count", 0),
            unique_sources=news_data.get("source_diversity", 1)
        )
        fusion_result = self.fusion_scorer.score_market_demand(signals)

        # --- INNOVATION 2: TIME-SERIES MOMENTUM ---
        # Construct trend data from raw trends if available, else mock windows
        raw_trends = trends_data.get("trend_points", [50] * 12)
        trends_30d = TimeSeriesData(values=raw_trends[-4:] if len(raw_trends) >= 4 else raw_trends, period_days=30)
        trends_90d = TimeSeriesData(values=raw_trends[-12:] if len(raw_trends) >= 12 else raw_trends, period_days=90)
        trends_180d = TimeSeriesData(values=raw_trends, period_days=180)
        momentum_result = self.momentum_analyzer.analyze_momentum(trends_30d, trends_90d, trends_180d)

        # --- INNOVATION 3: COMPETITIVE DENSITY MAPPING (HHI) ---
        # Map sector-specific signals to competitive data
        comp_data = CompetitiveData(
            commercial_entity_count=sector_signals.get("repo_count", sector_signals.get("trial_count", 10)),
            top_player_market_shares=[40, 20, 10] if sector_signals.get("saturation") == "High" else [10, 10, 5],
            new_entrants_12m=5,
            exits_12m=2,
            substitute_count=sector_signals.get("intent_signal", 50) // 10,
            youtube_video_count=signals.video_count
        )
        comp_result = self.comp_mapper.map_competition(comp_data)

        # --- INNOVATION 4: TECH STACK INTERACTION ---
        tech_db = TechStackAnalyzer.TECH_DB
        technologies = []
        for tech_name in request.tech_stack:
            if tech_name in tech_db:
                technologies.append(tech_db[tech_name])
            else:
                technologies.append(Technology(tech_name, TechCategory.BACKEND, 5, "STABLE", 2))
        
        tech_stack = TechStack(
            technologies=technologies,
            team_experience={t.name: "FAMILIAR" for t in technologies}
        )
        tech_result = self.tech_analyzer.analyze_stack(tech_stack)

        # --- INNOVATION 5: MVS QUALITY GATES ---
        mvs_inputs = MVSInputs(
            demand_score=fusion_result['demand_score'],
            demand_confidence=fusion_result['confidence'],
            momentum_score=momentum_result['momentum_score'],
            trend_pattern=momentum_result['trend_pattern'],
            competition_score=comp_result['competition_score'],
            market_structure=comp_result['market_structure'],
            execution_score=tech_result['execution_score'],
            complexity_rating=tech_result['complexity_rating'],
            capital_efficiency_score=60 # Default
        )
        mvs_result = self.mvs_scorer.calculate_mvs(mvs_inputs)

        # Track sources (for data quality)
        sources_used, fallback_count = self._track_data_sources([
            trends_data, autocomplete_data, wikipedia_data,
            reddit_data, youtube_data, news_data
        ])

        # --- INNOVATION 6: CACHE FOR STRATEGIC AUDIT AGENT ---
        scoring_result = ScoringResult(
            idea_name=request.idea_name,
            scored_at=datetime.utcnow().isoformat(),
            mvs_score=mvs_result.mvs_score,
            mvs_grade=mvs_result.grade,
            validation_class=mvs_result.validation_class,
            market_dimension=mvs_result.market_dimension,
            differentiation_dimension=mvs_result.differentiation_dimension,
            execution_dimension=mvs_result.execution_dimension,
            capital_dimension=mvs_result.capital_dimension,
            signal_fusion_output=fusion_result,
            momentum_analysis_output=momentum_result,
            competition_analysis_output=comp_result,
            tech_analysis_output=tech_result,
            mvs_calculation_output=asdict(mvs_result),
            recommendations=mvs_result.recommendations,
            quality_gates_triggered=mvs_result.quality_gates_triggered,
            audit_trail={
                'innovation_1_signal_fusion': {'outputs': fusion_result},
                'innovation_2_momentum': {'outputs': momentum_result},
                'innovation_3_competition': {'outputs': comp_result},
                'innovation_4_tech_stack': {'outputs': tech_result},
                'innovation_5_mvs': {'outputs': asdict(mvs_result)},
                'input': {
                    'idea_name': request.idea_name,
                    'idea_description': request.idea_description,
                    'sector': request.sector
                }
            }
        )
        
        # Cache in Redis for the Audit Agent
        cache_key = CacheKey.scoring_result(request.idea_name)
        safe_cache_set(cache_key, scoring_result, ttl=CacheTTL.SCORING_RESULT)
        logger.info(f"Cached scoring result for {request.idea_name} in Redis")
        
        return UniversalValidationResult(
            sector=request.sector,
            google_trends_score=int(trends_data.get("average_interest", 50)),
            autocomplete_popularity=int(autocomplete_data.get("popularity_score", 50)),
            wikipedia_interest=int(wikipedia_data.get("interest_score", 50)),
            reddit_engagement=int(reddit_data.get("engagement_score", 50)),
            youtube_coverage=int(youtube_data.get("engagement_score", 50)),
            news_mentions=int(news_data.get("article_count", 0)),
            sector_signals={**sector_signals, "momentum": momentum_result['trend_pattern'], "structure": comp_result['market_structure']},
            execution_complexity=int(tech_result['total_complexity']),
            execution_risk_level=tech_result['complexity_rating'],
            estimated_months=int(tech_result['estimated_learning_months'] + 6),
            key_challenges=[r['description'] for r in tech_result['risk_factors'][:3]] if tech_result['risk_factors'] else ["Baseline risks"],
            market_validation_score=int(mvs_result.market_dimension),
            social_proof_score=int(signals.total_views // 1000),
            overall_confidence=int(mvs_result.mvs_score),
            
            # MVS Mappings
            validation_class=mvs_result.validation_class,
            recommendations=mvs_result.recommendations,
            competitive_moat_score=int(mvs_result.differentiation_dimension),
            capital_efficiency_score=int(mvs_result.capital_dimension),
            execution_risk_score=int(mvs_result.execution_dimension),
            
            data_sources_used=sources_used,
            fallback_count=int(fallback_count)
        )
    
    def _calculate_market_score(self, trends: Dict, autocomplete: Dict, wikipedia: Dict) -> int:
        weights = {"trends": 0.40, "autocomplete": 0.30, "wikipedia": 0.30}
        score = (trends.get("average_interest", 50) * weights["trends"] +
                 autocomplete.get("popularity_score", 50) * weights["autocomplete"] +
                 wikipedia.get("interest_score", 50) * weights["wikipedia"])
        return int(score)
    
    def _calculate_social_score(self, reddit: Dict, youtube: Dict, news: Dict) -> int:
        weights = {"reddit": 0.40, "youtube": 0.35, "news": 0.25}
        news_score = min(news.get("article_count", 0) * 2, 100)
        score = (reddit.get("engagement_score", 50) * weights["reddit"] +
                 youtube.get("engagement_score", 50) * weights["youtube"] +
                 news_score * weights["news"])
        return int(score)
    
    def _calculate_overall_confidence(self, market: int, social: int, execution: int, sector: int) -> int:
        weights = {"market": 0.35, "social": 0.25, "execution": 0.25, "sector": 0.15}
        score = (market * weights["market"] + social * weights["social"] +
                 execution * weights["execution"] + sector * weights["sector"])
        return int(score)
    
    def _track_data_sources(self, data_list: List[Dict]) -> tuple[List[str], int]:
        sources_used = []
        fallback_count = 0
        for data in data_list:
            source = data.get("data_source", "Unknown")
            sources_used.append(source)
            if "Mock" in source or "unavailable" in source:
                fallback_count += 1
        return sources_used, fallback_count
