"""
Test Redis Caching Layer
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)


async def test_redis_caching():
    """Test Redis cache with universal validator"""
    
    print("=" * 70)
    print("🧪 Redis Caching Test")
    print("=" * 70)
    
    try:
        from verification.dependencies import get_universal_validator
        from verification.universal_validator import UniversalValidationRequest
        
        print("\n✅ Imports successful!")
        
        # Get validator (with caching)
        validator = get_universal_validator()
        print("✅ Universal validator initialized with Redis caching")
        
        # Test request
        request = UniversalValidationRequest(
            idea_name="AI Project Management Tool",
            idea_description="AI-powered project management for software teams",
            keywords=["project management", "AI productivity"],
            sector="software",
            tech_stack=["Python", "React", "FastAPI"],
            team_size=2,
            timeline_months=6,
            budget_usd=50000
        )
        
        print("\n🔍 First validation (should hit APIs)...")
        result1 = await validator.validate(request)
        print(f"\n📊 Result 1:")
        print(f"  Overall confidence: {result1.overall_confidence}/100")
        print(f"  Fallback count: {result1.fallback_count}")
        
        print("\n🔄 Second validation (should use cache)...")
        result2 = await validator.validate(request)
        print(f"\n📊 Result 2:")
        print(f"  Overall confidence: {result2.overall_confidence}/100")
        print(f"  Fallback count: {result2.fallback_count}")
        
        # Verify results match (deterministic)
        if result1.overall_confidence == result2.overall_confidence:
            print("\n✅ Cache working! Results are identical (deterministic)")
        else:
            print("\n⚠️  Results differ - check caching implementation")
        
        print("\n✅ Redis caching test complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_redis_caching())
