import httpx
import asyncio
import json

async def test_canvas():
    """Test canvas generator endpoint"""
    payload = {
        "id": "test-idea-123",  # Added ID
        "name": "Test Idea",
        "tagline": "Test tagline",
        "description": "A platform for testing AI services",
        "target_market": "Developers",
        "problem": "Testing is hard",
        "solution": "Automated testing",
        "business_model": {
            "revenue_streams": ["Subscription"], 
            "pricing_model": "SaaS",
            "channels": ["Direct Sales", "SEO"],
            "customer_segments": ["Developers", "Startups"],
            "key_partners": ["Cloud Providers", "Accelerators"],
            "cost_structure": ["Server Costs", "Salaries"],
            "value_proposition": "We help developers test AI services faster."  # Added value proposition
        },
        "mvp_features": [{"name": "Feature 1", "description": "Desc 1", "priority": 1}]  # Added priority as int
    }
    
    print(f"Testing Canvas Generator...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/grounded/canvas/generate",
                json=payload
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success!")
                print(f"Response keys: {response.json().keys()}")
            else:
                print(f"❌ Failed: {response.text}")
            
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_canvas())
