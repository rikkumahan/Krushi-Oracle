"""
Innovation 5: Market Validation Score (MVS)

Proprietary metric that combines demand, opportunity, timing, and
feasibility with quality gates to identify showstoppers.

Formula:
MVS = 0.35 * Market + 0.30 * Differentiation + 0.20 * Execution + 0.15 * Capital

Quality Gates:
- Any dimension < 30 → caps MVS at 50 (critical weakness)
- Market < 40 → caps MVS at 60 (risky market)

100% deterministic - NO LLM usage.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class MVSInputs:
    """All inputs required for MVS calculation"""
    
    # Market Demand (from Composite Signal Scorer)
    demand_score: int                    # 0-100
    demand_confidence: int               # 0-100
    
    # Market Momentum (from Momentum Analyzer)
    momentum_score: int                  # 0-100
    trend_pattern: str                   # RISING_FAST, RISING, etc.
    
    # Competition (from Competitive Density Mapper)
    competition_score: int               # 0-100 (higher = easier to compete)
    market_structure: str                # MONOPOLY, OLIGOPOLY, etc.
    
    # Technical Execution (from Tech Stack Analyzer)
    execution_score: int                 # 0-100 (higher = easier to execute)
    complexity_rating: str               # SIMPLE, MODERATE, etc.
    
    # Capital Efficiency (estimated from various factors)
    capital_efficiency_score: int = 50   # 0-100 (higher = less capital needed)


@dataclass
class MVSOutput:
    """Market Validation Score output"""
    
    mvs_score: int                       # Final score (0-100)
    grade: str                           # Letter grade (F to A+)
    validation_class: str                # Classification
    quality_gates_triggered: List[str]   # Any showstoppers
    
    # Dimension scores
    market_dimension: int                # Combined demand + momentum
    differentiation_dimension: int       # Competition score
    execution_dimension: int             # Tech execution
    capital_dimension: int               # Capital efficiency
    
    # Detailed breakdown
    breakdown: Dict[str, Any]
    recommendations: List[str]


class MarketValidationScorer:
    """Calculates Market Validation Score with quality gates"""
    
    def calculate_mvs(self, inputs: MVSInputs) -> MVSOutput:
        """
        Calculate comprehensive Market Validation Score.
        
        Returns MVSOutput with detailed breakdown and recommendations.
        """
        # Calculate dimension scores
        market_score = self._calculate_market_dimension(
            inputs.demand_score,
            inputs.demand_confidence,
            inputs.momentum_score,
            inputs.trend_pattern
        )
        
        differentiation_score = inputs.competition_score
        execution_score = inputs.execution_score
        capital_score = inputs.capital_efficiency_score
        
        # Check quality gates
        quality_gates = self._check_quality_gates(
            market_score,
            differentiation_score,
            execution_score,
            capital_score
        )
        
        # Calculate base MVS
        base_mvs = (
            0.35 * market_score +
            0.30 * differentiation_score +
            0.20 * execution_score +
            0.15 * capital_score
        )
        
        # Apply quality gate caps
        capped_mvs = self._apply_quality_gates(base_mvs, quality_gates)
        
        # Classify
        grade = self._assign_grade(capped_mvs)
        validation_class = self._classify_validation(capped_mvs, quality_gates)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            capped_mvs,
            market_score,
            differentiation_score,
            execution_score,
            capital_score,
            quality_gates,
            inputs
        )
        
        return MVSOutput(
            mvs_score=int(capped_mvs),
            grade=grade,
            validation_class=validation_class,
            quality_gates_triggered=quality_gates,
            market_dimension=int(market_score),
            differentiation_dimension=int(differentiation_score),
            execution_dimension=int(execution_score),
            capital_dimension=int(capital_score),
            breakdown={
                'base_mvs': round(base_mvs, 2),
                'capped_mvs': int(capped_mvs),
                'quality_gate_impact': round(base_mvs - capped_mvs, 2),
                'dimension_weights': {
                    'market': 0.35,
                    'differentiation': 0.30,
                    'execution': 0.20,
                    'capital': 0.15
                },
                'dimension_contributions': {
                    'market': round(0.35 * market_score, 2),
                    'differentiation': round(0.30 * differentiation_score, 2),
                    'execution': round(0.20 * execution_score, 2),
                    'capital': round(0.15 * capital_score, 2)
                },
                'inputs_summary': {
                    'demand_score': inputs.demand_score,
                    'momentum_score': inputs.momentum_score,
                    'competition_score': inputs.competition_score,
                    'execution_score': inputs.execution_score,
                    'capital_score': inputs.capital_efficiency_score
                }
            },
            recommendations=recommendations
        )
    
    def _calculate_market_dimension(
        self,
        demand: int,
        confidence: int,
        momentum: int,
        trend: str
    ) -> float:
        """
        Combine demand and momentum into single market score.
        
        Weights:
        - 60% demand (primary signal)
        - 30% momentum (growth trajectory)
        - 10% confidence boost
        """
        # Base: weighted average
        base_market = 0.60 * demand + 0.30 * momentum
        
        # Confidence boost (up to +10 points)
        confidence_boost = (confidence / 100) * 10
        
        # Momentum pattern bonus/penalty
        pattern_adjustments = {
            "RISING_FAST": +5,
            "RISING": +2,
            "STABLE": 0,
            "DECLINING": -10,
            "COLLAPSING": -20,
            "VOLATILE": -5
        }
        pattern_adjustment = pattern_adjustments.get(trend, 0)
        
        market_score = base_market + confidence_boost + pattern_adjustment
        
        return max(0, min(100, market_score))
    
    def _check_quality_gates(
        self,
        market: float,
        differentiation: float,
        execution: float,
        capital: float
    ) -> List[str]:
        """
        Check for showstopper quality gates.
        
        Returns list of triggered gates.
        """
        gates_triggered = []
        
        # Critical weakness gate: any dimension < 30
        if market < 30:
            gates_triggered.append("CRITICAL_MARKET_WEAKNESS")
        if differentiation < 30:
            gates_triggered.append("CRITICAL_DIFFERENTIATION_WEAKNESS")
        if execution < 30:
            gates_triggered.append("CRITICAL_EXECUTION_RISK")
        if capital < 30:
            gates_triggered.append("CRITICAL_CAPITAL_INEFFICIENCY")
        
        # Risky market gate: market < 40
        if market < 40 and "CRITICAL_MARKET_WEAKNESS" not in gates_triggered:
            gates_triggered.append("RISKY_MARKET")
        
        # Moderate risk gate: any dimension 30-40
        if 30 <= market < 40:
            gates_triggered.append("MODERATE_MARKET_RISK")
        if 30 <= differentiation < 40:
            gates_triggered.append("MODERATE_DIFFERENTIATION_RISK")
        if 30 <= execution < 40:
            gates_triggered.append("MODERATE_EXECUTION_RISK")
        
        return gates_triggered
    
    def _apply_quality_gates(
        self,
        base_mvs: float,
        gates: List[str]
    ) -> float:
        """
        Apply quality gate caps to MVS.
        
        Rules:
        - Any CRITICAL_* → cap at 50
        - RISKY_MARKET → cap at 60
        - MODERATE_* → cap at 75
        """
        caps = []
        
        # Critical gates
        critical_gates = [g for g in gates if g.startswith("CRITICAL_")]
        if critical_gates:
            caps.append(50)
        
        # Risky market
        if "RISKY_MARKET" in gates:
            caps.append(60)
        
        # Moderate risks
        moderate_gates = [g for g in gates if g.startswith("MODERATE_")]
        if moderate_gates:
            caps.append(75)
        
        # Apply most restrictive cap
        if caps:
            return min(base_mvs, min(caps))
        
        return base_mvs
    
    def _assign_grade(self, mvs: float) -> str:
        """Assign letter grade"""
        if mvs >= 95:
            return "A+"
        elif mvs >= 90:
            return "A"
        elif mvs >= 85:
            return "A-"
        elif mvs >= 80:
            return "B+"
        elif mvs >= 75:
            return "B"
        elif mvs >= 70:
            return "B-"
        elif mvs >= 65:
            return "C+"
        elif mvs >= 60:
            return "C"
        elif mvs >= 55:
            return "C-"
        elif mvs >= 50:
            return "D"
        else:
            return "F"
    
    def _classify_validation(
        self,
        mvs: float,
        gates: List[str]
    ) -> str:
        """Classify overall validation"""
        if mvs >= 80:
            return "ELITE_OPPORTUNITY"
        elif mvs >= 70:
            return "STRONG_OPPORTUNITY"
        elif mvs >= 60:
            return "VIABLE_WITH_CAUTION"
        elif mvs >= 50:
            return "HIGH_RISK"
        else:
            return "NOT_RECOMMENDED"
    
    def _generate_recommendations(
        self,
        mvs: float,
        market: float,
        differentiation: float,
        execution: float,
        capital: float,
        gates: List[str],
        inputs: MVSInputs
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        # Critical gates
        if "CRITICAL_MARKET_WEAKNESS" in gates:
            recs.append(
                f"🚨 SHOWSTOPPER: Market demand too low ({market:.0f}/100). "
                f"Validate real customer pain before proceeding."
            )
        
        if "CRITICAL_DIFFERENTIATION_WEAKNESS" in gates:
            recs.append(
                f"🚨 SHOWSTOPPER: Competition too intense ({differentiation:.0f}/100). "
                f"Identify unique moat or pivot to less crowded space."
            )
        
        if "CRITICAL_EXECUTION_RISK" in gates:
            recs.append(
                f"🚨 SHOWSTOPPER: Technical execution too complex ({execution:.0f}/100). "
                f"Simplify tech stack or acquire specialized talent."
            )
        
        # Risky market
        if "RISKY_MARKET" in gates:
            recs.append(
                f"⚠️ Market validation weak ({market:.0f}/100). "
                f"Conduct customer interviews and test willingness to pay before building."
            )
        
        # Dimension-specific improvements
        if market < differentiation and market < 70:
            recs.append(
                f"💡 Boost market score: Current {market:.0f}/100. "
                f"Focus on SEO, content marketing, or demand generation."
            )
        
        if differentiation < execution and differentiation < 70:
            recs.append(
                f"💡 Improve differentiation: Current {differentiation:.0f}/100. "
                f"Identify unique positioning or target underserved niche."
            )
        
        if execution < 70:
            recs.append(
                f"💡 Simplify execution: Current {execution:.0f}/100. "
                f"Consider no-code tools, simpler MVP, or outsourcing complex components."
            )
        
        # Momentum-specific
        if inputs.trend_pattern in ["DECLINING", "COLLAPSING"]:
            recs.append(
                f"⚠️ Market momentum is {inputs.trend_pattern}. "
                f"Validate if trend is temporary or structural decline."
            )
        
        # Success indicators
        if mvs >= 80:
            recs.append(
                f"✅ Strong opportunity (MVS: {mvs:.0f}/100). "
                f"Prioritize speed to market and customer acquisition."
            )
        
        return recs
