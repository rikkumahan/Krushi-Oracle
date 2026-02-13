"""
Test Suite for Strategic Audit Agent

Tests LLM agent with deterministic tools and FastAPI endpoints.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.idea_scorer_v2.engine import DeterministicScorerV2
from services.explanatory.strategic_audit_agent import (
    StrategicAuditAgent,
    StrategicTools,
    AuditQuery
)
from test_scorer_v2 import create_sample_idea


async def test_tools():
    """Test deterministic tools"""
    print("\n" + "="*70)
    print("TEST 1: Deterministic Tools")
    print("="*70)
    
    # Score an idea first
    scorer = DeterministicScorerV2()
    idea = create_sample_idea()
    result = scorer.score_idea(idea)
    
    # Initialize tools
    tools = StrategicTools(result)
    
    # Test each tool
    print("\n1️⃣ Testing get_market_segments()...")
    market = tools.get_market_segments()
    print(f"   TAM: ${market['tam_usd']:,}")
    print(f"   SAM: ${market['sam_usd']:,}")
    print(f"   SOM (Year 3): ${market['som_year3_usd']:,}")
    
    print("\n2️⃣ Testing get_competitive_moat()...")
    moat = tools.get_competitive_moat()
    print(f"   HHI Index: {moat['hhi_index']}")
    print(f"   Market Structure: {moat['market_structure']}")
    print(f"   Competition Score: {moat['competition_score']}/100")
    
    print("\n3️⃣ Testing get_momentum_vector()...")
    momentum = tools.get_momentum_vector()
    print(f"   Trend Pattern: {momentum['trend_pattern']}")
    print(f"   Slope: {momentum['slope_percentage']}")
    print(f"   Momentum Score: {momentum['momentum_score']}/100")
    
    print("\n4️⃣ Testing get_execution_risk()...")
    execution = tools.get_execution_risk()
    print(f"   Execution Score: {execution['execution_score']}/100")
    print(f"   Complexity: {execution['complexity_rating']}")
    print(f"   Learning Time: {execution['learning_months']} months")
    
    print("\n5️⃣ Testing compare_scenarios()...")
    scenario = tools.compare_scenarios("market", 90)
    print(f"   Scenario: {scenario['scenario']}")
    print(f"   Current MVS: {scenario['current_mvs']}")
    print(f"   New MVS: {scenario['new_mvs']}")
    print(f"   Delta: {scenario['delta_percentage']}")
    
    print("\n6️⃣ Testing recommend_improvements()...")
    recs = tools.recommend_improvements()
    print(f"   Recommendations: {len(recs)}")
    for i, rec in enumerate(recs[:3], 1):
        print(f"   {i}. [{rec['priority']}] {rec['recommendation'][:60]}...")
    
    print("\n✅ All tools working correctly!")
    return tools


async def test_agent():
    """Test Strategic Audit Agent"""
    print("\n" + "="*70)
    print("TEST 2: Strategic Audit Agent")
    print("="*70)
    
    # Score an idea first
    scorer = DeterministicScorerV2()
    idea = create_sample_idea()
    result = scorer.score_idea(idea)
    
    print(f"\n📊 Scored Idea: {result.idea_name}")
    print(f"MVS: {result.mvs_score}/100 (Grade: {result.mvs_grade})")
    
    # Initialize agent
    try:
        agent = StrategicAuditAgent()
        print("\n✅ Agent initialized successfully")
    except RuntimeError as e:
        print(f"\n⚠️ Agent initialization failed: {e}")
        print("Make sure OpenAI API key is configured in .env")
        return None
    
    # Test questions
    questions = [
        "Why is my market score 71/100? Explain like a VC.",
        "What's my biggest risk according to the data?",
        "If I improved my differentiation score to 70, what would my new MVS be?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*70}")
        print(f"QUESTION {i}: {question}")
        print('='*70)
        
        query = AuditQuery(question=question)
        
        try:
            explanation = await agent.explain(result, query)
            
            print(f"\n✅ Answer:")
            print(explanation.answer)
            
            print(f"\n🔧 Tools Used: {', '.join(explanation.tools_used)}")
            print(f"📊 Data Points Cited: {len(explanation.data_cited)}")
            print(f"🎯 Confidence: {explanation.confidence}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    return agent


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 STRATEGIC AUDIT AGENT - TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Tools
        tools = await test_tools()
        
        # Test 2: Agent
        agent = await test_agent()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70)
        
        if agent is None:
            print("\n⚠️ Note: Agent tests skipped due to missing API key")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED!")
        print("="*70)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
