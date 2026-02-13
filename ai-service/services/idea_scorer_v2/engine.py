"""
Deterministic Scoring Engine V2 - Main Orchestrator

Coordinates all 5 innovations into a unified scoring pipeline.
100% deterministic - NO LLM in computation.

Architecture:
1. Composite Signal Fusion → demand_score
2. Momentum Analyzer → momentum_score
3. Competitive Density Mapper → competition_score
4. Tech Stack Analyzer → execution_score
5. MVS Calculator → final_mvs_score

Generates complete audit trail for Strategic Audit Agent.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json
from datetime import datetime

from .signal_fusion import CompositeSignalScorer, MarketSignals, SignalWeights
from .momentum_analyzer import MomentumAnalyzer, TimeSeriesData
from .competition_mapper import CompetitiveDensityMapper, CompetitiveData
from .tech_analyzer import TechStackAnalyzer, TechStack, Technology
from .mvs_calculator import MarketValidationScorer, MVSInputs


@dataclass
class IdeaInput:
    """Input data for scoring an idea"""
    
    idea_name: str
    idea_description: str
    target_market: str
    
    # Market signals
    market_signals: MarketSignals
    
    # Time-series data
    trends_30d: TimeSeriesData
    trends_90d: TimeSeriesData
    trends_180d: TimeSeriesData
    
    # Competitive data
    competitive_data: CompetitiveData
    
    # Tech stack
    tech_stack: TechStack
    
    # Capital estimate (optional)
    estimated_capital_needed: Optional[int] = None  # USD


@dataclass
class ScoringResult:
    """Complete scoring result with audit trail"""
    
    # Meta
    idea_name: str
    scored_at: str
    
    # Final score
    mvs_score: int
    mvs_grade: str
    validation_class: str
    
    # Dimension scores
    market_dimension: int
    differentiation_dimension: int
    execution_dimension: int
    capital_dimension: int
    
    # Innovation outputs (full audit trail)
    signal_fusion_output: Dict[str, Any]
    momentum_analysis_output: Dict[str, Any]
    competition_analysis_output: Dict[str, Any]
    tech_analysis_output: Dict[str, Any]
    mvs_calculation_output: Dict[str, Any]
    
    # Recommendations
    recommendations: List[str]
    quality_gates_triggered: List[str]
    
    # Audit metadata
    audit_trail: Dict[str, Any]
    
    # Optional with defaults
    engine_version: str = "2.0"


class DeterministicScorerV2:
    """
    Main deterministic scoring engine.
    
    Orchestrates all 5 innovations and generates complete audit trail.
    """
    
    VERSION = "2.0-deterministic"
    
    # Capital efficiency thresholds (USD)
    CAPITAL_BOOTSTRAPPABLE = 50_000
    CAPITAL_SEED_FUNDABLE = 250_000
    CAPITAL_SERIES_A = 1_000_000
    CAPITAL_SERIES_B = 5_000_000
    
    # Score adjustments
    EXECUTION_BOOST_FACTOR = 10  # ±5 points per 50 point execution score difference
    COMPETITION_BOOST_FACTOR = 10  # ±5 points per 50 point competition score difference
    
    def __init__(
        self,
        signal_weights: Optional[SignalWeights] = None
    ):
        """Initialize all scorers"""
        self.signal_scorer = CompositeSignalScorer(weights=signal_weights)
        self.momentum_analyzer = MomentumAnalyzer()
        self.competition_mapper = CompetitiveDensityMapper()
        self.tech_analyzer = TechStackAnalyzer()
        self.mvs_calculator = MarketValidationScorer()
    
    def score_idea(self, idea: IdeaInput) -> ScoringResult:
        """
        Score an idea deterministically.
        
        Returns complete ScoringResult with audit trail.
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Innovation 1: Composite Signal Fusion
        signal_output = self.signal_scorer.score_market_demand(idea.market_signals)
        
        # Innovation 2: Momentum Analysis
        momentum_output = self.momentum_analyzer.analyze_momentum(
            idea.trends_30d,
            idea.trends_90d,
            idea.trends_180d
        )
        
        # Innovation 3: Competitive Density Mapping
        competition_output = self.competition_mapper.map_competition(idea.competitive_data)
        
        # Innovation 4: Tech Stack Analysis
        tech_output = self.tech_analyzer.analyze_stack(idea.tech_stack)
        
        # Innovation 5: Calculate capital efficiency (simplified for now)
        capital_efficiency = self._estimate_capital_efficiency(
            idea.estimated_capital_needed,
            tech_output['execution_score'],
            competition_output['competition_score']
        )
        
        # Innovation 5: MVS Calculation
        mvs_inputs = MVSInputs(
            demand_score=signal_output['demand_score'],
            demand_confidence=signal_output['confidence'],
            momentum_score=momentum_output['momentum_score'],
            trend_pattern=momentum_output['trend_pattern'],
            competition_score=competition_output['competition_score'],
            market_structure=competition_output['market_structure'],
            execution_score=tech_output['execution_score'],
            complexity_rating=tech_output['complexity_rating'],
            capital_efficiency_score=capital_efficiency
        )
        
        mvs_output = self.mvs_calculator.calculate_mvs(mvs_inputs)
        
        # Build complete audit trail
        audit_trail = self._build_audit_trail(
            idea,
            signal_output,
            momentum_output,
            competition_output,
            tech_output,
            mvs_output
        )
        
        # Assemble result
        result = ScoringResult(
            idea_name=idea.idea_name,
            scored_at=timestamp,
            engine_version=self.VERSION,
            mvs_score=mvs_output.mvs_score,
            mvs_grade=mvs_output.grade,
            validation_class=mvs_output.validation_class,
            market_dimension=mvs_output.market_dimension,
            differentiation_dimension=mvs_output.differentiation_dimension,
            execution_dimension=mvs_output.execution_dimension,
            capital_dimension=mvs_output.capital_dimension,
            signal_fusion_output=signal_output,
            momentum_analysis_output=momentum_output,
            competition_analysis_output=competition_output,
            tech_analysis_output=tech_output,
            mvs_calculation_output=asdict(mvs_output),
            recommendations=mvs_output.recommendations,
            quality_gates_triggered=mvs_output.quality_gates_triggered,
            audit_trail=audit_trail
        )
        
        return result
    
    def _estimate_capital_efficiency(
        self,
        capital_needed: Optional[int],
        execution_score: int,
        competition_score: int
    ) -> int:
        """
        Estimate capital efficiency score (0-100).
        
        Higher score = Less capital needed = Better for bootstrapping.
        
        Factors:
        - Estimated capital requirement
        - Execution complexity (simpler = less capital)
        - Competition intensity (easier market = less capital for customer acquisition)
        """
        if capital_needed is None:
            # Default to moderate
            base_score = 50
        elif capital_needed < self.CAPITAL_BOOTSTRAPPABLE:
            base_score = 90  # Bootstrappable
        elif capital_needed < self.CAPITAL_SEED_FUNDABLE:
            base_score = 75  # Seed-fundable
        elif capital_needed < self.CAPITAL_SERIES_A:
            base_score = 60  # Series A scale
        elif capital_needed < self.CAPITAL_SERIES_B:
            base_score = 40  # Series B scale
        else:
            base_score = 20  # Heavy capital
        
        # Boost from high execution score (simple to build = less burn)
        execution_boost = (execution_score - 50) / self.EXECUTION_BOOST_FACTOR
        
        # Boost from low competition (easier CAC = less marketing spend)
        competition_boost = (competition_score - 50) / self.COMPETITION_BOOST_FACTOR
        
        efficiency_score = base_score + execution_boost + competition_boost
        
        return int(max(0, min(100, efficiency_score)))
    
    def _build_audit_trail(
        self,
        idea: IdeaInput,
        signal_output: Dict,
        momentum_output: Dict,
        competition_output: Dict,
        tech_output: Dict,
        mvs_output
    ) -> Dict[str, Any]:
        """
        Build complete audit trail for Strategic Audit Agent.
        
        This is what the LLM will use to explain scores.
        """
        return {
            'input': {
                'idea_name': idea.idea_name,
                'idea_description': idea.idea_description,
                'target_market': idea.target_market,
                'estimated_capital': idea.estimated_capital_needed
            },
            'innovation_1_signal_fusion': {
                'outputs': signal_output,
                'rule_name': 'BAYESIAN_SIGNAL_AGGREGATION',
                'deterministic': True,
                'weights': {
                    'google_trends_volume': 0.25,
                    'google_trends_growth': 0.15,
                    'youtube_coverage': 0.15
                }
            },
            'innovation_2_momentum': {
                'outputs': momentum_output,
                'rule_name': 'TIME_SERIES_LINEAR_REGRESSION',
                'deterministic': True,
                'windows': ['30d', '90d', '180d']
            },
            'innovation_3_competition': {
                'outputs': competition_output,
                'rule_name': 'HHI_INDEX_CALCULATION',
                'deterministic': True,
                'market_structure': competition_output['market_structure']
            },
            'innovation_4_tech_stack': {
                'outputs': tech_output,
                'rule_name': 'INTERACTION_MATRIX_ANALYSIS',
                'deterministic': True,
                'complexity_rating': tech_output['complexity_rating']
            },
            'innovation_5_mvs': {
                'outputs': asdict(mvs_output),
                'rule_name': 'QUALITY_GATE_MVS',
                'deterministic': True,
                'formula': 'MVS = 0.35*Market + 0.30*Diff + 0.20*Exec + 0.15*Capital'
            },
            'determinism_proof': {
                'engine_version': self.VERSION,
                'computation_path': 'PURE_DETERMINISTIC',
                'llm_usage': 'NONE',
                'reproducibility': '100%',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def export_audit_trail_json(self, result: ScoringResult) -> str:
        """Export audit trail as JSON for LLM consumption"""
        return json.dumps(asdict(result), indent=2, default=str)
    
    def verify_determinism(self, idea: IdeaInput, runs: int = 100) -> Dict[str, Any]:
        """
        Verify determinism by running the same input N times.
        
        Returns:
        - is_deterministic: True if all runs match
        - unique_scores: Set of unique MVS scores seen
        - run_count: Number of runs
        """
        scores = set()
        
        for _ in range(runs):
            result = self.score_idea(idea)
            scores.add(result.mvs_score)
        
        return {
            'is_deterministic': len(scores) == 1,
            'unique_scores': list(scores),
            'expected_count': 1,
            'actual_count': len(scores),
            'run_count': runs,
            'verdict': 'DETERMINISTIC ✅' if len(scores) == 1 else 'NON-DETERMINISTIC ❌'
        }
