"""
Strategic Audit Agent - LLM Explanatory Layer

Uses GPT-4o as an agent with deterministic tools to provide
professional, VC-level strategic explanations grounded in the
deterministic audit trail.

Architecture:
- LLM acts as Strategic Auditor
- Tools query the deterministic audit trail
- Professional system prompt enforces TAM/SAM/SOM, HHI, strategic frameworks
- NO LLM in computation, only in explanation

Following fastapi-pro and python-pro best practices:
- Async-first design
- Type safety with Pydantic
- Structured logging
- Error handling
- Clean dependency injection
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
import json
from datetime import datetime

from pydantic import BaseModel, Field

# Import OpenAI helper
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openai_helper import get_openai_client, get_model_name
from services.idea_scorer_v2.engine import ScoringResult


# ==================== Pydantic Models ====================

class AuditQuery(BaseModel):
    """User question about a scoring result"""
    question: str = Field(..., description="User's question about the score")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ExplanationResponse(BaseModel):
    """Strategic explanation response"""
    answer: str = Field(..., description="Professional strategic answer")
    tools_used: List[str] = Field(default_factory=list, description="Tools called by agent")
    data_cited: List[Dict[str, Any]] = Field(default_factory=list, description="Deterministic data points cited")
    confidence: str = Field(..., description="Confidence level (HIGH|MEDIUM|LOW)")


# ==================== Tool Definitions ====================

@dataclass
class Tool:
    """Tool definition for LLM agent"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


