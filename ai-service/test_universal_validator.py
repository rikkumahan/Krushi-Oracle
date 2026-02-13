"""
Universal Validator Test
Tests all 6 core APIs + Execution Risk

Tests can run with or without API keys (graceful fallbacks)
"""

import asyncio
import json


async def test_universal_validator():
    """Test complete universal validation pipeline"""
    
    # Import services
    from services.external.google_trends import GoogleTrendsService
    from services.external.google_autocomplete import GoogleAutocompleteService
    from services.external.youtube_data import YouTubeDataService
    from services.external.news_api import NewsAPIService
    from services.external.reddit_api import RedditAPIService
    from services.external.wikipedia_pageviews import WikipediaPageviewsService
    from verification.execution_risk import ExecutionRiskAnalyzer
    from verification.universal_validator import (
        UniversalValidatorService,
        UniversalValidationRequest
    )
    
    print("=" * 70)
    print("🧪 UNIVERSAL VALIDATOR TEST - All 6 APIs + Execution Risk")
    print("=" * 70)
    
    # Initialize services
    print("\n📦 Initializing services...")
    trends_service = GoogleTrendsService()
    autocomplete_service = GoogleAutocompleteService()
    youtube_service = YouTubeDataService()
    news_service = NewsAPIService()
    reddit_service = RedditAPIService()
    wikipedia_service = WikipediaPageviewsService()
    execution_analyzer = ExecutionRiskAnalyzer()

    
    # Create universal validator
    validator = UniversalValidatorService(
        trends_service=trends_service,
        autocomplete_service=autocomplete_service,
        youtube_service=youtube_service,
        news_service=news_service,
        reddit_service=reddit_service,
        wikipedia_service=wikipedia_service,
        execution_analyzer=execution_analyzer
    )
    
    # Test cases for different sectors
    test_cases = [
        {
            "name": "Software Startup (SaaS)",
            "request": UniversalValidationRequest(
                idea_name="AI Project Management Tool",
                idea_description="AI-powered project management for remote teams",
                keywords=["project management software", "AI productivity tools"],
                sector="software",
                tech_stack=["React", "FastAPI", "PostgreSQL", "OpenAI"],
                team_size=2,
                timeline_months=6,
                budget_usd=50000
            )
        },
        {
            "name": "Physical Product",
            "request": UniversalValidationRequest(
                idea_name="Smart Coffee Maker",
                idea_description="IoT-enabled coffee maker with mobile app control",
                keywords=["smart coffee maker", "IoT kitchen appliances"],
                sector="physical_product",
                tech_stack=["IoT", "Mobile App", "Cloud"],
                team_size=3,
                timeline_months=12,
                budget_usd=100000
            )
        },
        {
            "name": "Food & Beverage",
            "request": UniversalValidationRequest(
                idea_name="Plant-Based Meal Delivery",
                idea_description="Healthy vegan meal delivery service for urban professionals",
                keywords=["vegan meal delivery", "plant-based food"],
                sector="food_beverage",
                tech_stack=["E-commerce", "Logistics"],
                team_size=4,
                timeline_months=9,
                budget_usd=75000
            )
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'─' * 70}")
        print(f"Idea: {test_case['request'].idea_name}")
        print(f"Sector: {test_case['request'].sector}")
        print(f"Keywords: {', '.join(test_case['request'].keywords)}")
        
        try:
            # Run validation
            result = await validator.validate(test_case['request'])
            
            # Display results
            print(f"\n📊 VALIDATION RESULTS:")
            print(f"\n  🎯 Market Validation:")
            print(f"    - Google Trends Score:     {result.google_trends_score}/100")
            print(f"    - Autocomplete Popularity: {result.autocomplete_popularity}/100")
            print(f"    - Wikipedia Interest:      {result.wikipedia_interest}/100")
            print(f"    - Overall Market Score:    {result.market_validation_score}/100")
            
            print(f"\n  💬 Social Proof:")
            print(f"    - Reddit Engagement:       {result.reddit_engagement}/100")
            print(f"    - YouTube Coverage:        {result.youtube_coverage}/100")
            print(f"    - News Mentions:           {result.news_mentions} articles")
            print(f"    - Overall Social Score:    {result.social_proof_score}/100")
            
            print(f"\n  ⚙️  Execution Risk:")
            print(f"    - Complexity Score:        {result.execution_complexity}/100")
            print(f"    - Risk Level:              {result.execution_risk_level}")
            print(f"    - Estimated Timeline:      {result.estimated_months} months")
            print(f"    - Key Challenges:")
            for challenge in result.key_challenges[:3]:
                print(f"      • {challenge}")
            
            print(f"\n  🎖️  Overall Confidence:      {result.overall_confidence}/100")
            
            print(f"\n  📡 Data Quality:")
            print(f"    - Sources Used:            {len(result.data_sources_used)}")
            print(f"    - Fallback Count:          {result.fallback_count}")
            
            # Verdict
            if result.overall_confidence >= 70:
                verdict = "✅ STRONG OPPORTUNITY"
            elif result.overall_confidence >= 50:
                verdict = "⚠️  MODERATE POTENTIAL"
            else:
                verdict = "❌ HIGH RISK"
            
            print(f"\n  🏆 Verdict: {verdict}")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Cleanup
    print(f"\n{'=' * 70}")
    print("🧹 Cleaning up...")
    await autocomplete_service.close()
    await youtube_service.close()
    await news_service.close()
    await reddit_service.close()
    await wikipedia_service.close()
    
    print("✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(test_universal_validator())
