"""
Grounded Idea Generator Service
Uses validation-in-the-loop to ensure all generated ideas pass 7-layer deterministic validation.
"""

import os
import json
import uuid
import httpx
import logging
import asyncio
from typing import List, Dict, Any, Optional
from models.schemas import (
    WizardInput, 
    StartupIdea, 
    MVPFeature, 
    BusinessModelSnippet,
    IdeaGenerationResponse
)

logger = logging.getLogger(__name__)

class GroundedIdeaGeneratorService:
    """
    Pro-level idea generator with validation-in-the-loop.
    Generates ideas → Validates immediately → Returns only validated ideas.
    """
    
    # Validation thresholds
    MVS_SCORE_MIN = 50  # Minimum MVS score (Grade C)
    MONTHS_TO_PROFITABILITY_MAX = 24  # Maximum months to profitability
    EXECUTION_SCORE_MIN = 60  # Minimum execution score
    MARKET_GROWTH_MIN = 0.0  # Minimum market growth rate
    
    def __init__(
        self,
        client: Any,
        universal_validator,
        v2_scorer,
        tech_feasibility,
        economics_simulator,
        traffic_estimator,
        comparison_engine,
        strategic_agent,
        trends_service,
        model: str = "gpt-4-turbo-preview"
    ):
        self.client = client
        self.model = model
        
        # Deterministic validators
        self.validator = universal_validator
        self.scorer = v2_scorer
        self.tech = tech_feasibility
        self.economics = economics_simulator
        self.traffic = traffic_estimator
        self.comparison = comparison_engine
        self.agent = strategic_agent
        self.trends = trends_service
    
    async def generate_validated_ideas(
        self, 
        wizard_input: WizardInput, 
        num_ideas: int = 5,
        contrarian_override: bool = False
    ) -> IdeaGenerationResponse:
        """
        Generate ideas with validation-in-the-loop.
        Only returns ideas that pass ALL 7 validators.
        """
        
        # STAGE 1: Extract Constraints (Deterministic)
        constraints = self._extract_constraints(wizard_input)
        
        # STAGE 2: Market Opportunity Discovery (Real Data)
        market_opportunities = await self._discover_market_opportunities(
            industry=wizard_input.industry,
            constraints=constraints
        )
        
        # STAGE 3: Competitive Gap Analysis (Real Data)
        competitive_gaps = await self._analyze_competitive_gaps(
            industry=wizard_input.industry,
            opportunities=market_opportunities
        )
        
        # STAGE 4-6: Iterative Generation + Validation
        validated_ideas = []
        iteration = 0
        max_iterations = 5
        total_generated = 0
        
        while len(validated_ideas) < num_ideas and iteration < max_iterations:
            iteration += 1
            
            # Generate 3 ideas with constraints
            raw_ideas = await self._generate_constrained_ideas(
                wizard_input=wizard_input,
                constraints=constraints,
                opportunities=market_opportunities,
                gaps=competitive_gaps,
                count=3,
                contrarian_override=contrarian_override
            )
            
            total_generated += len(raw_ideas)
            
            # Validate each idea in real-time
            for idea in raw_ideas:
                validation_result = await self._validate_idea_full_stack(idea, wizard_input)
                
                if validation_result["passed_all_layers"]:
                    idea.validation_report = validation_result
                    idea.composite_score = validation_result["composite_score"]
                    validated_ideas.append(idea)
                    
                    if len(validated_ideas) >= num_ideas:
                        break
        
        # STAGE 7: Ranking & Presentation
        validated_ideas.sort(key=lambda x: x.composite_score, reverse=True)
        
        validation_rate = (len(validated_ideas) / total_generated * 100) if total_generated > 0 else 0
        
        return IdeaGenerationResponse(
            ideas=validated_ideas[:num_ideas],
            generation_id=str(uuid.uuid4()),
            input_summary=f"Industry: {wizard_input.industry}, Validated: {len(validated_ideas)}/{total_generated} ({validation_rate:.1f}%)",
            metadata={
                "iterations": iteration,
                "total_generated": total_generated,
                "validation_rate": validation_rate,
                "constraints_applied": constraints,
                "market_opportunities_found": len(market_opportunities),
                "competitive_gaps_found": len(competitive_gaps)
            }
        )
    
    def _extract_constraints(self, wizard_input: WizardInput) -> Dict[str, Any]:
        """Extract hard constraints from user input (Deterministic)"""
        return {
            "budget_max": wizard_input.budget,
            "budget_min": wizard_input.budget * 0.5,
            "skills_required": wizard_input.skills,
            "industry": wizard_input.industry,
            "target_audience": wizard_input.target_audience,
            "mvs_score_min": self.MVS_SCORE_MIN,
            "months_to_profitability_max": self.MONTHS_TO_PROFITABILITY_MAX,
            "execution_score_min": self.EXECUTION_SCORE_MIN,
            "market_growth_min": self.MARKET_GROWTH_MIN
        }
    
    async def _discover_market_opportunities(
        self, 
        industry: str, 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Discover real market opportunities using Google Trends.
        Returns only GROWING markets.
        """
        opportunities = []
        
        # Get trending topics in industry
        industry_keywords = self._get_industry_keywords(industry)
        
        for keyword in industry_keywords:
            try:
                trend_data = await self.trends.get_interest_over_time(keyword)
                
                # Only include if growing
                if trend_data.get("trend") == "Rising" and trend_data.get("growth_rate", 0) > 0:
                    opportunities.append({
                        "keyword": keyword,
                        "interest_score": trend_data.get("average_interest", 0),
                        "growth_rate": trend_data.get("growth_rate", 0),
                        "trend": "Rising"
                    })
            except Exception as e:
                logger.error(f"Error fetching trends for {keyword}: {e}")
                continue
        
        # Sort by growth rate
        opportunities.sort(key=lambda x: x["growth_rate"], reverse=True)
        
        return opportunities[:10]  # Top 10 opportunities
    
    async def _analyze_competitive_gaps(
        self, 
        industry: str, 
        opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find competitive gaps by analyzing similar companies.
        Returns underserved niches.
        """
        gaps = []
        
        for opp in opportunities[:5]:  # Analyze top 5 opportunities
            try:
                # Find similar companies
                comparison_result = await self.comparison.find_similar(opp["keyword"])
                
                # Robust access
                if isinstance(comparison_result, dict):
                    companies = comparison_result.get('similar_companies', [])
                else:
                     companies = getattr(comparison_result, 'similar_companies', [])
                
                def get_outcome(c):
                    return c.get('outcome') if isinstance(c, dict) else getattr(c, 'outcome', None)
                
                # Analyze outcomes
                acquired = [c for c in companies if get_outcome(c) == "acquired"]
                failed = [c for c in companies if get_outcome(c) == "failed"]
                growing = [c for c in companies if get_outcome(c) == "growing"]
                
                # Gap exists if: successful exits + few competitors
                if len(acquired) > 0 and len(growing) < 5:
                    gaps.append({
                        "opportunity": opp["keyword"],
                        "successful_exits": len(acquired),
                        "current_competitors": len(growing),
                        "gap_score": len(acquired) / max(len(growing), 1),
                        "lessons_from_failures": [f.name for f in failed[:3]],
                        "proof": f"{len(acquired)} successful exits, {len(growing)} active competitors"
                    })
            except Exception as e:
                logger.error(f"Error analyzing gaps for {opp['keyword']}: {e}")
                continue
        
        return gaps
    
    async def _generate_constrained_ideas(
        self,
        wizard_input: WizardInput,
        constraints: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        gaps: List[Dict[str, Any]],
        count: int,
        contrarian_override: bool
    ) -> List[StartupIdea]:
        """
        LLM generates ideas WITH constraints.
        Uses real market data as input.
        """
        
        prompt = f"""
        Generate {count} startup ideas with the following HARD CONSTRAINTS:
        
        BUDGET CONSTRAINT:
        - Maximum initial cost: ${constraints['budget_max']:,}
        - Minimum initial cost: ${constraints['budget_min']:,}
        
        SKILL CONSTRAINT:
        - Required skills: {', '.join(constraints['skills_required'])}
        - Team must have these skills
        
        MARKET CONSTRAINT:
        - Industry: {constraints['industry']}
        - Target audience: {constraints['target_audience']}
        - Market MUST be growing (not declining)
        
        REAL MARKET OPPORTUNITIES (Use these, don't invent):
        {json.dumps(opportunities[:5], indent=2)}
        
        COMPETITIVE GAPS (Focus here):
        {json.dumps(gaps[:3], indent=2)}
        
        RULES:
        1. Each idea MUST address one of the opportunities above
        2. Each idea MUST fit within budget constraints
        3. Each idea MUST be buildable with required skills
        4. DO NOT invent market data - use the opportunities provided
        5. Learn from failed companies listed in gaps
        
        Return a JSON object with this structure:
        {{
            "ideas": [
                {{
                    "name": "Idea Name",
                    "tagline": "One-line pitch",
                    "description": "Detailed description",
                    "target_market": "Specific target market",
                    "estimated_initial_cost": 50000,
                    "mvp_features": [
                        {{"name": "Feature 1", "description": "Description", "priority": "high"}},
                        {{"name": "Feature 2", "description": "Description", "priority": "medium"}}
                    ],
                    "business_model": {{
                        "revenue_streams": ["Stream 1", "Stream 2"],
                        "pricing_strategy": "Pricing approach"
                    }}
                }}
            ]
        }}
        """
        
    async def _generate_constrained_ideas(
        self, 
        wizard_input: WizardInput,
        constraints: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        gaps: List[Dict[str, Any]],
        count: int = 3
    ) -> List[StartupIdea]:
        """Generate ideas adhering to constraints using injected client"""
        
        prompt = self._construct_generation_prompt(
            wizard_input, constraints, opportunities, gaps, count
        )
        
        if not self.client:
            return self._generate_stub_ideas(wizard_input, count)
            
        try:
            # Use asyncio.to_thread for blocking client call
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a startup advisor who generates ideas based on REAL market data and constraints."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.9 if constraints.get('contrarian_override') else 0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            ideas_data = json.loads(content)
            
            return self._parse_ideas(ideas_data, wizard_input.industry)
                
        except Exception as e:
            logger.error(f"Error generating constrained ideas: {e}")
            return self._generate_stub_ideas(wizard_input, count)
            
    def _parse_ideas(self, data: dict, industry: str) -> List[StartupIdea]:
        """Parse JSON response into StartupIdea objects"""
        ideas = []
        for idea_data in data.get("ideas", []):
            try:
                idea = StartupIdea(
                    id=str(uuid.uuid4()),
                    name=idea_data.get("name", "Unnamed Idea"),
                    tagline=idea_data.get("tagline", ""),
                    description=idea_data.get("description", ""),
                    industry=industry,
                    target_market=idea_data.get("target_market", ""),
                    estimated_initial_cost=idea_data.get("estimated_initial_cost", 0),
                    mvp_features=[
                        MVPFeature(**f) for f in idea_data.get("mvp_features", [])
                    ],
                    business_model=BusinessModelSnippet(**idea_data.get("business_model", {}))
                )
                ideas.append(idea)
            except Exception as e:
                logger.error(f"Error parsing idea: {e}")
                continue
        
        return ideas
    
    def _generate_stub_ideas(self, wizard_input: WizardInput, num_ideas: int) -> List[StartupIdea]:
        """Generate stub ideas when API is unavailable"""
        return [
            StartupIdea(
                id=str(uuid.uuid4()),
                name=f"Stub Idea {i+1}",
                tagline="API unavailable - stub idea",
                description=f"Stub idea for {wizard_input.industry}",
                industry=wizard_input.industry,
                target_market=wizard_input.target_audience,
                estimated_initial_cost=wizard_input.budget,
                mvp_features=[],
                business_model=BusinessModelSnippet(
                    revenue_streams=["Subscription"],
                    key_partners=["Cloud Providers"],
                    cost_structure=["Hosting", "Development"],
                    value_proposition=f"Automated solution for {wizard_input.industry}",
                    customer_segments=[wizard_input.target_audience],
                    channels=["Online Ads"]
                )
            )
            for i in range(num_ideas)
        ]
