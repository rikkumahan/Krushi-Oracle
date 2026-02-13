"""
Quick test for YARS Reddit scraper
"""

import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)


async def test_yars():
    """Test YARS scraper functionality"""
    
    print("=" * 70)
    print("🧪 YARS Reddit Scraper Test")
    print("=" * 70)
    
    try:
        from services.external.reddit_scraper import RedditScraperService
        
        print("\n✅ Import successful!")
        
        # Initialize scraper
        reddit = RedditScraperService()
        
        if not reddit.available:
            print("❌ YARS not available - check installation")
            return
        
        print("✅ YARS initialized successfully")
        
        # Test search
        print("\n🔍 Testing Reddit search for 'project management'...")
        result = await reddit.search_discussions(
            keyword="project management",
            limit=10
        )
        
        print(f"\n📊 Results:")
        print(f"  Posts found: {result['post_count']}")
        print(f"  Avg score: {result['avg_score']}")
        print(f"  Avg comments: {result['avg_comments']}")
        print(f"  Engagement score: {result['engagement_score']}/100")
        print(f"  Data source: {result['data_source']}")
        
        if result['post_count'] > 0:
            print("\n✅ YARS is working! Real Reddit data retrieved.")
        else:
            print("\n⚠️  No posts found - might be rate limited or search issue")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_yars())
