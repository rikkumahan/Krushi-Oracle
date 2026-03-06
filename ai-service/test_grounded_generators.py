"""
Test script for grounded generators.
Verifies all 4 generators are properly wired and functional.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_grounded_idea_generator():
    """Test grounded idea generator"""
    print("\n🧪 Testing Grounded Idea Generator...")
    
    payload = {
        "wizard_input": {
            "industry": "SaaS",
            "target_audience": "Small businesses",
            "skill_level": "intermediate",
            "budget": 50000,
            "time_frame": "6_months"
        },
        "num_ideas": 3,
        "contrarian_override": False
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/grounded/ideas/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Generated {len(data['ideas'])} validated ideas")
                print(f"   Validation rate: {data.get('metadata', {}).get('validation_rate', 0):.1f}%")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def test_grounded_landing_page():
    """Test grounded landing page generator"""
    print("\n🧪 Testing Grounded Landing Page Generator...")
    
    payload = {
        "idea_name": "TaskFlow",
        "tagline": "Project management for small teams",
        "description": "Simple project management tool for small businesses",
        "target_audience": "Small businesses",
        "features": ["Task tracking", "Team collaboration", "Time tracking"]
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/grounded/landing-page/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Generated landing page with {len(data.get('validation_sources', {}))} validation sources")
                print(f"   HTML length: {len(data.get('html_content', ''))} chars")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def test_grounded_canvas():
    """Test grounded canvas generator"""
    print("\n🧪 Testing Grounded Canvas Generator...")
    
    payload = {
        "id": "test-123",
        "name": "TaskFlow",
        "tagline": "Project management for small teams",
        "description": "Simple project management tool for small businesses",
        "target_customer": "Small businesses",
        "problem_solved": "Inefficient project tracking",
        "estimated_initial_cost": 50000,
        "mvp_features": [],
        "business_model": {
            "revenue_streams": ["Subscription"],
            "key_partners": ["Cloud providers", "Payment processors"],
            "cost_structure": ["Development", "Marketing", "Infrastructure"],
            "value_proposition": "Simple project management for small teams",
            "customer_segments": ["Small businesses", "Startups"],
            "channels": ["Web", "Mobile app", "Email marketing"]
        }
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/grounded/canvas/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                canvas = data.get('canvas', {})
                coverage = data.get('data_coverage', 0)
                print(f"✅ Generated canvas with {len(canvas)} sections")
                print(f"   Data coverage: {coverage:.0f}%")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def test_grounded_pitch():
    """Test grounded pitch deck generator"""
    print("\n🧪 Testing Grounded Pitch Deck Generator...")
    
    payload = {
        "id": "test-123",
        "name": "TaskFlow",
        "tagline": "Project management for small teams",
        "description": "Simple project management tool for small businesses",
        "target_customer": "Small businesses",
        "problem_solved": "Inefficient project tracking",
        "estimated_initial_cost": 50000,
        "mvp_features": [],
        "business_model": {
            "revenue_streams": ["Subscription"],
            "key_partners": ["Cloud providers", "Payment processors"],
            "cost_structure": ["Development", "Marketing", "Infrastructure"],
            "value_proposition": "Simple project management for small teams",
            "customer_segments": ["Small businesses", "Startups"],
            "channels": ["Web", "Mobile app", "Email marketing"]
        }
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/grounded/pitch/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                slides = data.get('slides', [])
                validation = data.get('validation_report', {})
                print(f"✅ Generated pitch with {len(slides)} slides")
                print(f"   Validation rate: {validation.get('validation_rate', 0):.0f}%")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Grounded Generators Test Suite")
    print("=" * 60)
    
    results = {
        "Idea Generator": await test_grounded_idea_generator(),
        "Landing Page": await test_grounded_landing_page(),
        "Canvas Generator": await test_grounded_canvas(),
        "Pitch Deck": await test_grounded_pitch()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")

if __name__ == "__main__":
    asyncio.run(main())
