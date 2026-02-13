from typing import List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.comparison_schemas import (
    ComparisonRequest, 
    ComparisonResponse, 
    SimilarCompany,
    CompanyOutcome
)
from .keyword_extractor import KeywordExtractor
from .company_searcher import ProductHuntSearcher
from .outcome_classifier import OutcomeClassifier
from .similarity_ranker import SimilarityRanker

class ComparisonEngine:
    """Orchestrator for the Smart Comparison Search feature"""
    
    def __init__(self):
        self.keyword_extractor = KeywordExtractor()
        self.ph_searcher = ProductHuntSearcher()
        self.classifier = OutcomeClassifier()
        self.ranker = SimilarityRanker()
    
    async def find_similar_companies(
        self, 
        request: ComparisonRequest
    ) -> ComparisonResponse:
        """
        Main orchestration logic:
        1. Extract keywords
        2. Search external sources
        3. Classify outcomes
        4. Rank by similarity
        5. Return results
        """
        
        # 1. Extract keywords (LLM)
        keywords = self.keyword_extractor.extract_keywords(
            request.idea_description,
            request.target_market
        )
        
        # 2. Search Product Hunt (External API)
        ph_results = self.ph_searcher.search_companies(keywords, limit=20)
        
        # 3. Classify and transform to domain model
        raw_companies = []
        for raw in ph_results:
            # Create the company object
            company = SimilarCompany(
                name=raw["name"],
                description=raw.get("description", ""),
                business_model="Startup",  # Simple default
                outcome=CompanyOutcome.UNKNOWN, # To be filled
                key_lesson="", # To be filled
                url=raw.get("url"),
                data_sources=["producthunt"]
            )
            
            # Use LLM to classify outcome and generate lesson
            outcome, lesson = self.classifier.classify_outcome(raw)
            company.outcome = outcome
            company.key_lesson = lesson
            
            # Extract founded year if possible (from launch date)
            launch_date = raw.get("metadata", {}).get("launch_date")
            if launch_date:
                try:
                    company.founded_year = int(launch_date[:4])
                except:
                    pass
            
            raw_companies.append(company)
        
        # 4. Rank by similarity (Embeddings)
        ranked_companies = self.ranker.rank_companies(
            raw_companies,
            request.idea_description,
            request.target_market
        )
        
        # 5. Build response
        # In a real scenario, we might want to enrich with Crunchbase here if available
        # or add more data sources.
        
        return ComparisonResponse(
            similar_companies=ranked_companies[:5],
            search_keywords=keywords,
            total_found=len(raw_companies),
            data_quality_score=self._calculate_data_quality(ranked_companies[:5])
        )
    
    def _calculate_data_quality(self, companies: List[SimilarCompany]) -> float:
        """Heuristic for how complete the returned data is"""
        if not companies:
            return 0.0
            
        points = 0
        total_possible = len(companies) * 4
        
        for c in companies:
            if c.url: points += 1
            if c.founded_year: points += 1
            if c.funding_raised_usd: points += 1
            if c.outcome != "unknown": points += 1
            
        return (points / total_possible) * 100 if total_possible > 0 else 0
