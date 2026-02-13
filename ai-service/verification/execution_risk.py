"""
Execution Risk Analyzer
Deterministic complexity and feasibility assessment
"""

import logging
from typing import Dict, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExecutionRiskInput(BaseModel):
    """Input for execution risk analysis"""
    idea_name: str
    idea_description: str
    tech_stack: List[str] = []
    team_size: int = 1
    timeline_months: int = 6
    budget_usd: float = 0


class ExecutionRiskAnalysis(BaseModel):
    """Execution risk analysis result"""
    complexity_score: int  # 0-100 (higher = more complex)
    resource_requirements: Dict[str, str]
    risk_level: str  # Low, Medium, High, Very High
    key_challenges: List[str]
    estimated_months: int
    confidence: int  # 0-100


class ExecutionRiskAnalyzer:
    """
    Deterministic execution risk assessment
    NO AI hallucination - only rule-based logic
    """
    
    # Complexity multipliers (deterministic)
    TECH_COMPLEXITY = {
        # Low complexity (1-2x)
        "html": 1,
        "css": 1,
        "javascript": 1.5,
        "python": 1.5,
        "node.js": 1.5,
        
        # Medium complexity (2-3x)
        "react": 2,
        "vue": 2,
        "nextjs": 2.5,
        "fastapi": 2,
        "django": 2.5,
        "postgresql": 2,
        
        # High complexity (3-5x)
        "machine learning": 4,
        "blockchain": 5,
        "ar/vr": 5,
        "iot": 4,
        "real-time video": 4.5,
        "kubernetes": 4,
        
        # Very high complexity (5-10x)
        "quantum computing": 10,
        "biotech": 9,
        "robotics": 8,
        "autonomous vehicles": 9,
        "advanced ai": 8
    }
    
    def analyze(self, input_data: ExecutionRiskInput) -> ExecutionRiskAnalysis:
        """
        Analyze execution risk deterministically
        Same inputs → Same outputs
        """
        
        # 1. Calculate technical complexity
        tech_complexity = self._calculate_tech_complexity(input_data.tech_stack)
        
        # 2. Assess team capacity
        team_factor = self._calculate_team_factor(input_data.team_size)
        
        # 3. Evaluate timeline realism
        timeline_risk = self._evaluate_timeline(tech_complexity, input_data.timeline_months, input_data.team_size)
        
        # 4. Check budget constraints
        budget_risk = self._evaluate_budget(tech_complexity, input_data.budget_usd, input_data.team_size)
        
        # 5. Aggregate complexity score (0-100)
        complexity_score = min(int(tech_complexity * 10), 100)
        
        # 6. Determine risk level
        risk_level = self._determine_risk_level(complexity_score, timeline_risk, budget_risk)
        
        # 7. Identify key challenges
        key_challenges = self._identify_challenges(input_data, tech_complexity, timeline_risk, budget_risk)
        
        # 8. Estimate realistic timeline
        estimated_months = self._estimate_timeline(tech_complexity, input_data.team_size)
        
        # 9. Calculate confidence
        confidence = self._calculate_confidence(timeline_risk, budget_risk, input_data.team_size)
        
        logger.info(f"Execution risk for '{input_data.idea_name}': {risk_level} ({complexity_score}/100)")
        
        return ExecutionRiskAnalysis(
            complexity_score=complexity_score,
            resource_requirements={
                "recommended_team_size": str(max(input_data.team_size, self._min_team_size(tech_complexity))),
                "recommended_budget_usd": str(self._min_budget(tech_complexity, input_data.team_size)),
                "recommended_timeline_months": str(estimated_months)
            },
            risk_level=risk_level,
            key_challenges=key_challenges,
            estimated_months=estimated_months,
            confidence=confidence
        )
    
    def _calculate_tech_complexity(self, tech_stack: List[str]) -> float:
        """
        Calculate technical complexity multiplier
        Based on technologies mentioned
        """
        if not tech_stack:
            return 2.0  # Default medium complexity
        
        total_complexity = 0
        for tech in tech_stack:
            tech_lower = tech.lower()
            
            # Find matching complexity
            for key, value in self.TECH_COMPLEXITY.items():
                if key in tech_lower:
                    total_complexity += value
                    break
            else:
                total_complexity += 2  # Unknown tech = medium complexity
        
        # Average complexity
        return total_complexity / len(tech_stack) if tech_stack else 2.0
    
    def _calculate_team_factor(self, team_size: int) -> float:
        """Team capacity factor"""
        if team_size >= 5:
            return 1.0  # Full team
        elif team_size >= 3:
            return 1.5  # Small team
        elif team_size >= 2:
            return 2.0  # Couple
        else:
            return 3.0  # Solo founder
    
    def _evaluate_timeline(self, complexity: float, months: int, team_size: int) -> str:
        """Evaluate timeline realism"""
        min_months = self._estimate_timeline(complexity, team_size)
        
        if months >= min_months * 1.5:
            return "Conservative"
        elif months >= min_months:
            return "Realistic"
        elif months >= min_months * 0.7:
            return "Optimistic"
        else:
            return "Unrealistic"
    
    def _evaluate_budget(self, complexity: float, budget: float, team_size: int) -> str:
        """Evaluate budget adequacy"""
        min_budget = self._min_budget(complexity, team_size)
        
        if budget >= min_budget * 2:
            return "Well-funded"
        elif budget >= min_budget:
            return "Adequate"
        elif budget >= min_budget * 0.5:
            return "Tight"
        else:
            return "Insufficient"
    
    def _determine_risk_level(self, complexity: int, timeline_risk: str, budget_risk: str) -> str:
        """Determine overall risk level"""
        risk_points = 0
        
        # Complexity risk
        if complexity >= 80:
            risk_points += 3
        elif complexity >= 60:
            risk_points += 2
        elif complexity >= 40:
            risk_points += 1
        
        # Timeline risk
        if timeline_risk == "Unrealistic":
            risk_points += 3
        elif timeline_risk == "Optimistic":
            risk_points += 2
        elif timeline_risk == "Realistic":
            risk_points += 1
        
        # Budget risk
        if budget_risk == "Insufficient":
            risk_points += 3
        elif budget_risk == "Tight":
            risk_points += 2
        elif budget_risk == "Adequate":
            risk_points += 1
        
        # Map to risk level
        if risk_points >= 7:
            return "Very High"
        elif risk_points >= 5:
            return "High"
        elif risk_points >= 3:
            return "Medium"
        else:
            return "Low"
    
    def _identify_challenges(self, input_data: ExecutionRiskInput, complexity: float, timeline_risk: str, budget_risk: str) -> List[str]:
        """Identify key execution challenges"""
        challenges = []
        
        if complexity >= 5:
            challenges.append("High technical complexity requires specialized expertise")
        
        if input_data.team_size == 1:
            challenges.append("Solo founder - risk of burnout and skill gaps")
        
        if timeline_risk in ["Optimistic", "Unrealistic"]:
            challenges.append(f"Timeline ({input_data.timeline_months} months) may be too aggressive")
        
        if budget_risk in ["Tight", "Insufficient"]:
            challenges.append("Budget constraints may limit development velocity")
        
        if not input_data.tech_stack:
            challenges.append("No tech stack specified - need to define architecture")
        
        # Default challenge if none found
        if not challenges:
            challenges.append("Standard startup execution risks apply")
        
        return challenges[:5]  # Top 5 challenges
    
    def _estimate_timeline(self, complexity: float, team_size: int) -> int:
        """Estimate realistic timeline in months"""
        # Base: 3 months for simple project
        base_months = 3
        
        # Multiply by complexity
        complex_months = base_months * complexity
        
        # Adjust for team size
        team_factor = self._calculate_team_factor(team_size)
        adjusted_months = complex_months * team_factor
        
        return max(int(adjusted_months), 1)
    
    def _min_team_size(self, complexity: float) -> int:
        """Minimum recommended team size"""
        if complexity >= 7:
            return 5  # Complex projects need full team
        elif complexity >= 4:
            return 3  # Medium complexity
        elif complexity >= 2:
            return 2  # Low-medium complexity
        else:
            return 1  # Simple projects OK solo
    
    def _min_budget(self, complexity: float, team_size: int) -> float:
        """Minimum budget estimate (USD)"""
        # $5K per month per person (MVP budget)
        months = self._estimate_timeline(complexity, team_size)
        cost_per_person_month = 5000
        
        return months * max(team_size, self._min_team_size(complexity)) * cost_per_person_month
    
    def _calculate_confidence(self, timeline_risk: str, budget_risk: str, team_size: int) -> int:
        """Calculate confidence in execution (0-100)"""
        confidence = 100
        
        # Penalize unrealistic plans
        if timeline_risk == "Unrealistic":
            confidence -= 30
        elif timeline_risk == "Optimistic":
            confidence -= 15
        
        if budget_risk == "Insufficient":
            confidence -= 30
        elif budget_risk == "Tight":
            confidence -= 15
        
        if team_size == 1:
            confidence -= 20
        
        return max(confidence, 0)
