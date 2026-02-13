"""
Google Trends Integration Test
Tests the new Google Trends service integration
"""

import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_google_trends_integration():
    """Test Google Trends integration via Traffic endpoint"""
    print("="*60)
    print("🔍 Testing Google Trends Integration")
    print("="*60)
    
    # Test 1: Software/SaaS keyword
    test_cases = [
        {
            "name": "SaaS Project Management",
            "data": {
                "keyword": "project management software",
                "industry": "SaaS",
                "target_audience": "Small businesses",
                "budget": 2000.0
            }
        },
        {
            "name": "AI Tools Trend",
            "data": {
                "keyword": "ai writing assistant",
                "industry": "AI Tools",
                "target_audience": "Content creators",
                "budget": 1500.0
            }
        },
        {
            "name": "E-commerce",
            "data": {
                "keyword": "online store builder",
                "industry": "E-commerce",
                "target_audience": "Entrepreneurs",
                "budget": 1000.0
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'─'*60}")
        print(f"Test: {test_case['name']}")
        print(f"Keyword: {test_case['data']['keyword']}")
        print(f"{'─'*60}")
        
        try:
            url = f"{BASE_URL}/api/v2/verification/traffic"
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(test_case['data']).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                print(f"✅ Status: {response.getcode()}")
                print(f"\n📊 Results:")
                print(f"  - Estimated CPC: ${result.get('estimated_cpc', 0):.2f}")
                print(f"  - Estimated Clicks: {result.get('estimated_clicks', 0):,}")
                print(f"  - Confidence Score: {result.get('confidence_score', 0)}%")
                print(f"  - Trend: {result.get('search_volume_trend', 'Unknown')}")
                print(f"  - Channels: {', '.join(result.get('recommended_channels', []))}")
                
                # Display Google Trends data if available
                if result.get('trend_data'):
                    trend = result['trend_data']
                    print(f"\n🌐 Google Trends Data:")
                    print(f"  - Data Source: {trend.get('data_source', 'Unknown')}")
                    print(f"  - Average Interest: {trend.get('average_interest', 0)}/100")
                    print(f"  - Current Interest: {trend.get('current_interest', 0)}/100")
                    print(f"  - Trending: {'Yes 🔥' if trend.get('is_trending') else 'No'}")
                    
                    if trend.get('data_source') == "Google Trends (Live)":
                        results.append(True)
                        print("  ✨ Using LIVE Google Trends data!")
                    else:
                        results.append(False)
                        print(f"  ⚠️  Fallback data: {trend.get('data_source', 'Unknown')}")
                else:
                    print("\n⚠️  No Google Trends data returned")
                    results.append(False)
                    
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            try:
                error_body = e.read().decode('utf-8')
                print(f"Error Details: {error_body[:300]}")
            except:
                pass
            results.append(False)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append(False)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 GOOGLE TRENDS INTEGRATION SUMMARY")
    print(f"{'='*60}")
    live_data_count = sum(results)
    total_tests = len(results)
    print(f"Tests with Live Google Trends Data: {live_data_count}/{total_tests}")
    
    if live_data_count > 0:
        print("\n✅ Google Trends integration is working!")
        print("The system is now using real market interest data.")
    else:
        print("\n⚠️  Google Trends integration is using fallback data.")
        print("Possible reasons:")
        print("  - Rate limiting (Google Trends free tier)")
        print("  - Network connectivity issues")
        print("  - Service temporarily unavailable")
        print("\nThe system will continue to work with mock data as fallback.")
    
    return live_data_count > 0

if __name__ == "__main__":
    success = test_google_trends_integration()
    sys.exit(0 if success else 1)
