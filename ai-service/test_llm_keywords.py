"""
LLM-Powered Keyword Extraction + Google Trends Integration Test
Tests the intelligent traffic estimation with automatic keyword generation
"""

import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_llm_keyword_trends():
    """Test LLM keyword extraction + multi-keyword Google Trends analysis"""
    print("="*70)
    print("🧠 Testing LLM-Powered Keyword Extraction + Google Trends")
    print("="*70)
    
    test_cases = [
        {
            "name": "AI Code Assistant",
            "data": {
                "idea_name": "CodeWhisperer Pro",
                "idea_description": "An AI-powered VS Code extension that helps developers write better code by providing intelligent suggestions, bug detection, and automated refactoring",
                "industry": "AI Tools",
                "target_audience": "Software developers",
                "budget": 2000.0
            }
        },
        {
            "name": "Project Management SaaS",
            "data": {
                "idea_name": "TaskFlow",
                "idea_description": "A project management platform for remote teams with real-time collaboration, Gantt charts, and AI-powered task prioritization",
                "industry": "SaaS",
                "target_audience": "Remote teams and startups",
                "budget": 3000.0
            }
        },
        {
            "name": "E-learning Platform",
            "data": {
                "idea_name": "LearnHub",
                "idea_description": "An interactive e-learning platform for K-12 students with gamification, progress tracking, and personalized learning paths",
                "industry": "EdTech",
                "target_audience": "Parents and students",
                "budget": 1500.0
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'═'*70}")
        print(f"💡 Idea: {test_case['name']}")
        print(f"Description: {test_case['data']['idea_description'][:80]}...")
        print(f"{'═'*70}")
        
        try:
            url = f"{BASE_URL}/api/v2/verification/traffic"
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(test_case['data']).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                print(f"\n✅ Status: {response.getcode()}")
                
                # Display extracted keywords
                keywords_analyzed = result.get('keywords_analyzed', [])
                print(f"\n🔍 Keywords Extracted (LLM):")
                for i, keyword in enumerate(keywords_analyzed, 1):
                    print(f"  {i}. \"{keyword}\"")
                
                # Display traffic estimate
                print(f"\n📊 Traffic Estimate:")
                print(f"  - Estimated CPC: ${result.get('estimated_cpc', 0):.2f}")
                print(f"  - Estimated Clicks: {result.get('estimated_clicks', 0):,}")
                print(f"  - Confidence Score: {result.get('confidence_score', 0)}%")
                print(f"  - Market Trend: {result.get('search_volume_trend', 'Unknown')}")
                
                # Display aggregated trend insights
                insights = result.get('trend_insights', {})
                if insights:
                    print(f"\n🌐 Multi-Keyword Trend Analysis:")
                    print(f"  - Average Market Interest: {insights.get('average_market_interest', 0)}/100")
                    print(f"  - Has Trending Keyword: {'Yes 🔥' if insights.get('has_trending_keyword') else 'No'}")
                    print(f"  - Data Quality: {insights.get('data_quality', 'Unknown').upper()}")
                    print(f"  - Live Data: {insights.get('live_data_percentage', 0)}%")
                    
                    # Show per-keyword breakdown
                    keywords_data = insights.get('keywords_data', [])
                    if keywords_data:
                        print(f"\n  📈 Per-Keyword Breakdown:")
                        for kwd in keywords_data:
                            trend_emoji = "📈" if kwd['trend'] == "Rising" else "📉" if kwd['trend'] == "Declining" else "➡️"
                            data_source_indicator = "🟢" if "Live" in kwd['data_source'] else "🟡"
                            print(f"    {data_source_indicator} {trend_emoji} \"{kwd['keyword']}\": {kwd['current_interest']}/100 ({kwd['trend']})")
                    
                    # Determine success
                    if insights.get('data_quality') == 'live':
                        results.append(True)
                        print("\n  ✨ Using LIVE Google Trends data with LLM keyword extraction!")
                    else:
                        results.append(False)
                        print(f"\n  ⚠️  Using fallback data")
                else:
                    print("\n⚠️  No trend insights returned")
                    results.append(False)
                    
        except urllib.error.HTTPError as e:
            print(f"\n❌ HTTP Error {e.code}: {e.reason}")
            try:
                error_body = e.read().decode('utf-8')
                print(f"Error Details: {error_body[:400]}")
            except:
                pass
            results.append(False)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 LLM + GOOGLE TRENDS INTEGRATION SUMMARY")
    print(f"{'='*70}")
    live_data_count = sum(results)
    total_tests = len(results)
    print(f"Tests with Live Data: {live_data_count}/{total_tests}")
    
    if live_data_count > 0:
        print("\n✅ LLM + Google Trends integration is working!")
        print("   - Keywords are automatically extracted from idea descriptions")
        print("   - Multiple keywords are analyzed for comprehensive insights")
        print("   - Real market trends are used for validation")
    else:
        print("\n⚠️  Integration is using fallback data.")
        print("   System will continue to work with mock data.")
    
    return live_data_count > 0

if __name__ == "__main__":
    success = test_llm_keyword_trends()
    sys.exit(0 if success else 1)
