"""
Property-Based Tests for Scorer V2 - Edge Cases

Uses Hypothesis for comprehensive edge case coverage.
Tests invariants that must hold for ALL inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from services.idea_scorer_v2.signal_fusion import CompositeSignalScorer, MarketSignals
from services.idea_scorer_v2.momentum_analyzer import MomentumAnalyzer, TimeSeriesData
from services.idea_scorer_v2.competition_mapper import CompetitiveDensityMapper, CompetitiveData
from services.idea_scorer_v2.tech_analyzer import TechStackAnalyzer, TechStack, Technology, TechCategory
from services.idea_scorer_v2.mvs_calculator import MarketValidationScorer, MVSInputs


# ============================================================================
# Signal Fusion Property Tests
# ============================================================================

@given(
    monthly_searches=st.integers(min_value=0, max_value=10_000_000),
    growth_rate=st.floats(min_value=-1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    video_count=st.integers(min_value=0, max_value=100_000),
    total_views=st.integers(min_value=0, max_value=100_000_000)
)
@settings(max_examples=100)
def test_signal_fusion_bounds(monthly_searches, growth_rate, video_count, total_views):
    """Property: Demand score must be 0-100 regardless of inputs"""
    scorer = CompositeSignalScorer()
    signals = MarketSignals(
        monthly_searches=monthly_searches,
        growth_rate_30d=growth_rate,
        video_count=video_count,
        total_views=total_views
    )
    
    result = scorer.score_market_demand(signals)
    
    # Invariant: Score must be bounded
    assert 0 <= result['demand_score'] <= 100, f"Score {result['demand_score']} out of bounds"
    assert 0 <= result['confidence'] <= 100, f"Confidence {result['confidence']} out of bounds"


@given(
    signals=st.builds(
        MarketSignals,
        monthly_searches=st.integers(min_value=0, max_value=1_000_000),
        growth_rate_30d=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False)
    )
)
@settings(max_examples=50)
def test_signal_fusion_determinism(signals):
    """Property: Same input always produces same output"""
    scorer = CompositeSignalScorer()
    
    result1 = scorer.score_market_demand(signals)
    result2 = scorer.score_market_demand(signals)
    
    assert result1['demand_score'] == result2['demand_score']
    assert result1['confidence'] == result2['confidence']


def test_signal_fusion_zero_inputs():
    """Edge case: All zeros should not crash"""
    scorer = CompositeSignalScorer()
    signals = MarketSignals()  # All default to 0
    
    result = scorer.score_market_demand(signals)
    
    assert 0 <= result['demand_score'] <= 100
    assert result['demand_score'] == 0  # Zero signals → zero score
    assert result['confidence'] >= 0  # But confidence can vary


def test_signal_fusion_max_inputs():
    """Edge case: Maximum values should not overflow"""
    scorer = CompositeSignalScorer()
    signals = MarketSignals(
        monthly_searches=10_000_000,
        growth_rate_30d=10.0,
        video_count=100_000,
        total_views=100_000_000,
        post_count=10_000,
        daily_views=100_000,
        article_count_30d=10_000,
        unique_sources=1000
    )
    
    result = scorer.score_market_demand(signals)
    
    assert 0 <= result['demand_score'] <= 100
    assert result['demand_score'] >= 95  # Max inputs should give high score


# ============================================================================
# Momentum Analyzer Property Tests
# ============================================================================

@given(
    values=st.lists(
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=30
    )
)
@settings(max_examples=100)
def test_momentum_analyzer_bounds(values):
    """Property: Momentum score must be 0-100 for any time series"""
    analyzer = MomentumAnalyzer()
    
    # Create time series data
    trends_30d = TimeSeriesData(values=values, period_days=30)
    trends_90d = TimeSeriesData(values=values, period_days=90)
    trends_180d = TimeSeriesData(values=values, period_days=180)
    
    result = analyzer.analyze_momentum(trends_30d, trends_90d, trends_180d)
    
    assert 0 <= result['momentum_score'] <= 100


@given(
    value=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False)
)
@settings(max_examples=50)
def test_momentum_flat_line(value):
    """Property: Flat line (constant values) should have zero slope"""
    analyzer = MomentumAnalyzer()
    
    flat_line = [value] * 10
    data = TimeSeriesData(values=flat_line, period_days=30)
    
    window_result = analyzer._analyze_window(data)
    
    assert abs(window_result['slope']) < 0.001  # Should be ~0
    assert window_result['trend_strength'] in ['FLAT', 'WEAK']


def test_momentum_declining_market():
    """Edge case: Declining market (negative growth)"""
    analyzer = MomentumAnalyzer()
    
    declining = [100, 90, 80, 70, 60, 50]
    data_30d = TimeSeriesData(values=declining, period_days=30)
    data_90d = TimeSeriesData(values=declining, period_days=90)
    data_180d = TimeSeriesData(values=declining, period_days=180)
    
    result = analyzer.analyze_momentum(data_30d, data_90d, data_180d)
    
    assert result['trend_pattern'] in ['DECLINING', 'COLLAPSING']
    assert result['weighted_slope'] < 0  # Negative slope


def test_momentum_single_point():
    """Edge case: Insufficient data (single point)"""
    analyzer = MomentumAnalyzer()
    
    single_point = TimeSeriesData(values=[100], period_days=30)
    
    result = analyzer._analyze_window(single_point)
    
    assert result['slope'] == 0.0
    assert result['trend_strength'] == 'INSUFFICIENT_DATA'


# ============================================================================
# Competition Mapper Property Tests
# ============================================================================

@given(
    market_shares=st.lists(
        st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
        min_size=0,
        max_size=10
    ).filter(lambda x: sum(x) <= 100)  # Must sum to ≤100%
)
@settings(max_examples=100)
def test_competition_hhi_bounds(market_shares):
    """Property: HHI must be 0-10000"""
    mapper = CompetitiveDensityMapper()
    
    hhi = mapper._calculate_hhi(market_shares)
    
    assert 0 <= hhi <= 10000


def test_competition_monopoly():
    """Edge case: Pure monopoly (100% market share)"""
    mapper = CompetitiveDensityMapper()
    
    data = CompetitiveData(
        commercial_entity_count=1,
        top_player_market_shares=[100.0]
    )
    
    result = mapper.map_competition(data)
    
    assert result['hhi_index'] == 10000  # 100² = 10000
    assert result['market_structure'] == 'MONOPOLY'
    assert result['competition_score'] <= 30  # Hard to compete


def test_competition_perfect_competition():
    """Edge case: Highly fragmented market"""
    mapper = CompetitiveDensityMapper()
    
    # 20 players each with 5% market share
    data = CompetitiveData(
        commercial_entity_count=20,
        top_player_market_shares=[5.0] * 20
    )
    
    result = mapper.map_competition(data)
    
    # HHI = 20 * (5²) = 20 * 25 = 500
    assert result['hhi_index'] == 500
    assert result['market_structure'] in ['FRAGMENTED', 'MODERATE_COMPETITION']
    assert result['competition_score'] >= 70  # Easy to compete


def test_competition_zero_data():
    """Edge case: No competitive data"""
    mapper = CompetitiveDensityMapper()
    
    data = CompetitiveData()  # All zeros
    
    result = mapper.map_competition(data)
    
    assert result['hhi_index'] == 0
    assert result['market_structure'] == 'UNKNOWN'


# ============================================================================
# Tech Stack Analyzer Property Tests
# ============================================================================

def test_tech_stack_empty():
    """Edge case: Empty tech stack"""
    analyzer = TechStackAnalyzer()
    
    stack = TechStack(technologies=[])
    
    result = analyzer.analyze_stack(stack)
    
    # Should handle gracefully
    assert result['execution_score'] >= 0
    assert result['total_complexity'] == 0


def test_tech_stack_single_simple():
    """Edge case: Single simple technology"""
    analyzer = TechStackAnalyzer()
    
    tech = Technology("React", TechCategory.FRONTEND, complexity=5, maturity="MATURE", learning_curve_months=2.0)
    stack = TechStack(technologies=[tech])
    
    result = analyzer.analyze_stack(stack)
    
    assert result['complexity_rating'] == 'SIMPLE'
    assert result['execution_score'] >= 80


def test_tech_stack_expert_team():
    """Edge case: Expert team with complex stack"""
    analyzer = TechStackAnalyzer()
    
    techs = [
        Technology("Kubernetes", TechCategory.DEVOPS, complexity=9, maturity="STABLE", learning_curve_months=6.0),
        Technology("TensorFlow", TechCategory.AI_ML, complexity=9, maturity="MATURE", learning_curve_months=6.0)
    ]
    stack = TechStack(
        technologies=techs,
        team_experience={"Kubernetes": "EXPERT", "TensorFlow": "EXPERT"}
    )
    
    result = analyzer.analyze_stack(stack)
    
    # Expert team should get high readiness
    assert result['team_readiness_score'] == 100
    # But complexity is still high
    assert result['complexity_rating'] in ['COMPLEX', 'ADVANCED']


# ============================================================================
# MVS Calculator Property Tests
# ============================================================================

@given(
    demand=st.integers(min_value=0, max_value=100),
    momentum=st.integers(min_value=0, max_value=100),
    competition=st.integers(min_value=0, max_value=100),
    execution=st.integers(min_value=0, max_value=100),
    capital=st.integers(min_value=0, max_value=100)
)
@settings(max_examples=200)
def test_mvs_bounds(demand, momentum, competition, execution, capital):
    """Property: MVS must be 0-100 for any dimension scores"""
    calculator = MarketValidationScorer()
    
    inputs = MVSInputs(
        demand_score=demand,
        demand_confidence=50,
        momentum_score=momentum,
        trend_pattern="STABLE",
        competition_score=competition,
        market_structure="MODERATE_COMPETITION",
        execution_score=execution,
        complexity_rating="MODERATE",
        capital_efficiency_score=capital
    )
    
    result = calculator.calculate_mvs(inputs)
    
    assert 0 <= result.mvs_score <= 100


def test_mvs_quality_gate_critical():
    """Edge case: Critical weakness should cap MVS at 50"""
    calculator = MarketValidationScorer()
    
    inputs = MVSInputs(
        demand_score=25,  # CRITICAL (<30)
        demand_confidence=100,
        momentum_score=90,
        trend_pattern="RISING_FAST",
        competition_score=90,
        market_structure="FRAGMENTED",
        execution_score=90,
        complexity_rating="SIMPLE",
        capital_efficiency_score=90
    )
    
    result = calculator.calculate_mvs(inputs)
    
    # Despite high scores elsewhere, critical market weakness caps at 50
    assert result.mvs_score <= 50
    assert "CRITICAL_MARKET_WEAKNESS" in result.quality_gates_triggered


def test_mvs_perfect_scores():
    """Edge case: Perfect 100s across all dimensions"""
    calculator = MarketValidationScorer()
    
    inputs = MVSInputs(
        demand_score=100,
        demand_confidence=100,
        momentum_score=100,
        trend_pattern="RISING_FAST",
        competition_score=100,
        market_structure="FRAGMENTED",
        execution_score=100,
        complexity_rating="SIMPLE",
        capital_efficiency_score=100
    )
    
    result = calculator.calculate_mvs(inputs)
    
    assert result.mvs_score >= 95  # Should be near-perfect
    assert result.grade in ['A+', 'A']
    assert result.validation_class == 'ELITE_OPPORTUNITY'


def test_mvs_all_zeros():
    """Edge case: Zero scores across all dimensions"""
    calculator = MarketValidationScorer()
    
    inputs = MVSInputs(
        demand_score=0,
        demand_confidence=0,
        momentum_score=0,
        trend_pattern="COLLAPSING",
        competition_score=0,
        market_structure="MONOPOLY",
        execution_score=0,
        complexity_rating="MOONSHOT",
        capital_efficiency_score=0
    )
    
    result = calculator.calculate_mvs(inputs)
    
    assert result.mvs_score == 0
    assert result.grade == 'F'
    assert result.validation_class == 'NOT_RECOMMENDED'


# ============================================================================
# Cross-Component Integration Tests
# ============================================================================

def test_full_scoring_pipeline_determinism():
    """Integration test: Full scoring should be deterministic"""
    from services.idea_scorer_v2.engine import DeterministicScorerV2
    
    scorer = DeterministicScorerV2()
    
    input_data = {
        "idea_name": "Test Idea",
        "idea_description": "Test description",
        "monthly_searches": 1000,
        "growth_rate_30d": 0.15,
        "video_count": 50,
        "total_views": 10000,
        "post_count": 20,
        "commercial_entity_count": 10,
        "top_player_market_shares": [30, 25, 15],
        "tech_stack": ["React", "Node.js", "PostgreSQL"],
        "team_experience": {},
        "capital_needed": 100000
    }
    
    # Score 10 times
    scores = []
    for _ in range(10):
        result = scorer.score_idea(input_data)
        scores.append(result.mvs_score)
    
    # All scores must be identical
    assert len(set(scores)) == 1, f"Non-deterministic scores: {scores}"


if __name__ == "__main__":
    # Run with: pytest test_scorer_v2_property.py -v
    pytest.main([__file__, "-v", "--tb=short"])
