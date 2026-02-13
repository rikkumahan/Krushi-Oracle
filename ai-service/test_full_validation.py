"""
Direct Universal Validation Test
Bypasses FastAPI endpoint to test validation logic directly
"""

import asyncio
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_direct_validation():
    """Test universal validation directly without FastAPI endpoint"""
    
    print("=" * 80)
    print("🧪 Direct Universal Validation Test (Bypassing FastAPI)")
    print("=" * 80)
    
    try:
        # Import validation components
        print("\n📦 Loading validation components...")
        from verification.dependencies import get_universal_validator
        from verification.universal_validator import UniversalValidationRequest
        
        print("✅ Imports successful")
        
        # Get validator instance
        print("\n🔌 Initializing universal validator...")
        validator = get_universal_validator()
        print("✅ Validator initialized")
        
        # Create test request
        print("\n📋 Creating validation request...")
        request = UniversalValidationRequest(
            idea_name="AI-Powered Code Review Assistant",
            idea_description="Automated code review tool that uses machine learning to detect bugs, security vulnerabilities, and suggest improvements for pull requests across multiple programming languages",
            keywords=["code review", "AI developer tools", "static analysis"],
            sector="software",
            tech_stack=["Python", "FastAPI", "Machine Learning", "Docker"],
            team_size=3,
            timeline_months=12,
            budget_usd=150000
        )
        print(f"✅ Request created for: {request.idea_name}")
        
        # Run validation
        print("\n⚡ Running validation (this will call 6 external APIs)...")
        print("  - Google Trends")
        print("  - Google Autocomplete")
        print("  - YouTube Data API")
        print("  - News API")
        print("   - Reddit (YARS Scraper)")
        print("  - Wikipedia Pageviews")
        print()
        
        result = await validator.validate(request)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 VALIDATION RESULTS")
        print("=" * 80)
        
        print(f"\n🎯 Idea: {request.idea_name}")
        print(f"📂 Sector: {request.sector}")
        
        print(f"\n📈 MARKET VALIDATION: {result.market_validation_score}/100")
        print(f"  - Google Trends: {result.google_trends_score}/100")
        print(f"  - Autocomplete Popularity: {result.autocomplete_popularity}/100")
        print(f"  - Wikipedia Interest: {result.wikipedia_interest}/100")
        
        print(f"\n👥 SOCIAL PROOF: {result.social_proof_score}/100")
        print(f"  - Reddit Engagement: {result.reddit_engagement}/100")
        print(f"  - YouTube Coverage: {result.youtube_coverage}/100")
        print(f"  - News Mentions: {result.news_mentions}/100")
        
        print(f"\n⚙️  EXECUTION RISK:")
        print(f"  - Complexity: {result.execution_complexity}/100")
        print(f"  - Risk Level: {result.execution_risk_level}")
        print(f"  - Estimated Timeline: {result.estimated_months} months")
        print(f"  - Key Challenges: {', '.join(result.key_challenges)}")
        
        print(f"\n🎯 OVERALL CONFIDENCE: {result.overall_confidence}/100")
        
        # Calculate verdict
        if result.overall_confidence >= 75:
            verdict = "🚀 STRONG OPPORTUNITY"
        elif result.overall_confidence >= 60:
            verdict = "✅ VIABLE"
        elif result.overall_confidence >= 45:
            verdict = "⚠️ MODERATE POTENTIAL"
        else:
            verdict = "❌ HIGH RISK"
        
        print(f"📋 Verdict: {verdict}")
        
        print(f"\n📊 DATA QUALITY:")
        print(f"  - Sources Used: {result.data_sources_used}")
        print(f"  - Fallback Count: {result.fallback_count}/6")
        print(f"  - Reliability: {'High' if result.fallback_count <= 2 else 'Medium' if result.fallback_count <= 4 else 'Low'}")
        
        print("\n" + "=" * 80)
        print("✅ VALIDATION COMPLETE!")
        print("=" * 80)
        
        # Export as JSON
        json_result = {
            "idea_name": request.idea_name,
            "sector": request.sector,
            "market_validation": {
                "google_trends_score": result.google_trends_score,
                "autocomplete_popularity": result.autocomplete_popularity,
                "wikipedia_interest": result.wikipedia_interest,
                "overall_score": result.market_validation_score
            },
            "social_proof": {
                "reddit_engagement": result.reddit_engagement,
                "youtube_coverage": result.youtube_coverage,
                "news_mentions": result.news_mentions,
                "overall_score": result.social_proof_score
            },
            "execution_risk": {
                "complexity_score": result.execution_complexity,
                "risk_level": result.execution_risk_level,
                "estimated_months": result.estimated_months,
                "key_challenges": result.key_challenges
            },
            "overall_confidence": result.overall_confidence,
            "verdict": verdict,
            "data_quality": {
                "sources_used": result.data_sources_used,
                "fallback_count": result.fallback_count
            }
        }
        
        with open("validation_result.json", "w") as f:
            json.dump(json_result, f, indent=2)
        
        print(f"\n💾 Results saved to: validation_result.json")
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_validation())
