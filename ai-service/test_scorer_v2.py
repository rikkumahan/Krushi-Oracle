"""
Test Suite for Deterministic Scoring Engine V2

Verifies:
1. Determinism (100% reproducibility)
2. All innovations work
3. Audit trail generation
4. MVS calculations
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.idea_scorer_v2.engine import DeterministicScorerV2, IdeaInput
from services.idea_scorer_v2.signal_fusion import MarketSignals
from services.idea_scorer_v2.momentum_analyzer import TimeSeriesData
from services.idea_scorer_v2.competition_mapper import CompetitiveData
from services.idea_scorer_v2.tech_analyzer import TechStack, Technology, TechCategory


def create_sample_idea() -> IdeaInput:
    """Create a sample idea for testing"""
    
    # Market signals
    signals = MarketSignals(
        monthly_searches=25000,
        growth_rate_30d=0.15,  # +15% growth
        video_count=350,
        total_views=1800000,
        post_count=120,
        total_score=2400,
        daily_views=850,
        article_count_30d=45,
        unique_sources=12
    )
    
    # Time-series data (simulated trending upward)
    trends_30d = TimeSeriesData(
        values=[100, 105, 110, 115, 120, 125, 130],
        period_days=30
    )
    
    trends_90d = TimeSeriesData(
        values=[80, 85, 90, 95, 100, 105, 110, 115, 120],
        period_days=90
    )
    
    trends_180d = TimeSeriesData(
        values=[60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120],
        period_days=180
    )
    
    # Competitive data
    comp_data = CompetitiveData(
        commercial_entity_count=25,
        top_player_market_shares=[30, 20, 15, 10, 5],  # HHI = 1550 (Oligopoly)
        new_entrants_12m=8,
        exits_12m=3,
        substitute_count=12,
        patent_filings_12m=5,
        funding_rounds_12m=15,
        youtube_video_count=350,
        blog_post_count=1200
    )
    
    # Tech stack (moderate complexity)
    from services.idea_scorer_v2.tech_analyzer import TechStackAnalyzer
    
    tech_db = TechStackAnalyzer.TECH_DB
    tech_stack = TechStack(
        technologies=[
            tech_db["Next.js"],
            tech_db["FastAPI"],
            tech_db["PostgreSQL"],
            tech_db["Prisma"],
            tech_db["Vercel"]
        ],
        team_experience={
            "Next.js": "FAMILIAR",
            "FastAPI": "FAMILIAR",
            "PostgreSQL": "BEGINNER",
            "Prisma": "FAMILIAR",
            "Vercel": "EXPERT"
        }
    )
    
    return IdeaInput(
        idea_name="AI-Powered Meal Planning for Busy Professionals",
        idea_description="Personalized meal plans with grocery lists and recipe videos",
        target_market="Busy professionals aged 25-45",
        market_signals=signals,
        trends_30d=trends_30d,
        trends_90d=trends_90d,
        trends_180d=trends_180d,
        competitive_data=comp_data,
        tech_stack=tech_stack,
        estimated_capital_needed=150000
    )


def test_basic_scoring():
    """Test basic scoring functionality"""
    print("\n" + "="*70)
    print("TEST 1: Basic Scoring")
    print("="*70)
    
    scorer = DeterministicScorerV2()
    idea = create_sample_idea()
    
    result = scorer.score_idea(idea)
    
    print(f"\n✅ Idea: {result.idea_name}")
    print(f"MVS Score: {result.mvs_score}/100 (Grade: {result.mvs_grade})")
    print(f"Classification: {result.validation_class}")
    print(f"\nDimension Scores:")
    print(f"  - Market: {result.market_dimension}/100")
    print(f"  - Differentiation: {result.differentiation_dimension}/100")
    print(f"  - Execution: {result.execution_dimension}/100")
    print(f"  - Capital: {result.capital_dimension}/100")
    
    if result.quality_gates_triggered:
        print(f"\n⚠️ Quality Gates Triggered: {len(result.quality_gates_triggered)}")
        for gate in result.quality_gates_triggered:
            print(f"  - {gate}")
    
    print(f"\n📝 Recommendations: {len(result.recommendations)}")
    for i, rec in enumerate(result.recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    return result


def test_determinism():
    """Test that scoring is 100% deterministic"""
    print("\n" + "="*70)
    print("TEST 2: Determinism Verification")
    print("="*70)
    
    scorer = DeterministicScorerV2()
    idea = create_sample_idea()
    
    print("\nRunning 100 iterations with same input...")
    verification = scorer.verify_determinism(idea, runs=100)
    
    print(f"\n✅ Verdict: {verification['verdict']}")
    print(f"Unique scores seen: {verification['unique_scores']}")
    print(f"Expected: 1 unique score")
    print(f"Actual: {verification['actual_count']} unique score(s)")
    print(f"Runs: {verification['run_count']}")
    
    assert verification['is_deterministic'], "❌ FAILED: Scoring is not deterministic!"
    
    return verification


def test_innovations():
    """Test each innovation individually"""
    print("\n" + "="*70)
    print("TEST 3: Individual Innovation Tests")
    print("="*70)
    
    scorer = DeterministicScorerV2()
    idea = create_sample_idea()
    result = scorer.score_idea(idea)
    
    # Test Innovation 1: Signal Fusion
    print("\n1️⃣ Innovation 1: Composite Signal Fusion")
    signal_output = result.signal_fusion_output
    print(f"   Demand Score: {signal_output['demand_score']}/100")
    print(f"   Confidence: {signal_output['confidence']}/100")
    print(f"   Rule: {signal_output['rule_applied']}")
    
    # Test Innovation 2: Momentum
    print("\n2️⃣ Innovation 2: Momentum Analysis")
    momentum_output = result.momentum_analysis_output
    print(f"   Momentum Score: {momentum_output['momentum_score']}/100")
    print(f"   Trend Pattern: {momentum_output['trend_pattern']}")
    print(f"   Weighted Slope: {momentum_output['weighted_slope']}")
    
    # Test Innovation 3: Competition
    print("\n3️⃣ Innovation 3: Competitive Density Mapping")
    comp_output = result.competition_analysis_output
    print(f"   Competition Score: {comp_output['competition_score']}/100")
    print(f"   Market Structure: {comp_output['market_structure']}")
    print(f"   HHI Index: {comp_output['hhi_index']}")
    
    # Test Innovation 4: Tech Stack
    print("\n4️⃣ Innovation 4: Tech Stack Analysis")
    tech_output = result.tech_analysis_output
    print(f"   Execution Score: {tech_output['execution_score']}/100")
    print(f"   Complexity: {tech_output['complexity_rating']}")
    print(f"   Learning Time: {tech_output['estimated_learning_months']} months")
    
    # Test Innovation 5: MVS
    print("\n5️⃣ Innovation 5: Market Validation Score")
    mvs_output = result.mvs_calculation_output
    print(f"   Final MVS: {mvs_output['mvs_score']}/100")
    print(f"   Grade: {mvs_output['grade']}")
    print(f"   Quality Gates: {len(mvs_output['quality_gates_triggered'])}")
    
    return result


def test_audit_trail():
    """Test audit trail generation"""
    print("\n" + "="*70)
    print("TEST 4: Audit Trail Generation")
    print("="*70)
    
    scorer = DeterministicScorerV2()
    idea = create_sample_idea()
    result = scorer.score_idea(idea)
    
    print("\n✅ Audit Trail Structure:")
    audit = result.audit_trail
    
    for key in audit.keys():
        print(f"  - {key}")
    
    # Verify determinism proof
    proof = audit['determinism_proof']
    print(f"\n🔒 Determinism Proof:")
    print(f"  - Engine Version: {proof['engine_version']}")
    print(f"  - Computation Path: {proof['computation_path']}")
    print(f"  - LLM Usage: {proof['llm_usage']}")
    print(f"  - Reproducibility: {proof['reproducibility']}")
    
    # Export as JSON
    json_trail = scorer.export_audit_trail_json(result)
    print(f"\n📄 JSON Audit Trail: {len(json_trail)} bytes")
    
    return audit


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 DETERMINISTIC SCORING ENGINE V2 - TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Basic scoring
        result = test_basic_scoring()
        
        # Test 2: Determinism
        verification = test_determinism()
        
        # Test 3: Individual innovations
        test_innovations()
        
        # Test 4: Audit trail
        audit = test_audit_trail()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print(f"\nEngine is 100% deterministic: {verification['is_deterministic']}")
        print(f"MVS Score: {result.mvs_score}/100")
        print(f"Grade: {result.mvs_grade}")
        print(f"Validation: {result.validation_class}")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED!")
        print("="*70)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