class StrategicTools:
    """Deterministic tools for strategic analysis"""
    
    def __init__(self, scoring_result: ScoringResult):
        """Initialize with scoring result audit trail"""
        self.result = scoring_result
        self.audit = scoring_result.audit_trail
    
    def get_market_segments(self, industry: str = "default") -> Dict[str, Any]:
        """
        Get TAM/SAM/SOM equivalent from market signals.
        
        Returns market size breakdown in VC-friendly terms.
        
        Args:
            industry: Industry type (saas, ecommerce, consumer_app, marketplace, default)
        """
        # Import here to avoid circular dependencies
        from utils.config_loader import get_industry_assumptions
        
        signal_output = self.result.signal_fusion_output
        
        # Calculate implied market size from search volume
        monthly_searches = signal_output['breakdown']['google_trends_volume']['raw']
        
        # Get industry-specific assumptions
        assumptions = get_industry_assumptions(industry)
        conversion_rate = assumptions.get("conversion_rate", 0.10)
        arpu_annual = assumptions.get("arpu_annual", 50)
        
        # TAM calculation
        implied_users = monthly_searches * 12 * conversion_rate  # Annual addressable users
        tam = implied_users * arpu_annual
        
        # SAM (serviceable) - assume we can reach 30%
        sam = tam * 0.30
        
        # SOM (obtainable) - conservative 5% market share in year 3
        som_year3 = sam * 0.05
        
        return {
            "tam_usd": int(tam),
            "sam_usd": int(sam),
            "som_year3_usd": int(som_year3),
            "monthly_search_volume": monthly_searches,
            "industry": industry,
            "calculation_basis": f"{conversion_rate*100:.1f}% conversion rate * ${arpu_annual} ARPU * 12 months",

            "assumptions": [
                "10% of searchers convert to users",
                "Average revenue per user: $50/year",
                "Market penetration: 30% (SAM)",
                "Realistic market share: 5% by year 3 (SOM)"
            ]
        }
    
    def get_competitive_moat(self) -> Dict[str, Any]:
        """
        Get competitive moat analysis using HHI and entry barriers.
        
        Returns competitive positioning in strategic terms.
        """
        comp_output = self.result.competition_analysis_output
        
        return {
            "hhi_index": comp_output['hhi_index'],
            "market_structure": comp_output['market_structure'],
            "entry_difficulty": comp_output['entry_difficulty'],
            "saturation_level": comp_output['saturation_level'],
            "competition_score": comp_output['competition_score'],
            "strategic_insight": comp_output['strategic_insight'],
            "interpretation": self._interpret_moat(
                comp_output['hhi_index'],
                comp_output['market_structure'],
                comp_output['competition_score']
            )
        }
    
    def get_momentum_vector(self) -> Dict[str, Any]:
        """
        Get market momentum analysis (growth trajectory).
        
        Returns trend data in strategic terms.
        """
        momentum_output = self.result.momentum_analysis_output
        
        return {
            "trend_pattern": momentum_output['trend_pattern'],
            "momentum_score": momentum_output['momentum_score'],
            "weighted_slope": momentum_output['weighted_slope'],
            "slope_percentage": f"{momentum_output['weighted_slope']*100:+.1f}%",
            "volatility": momentum_output['volatility'],
            "interpretation": momentum_output['interpretation'],
            "breakdown": momentum_output['breakdown']
        }
    
    def get_execution_risk(self) -> Dict[str, Any]:
        """
        Get technical execution risk from tech stack analysis.
        
        Returns feasibility assessment in strategic terms.
        """
        tech_output = self.result.tech_analysis_output
        
        return {
            "execution_score": tech_output['execution_score'],
            "complexity_rating": tech_output['complexity_rating'],
            "total_complexity": tech_output['total_complexity'],
            "learning_months": tech_output['estimated_learning_months'],
            "team_readiness": tech_output['team_readiness_score'],
            "risk_factors": tech_output['risk_factors'],
            "technologies": [
                {
                    "name": t['name'],
                    "complexity": t['complexity'],
                    "team_experience": t['team_experience']
                }
                for t in tech_output['technologies']
            ]
        }
    
    def explain_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Explain a specific rule or threshold used in scoring.
        
        Args:
            rule_name: Name of rule (e.g., "MODERATE_DEMAND", "HHI_INDEX")
        
        Returns detailed rule explanation.
        """
        from utils.rule_engine import rule_engine
        
        explanation = rule_engine.explain_rule(rule_name)
        
        return {
            "rule_name": rule_name,
            "explanation": explanation,
            "deterministic": True
        }
    
    def compare_scenarios(self, dimension: str, new_value: float) -> Dict[str, Any]:
        """
        Simulate "what-if" scenario by changing a dimension.
        
        Args:
            dimension: Dimension to change (market|differentiation|execution|capital)
            new_value: New score value (0-100)
        
        Returns impact analysis.
        """
        current_scores = {
            "market": self.result.market_dimension,
            "differentiation": self.result.differentiation_dimension,
            "execution": self.result.execution_dimension,
            "capital": self.result.capital_dimension
        }
        
        if dimension not in current_scores:
            return {"error": f"Invalid dimension: {dimension}"}
        
        # Calculate new MVS
        scores_copy = current_scores.copy()
        scores_copy[dimension] = new_value
        
        new_mvs = (
            0.35 * scores_copy["market"] +
            0.30 * scores_copy["differentiation"] +
            0.20 * scores_copy["execution"] +
            0.15 * scores_copy["capital"]
        )
        
        delta = new_mvs - self.result.mvs_score
        
        # Calculate percentage change safely (avoid division by zero)
        if self.result.mvs_score > 0:
            delta_percentage = f"{(delta / self.result.mvs_score * 100):+.1f}%"
        else:
            delta_percentage = "N/A (current score is 0)"
        
        return {
            "scenario": f"If {dimension} changes from {current_scores[dimension]} to {new_value}",
            "current_mvs": self.result.mvs_score,
            "new_mvs": int(new_mvs),
            "delta": round(delta, 1),
            "delta_percentage": delta_percentage,
            "impact_level": "HIGH" if abs(delta) > 10 else "MODERATE" if abs(delta) > 5 else "LOW"
        }
    
    def recommend_improvements(self) -> List[Dict[str, Any]]:
        """
        Get prioritized improvement recommendations.
        
        Returns list of actionable recommendations.
        """
        return [
            {
                "recommendation": rec,
                "priority": self._assess_priority(rec)
            }
            for rec in self.result.recommendations[:5]  # Top 5
        ]
    
    def _interpret_moat(self, hhi: int, structure: str, score: int) -> str:
        """Generate strategic interpretation of competitive moat"""
        if score >= 70:
            return f"{structure} market (HHI: {hhi}). Favorable for new entrants with differentiation."
        elif score >= 50:
            return f"{structure} market (HHI: {hhi}). Moderate competition requires strong positioning."
        else:
            return f"{structure} market (HHI: {hhi}). Highly competitive - strong moat essential."
    
    def _assess_priority(self, recommendation: str) -> str:
        """Assess priority from recommendation text"""
        if "🚨 SHOWSTOPPER" in recommendation:
            return "CRITICAL"
        elif "⚠️" in recommendation:
            return "HIGH"
        elif "💡" in recommendation:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_all_tools_schema(self) -> List[Dict[str, Any]]:
        """Get OpenAI function calling schema for all tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_market_segments",
                    "description": "Get TAM/SAM/SOM market size breakdown for strategic analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_competitive_moat",
                    "description": "Get competitive moat analysis including HHI index and entry barriers",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_momentum_vector",
                    "description": "Get market momentum and growth trajectory analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_execution_risk",
                    "description": "Get technical execution risk and feasibility assessment",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "explain_rule",
                    "description": "Explain a specific scoring rule or threshold",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "rule_name": {
                                "type": "string",
                                "description": "Name of the rule to explain (e.g., 'MODERATE_DEMAND', 'HHI_INDEX')"
                            }
                        },
                        "required": ["rule_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_scenarios",
                    "description": "Simulate 'what-if' scenario by changing a dimension score",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dimension": {
                                "type": "string",
                                "enum": ["market", "differentiation", "execution", "capital"],
                                "description": "Dimension to change"
                            },
                            "new_value": {
                                "type": "number",
                                "description": "New score value (0-100)"
                            }
                        },
                        "required": ["dimension", "new_value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "recommend_improvements",
                    "description": "Get prioritized improvement recommendations",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name"""
        tool_methods = {
            "get_market_segments": self.get_market_segments,
            "get_competitive_moat": self.get_competitive_moat,
            "get_momentum_vector": self.get_momentum_vector,
            "get_execution_risk": self.get_execution_risk,
            "explain_rule": self.explain_rule,
            "compare_scenarios": self.compare_scenarios,
            "recommend_improvements": self.recommend_improvements
        }
        
        method = tool_methods.get(tool_name)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return method(**arguments)


# ==================== Strategic Audit Agent ====================

class StrategicAuditAgent:
    """
    LLM agent that provides strategic explanations using deterministic tools.
    
    Following fastapi-pro best practices:
    - Async-first design
    - Proper error handling
    - Type safety
    """
    
    # Configuration constants
    MAX_TOOL_ITERATIONS = 5  # Prevent runaway loops
    MODEL_NAME = "gpt-4o"
    MODEL_TEMPERATURE = 0.3  # Low for consistency
    
    # Professional system prompt
    SYSTEM_PROMPT = """You are a Senior Venture Capital Analyst and Strategic Auditor.

Your goal is to explain IdeaLab scoring results with extreme clarity and strategic depth.

RULES:
1. NEVER guess. Always use tools to fetch deterministic results.
2. Use professional terminology (TAM/SAM/SOM, CAGR, HHI Index, Moats).
3. Be forceful and direct. Avoid generic AI filler ("I hope this helps").
4. Every numerical score MUST be justified by a specific data point from tools.
5. Focus on the 'So What?' — what does this number mean for the founder?
6. Structure answers as:
   - Executive Summary (1-2 sentences)
   - Strategic Foundation (data-backed reasoning)
   - Gap Analysis (why not higher/lower?)
   - Actionable Roadmap (3 specific moves)

OUTPUT STYLE:
- Use markdown formatting
- Bold key metrics
- Use bullet points for clarity
- Cite specific data points with numbers
- End with concrete next steps

Remember: You are NOT a chatbot. You are a strategic auditor justifying every word with deterministic data."""
    
    def __init__(self, client: Optional[Any] = None):
        """Initialize agent with OpenAI client (or use default)"""
        self.client = client or get_openai_client()
        if not self.client:
            raise RuntimeError("OpenAI client not available. Check environment variables.")
    
    async def explain(
        self,
        scoring_result: ScoringResult,
        query: AuditQuery
    ) -> ExplanationResponse:
        """
        Generate strategic explanation for a user question.
        
        Args:
            scoring_result: Complete scoring result with audit trail
            query: User's question
        
        Returns:
            Professional strategic explanation
        """
        # Initialize tools
        tools = StrategicTools(scoring_result)
        tools_schema = tools.get_all_tools_schema()
        
        # Build initial message
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Idea: {scoring_result.idea_name}
MVS Score: {scoring_result.mvs_score}/100 (Grade: {scoring_result.mvs_grade})
Classification: {scoring_result.validation_class}

User Question: {query.question}

Use the available tools to answer this question with strategic depth. Cite specific data points."""
            }
        ]
        
        # Agentic loop (prevent runaway)
        tools_used = []
        data_cited = []
        
        for _ in range(self.MAX_TOOL_ITERATIONS):
            # Call LLM
            response = self.client.chat.completions.create(
                model=get_model_name(),
                messages=messages,
                tools=tools_schema,
                tool_choice="auto",
                temperature=self.MODEL_TEMPERATURE
            )
            
            message = response.choices[0].message
            
            # Check if done
            if not message.tool_calls:
                # Final answer
                return ExplanationResponse(
                    answer=message.content,
                    tools_used=tools_used,
                    data_cited=data_cited,
                    confidence="HIGH" if len(tools_used) >= 2 else "MEDIUM"
                )
            
            # Execute tool calls
            messages.append(message)
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Call tool
                result = tools.call_tool(tool_name, arguments)
                
                # Track usage
                tools_used.append(tool_name)
                data_cited.append({
                    "tool": tool_name,
                    "data": result
                })
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, indent=2)
                })
        
        # Max iterations reached - return partial answer
        return ExplanationResponse(
            answer="Analysis incomplete - maximum tool calls reached. Please refine your question.",
            tools_used=tools_used,
            data_cited=data_cited,
            confidence="LOW"
        )
