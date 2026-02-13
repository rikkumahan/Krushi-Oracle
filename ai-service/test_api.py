"""
API Test Script - Nova AI Service V2
Tests all endpoints to verify configuration and functionality
"""

import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, method, endpoint, data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            with urllib.request.urlopen(url) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"✅ Status: {response.getcode()}")
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
        
        elif method == "POST":
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"✅ Status: {response.getcode()}")
                print(f"Response Preview: {json.dumps(result, indent=2)[:500]}...")
                return True
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error Details: {error_body[:500]}")
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         Nova AI Service V2 - API Test Suite              ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Test 1: Health Check
    results.append(test_endpoint(
        "Health Check",
        "GET",
        "/health"
    ))
    
    # Test 2: Root Endpoint
    results.append(test_endpoint(
        "Root Endpoint",
        "GET",
        "/"
    ))
    
    # Test 3: Unit Economics
    results.append(test_endpoint(
        "Unit Economics Verification",
        "POST",
        "/api/v2/verification/economics",
        {
            "cac": 100.0,
            "arpu": 50.0,
            "churn_rate": 0.05,
            "sector": "SaaS"
        }
    ))
    
    # Test 4: Tech Feasibility (using query params)
    feasibility_params = urllib.parse.urlencode({
        'idea_name': 'AI Code Assistant',
        'description': 'An AI-powered VS Code extension that helps developers write better code'
    })
    results.append(test_endpoint(
        "Tech Feasibility Analysis",
        "POST",
        f"/api/v2/verification/feasibility?{feasibility_params}"
    ))
    
    # Test 5: Traffic Estimation
    results.append(test_endpoint(
        "Traffic Estimation",
        "POST",
        "/api/v2/verification/traffic",
        {
            "keyword": "project management software",
            "budget": 1000.0,
            "platform": "Google Ads"
        }
    ))
    
    # Test 6: Idea Generation (Main Feature)
    results.append(test_endpoint(
        "Idea Generation",
        "POST",
        "/api/ideas/generate",
        {
            "wizard_input": {
                "industry": "SaaS",
                "target_audience": "Small businesses",
                "skill_level": "intermediate",
                "budget": 5000,
                "time_frame": "3_months",
                "interests": "AI and automation",
                "location": "United States"
            },
            "num_ideas": 3,
            "contrarian_override": False
        }
    ))
    
    # Test 7: Landing Page Generation
    results.append(test_endpoint(
        "Landing Page Generator",
        "POST",
        "/api/v2/assets/landing-page",
        {
            "idea_name": "TaskMaster Pro",
            "tagline": "Project management made simple",
            "description": "An AI-powered project management tool for small teams",
            "target_audience": "Small business owners",
            "features": [
                "AI task prioritization",
                "Team collaboration",
                "Real-time updates"
            ],
            "style_preference": "Modern SaaS"
        }
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ All tests passed! Your API is fully configured.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Common issues:")
        print("   - Missing OPENAI_API_KEY in .env file")
        print("   - Invalid API key or insufficient credits")
        print("   - Server not running on port 8000")
        sys.exit(1)

if __name__ == "__main__":
    main()
