import httpx
import asyncio
import json

async def test_all():
    timeout = httpx.Timeout(120.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        
        # 1. Test Canvas
        print("\n--- Testing Canvas Generator ---")
        canvas_payload = {
            "id": "test-idea-123",
            "name": "Test Idea",
            "tagline": "Test tagline",
            "description": "A platform for testing AI services",
            "target_customer": "Developers",
            "problem": "Testing is hard",
            "solution": "Automated testing",
            "business_model": {
                "revenue_streams": ["Subscription"], 
                "pricing_model": "SaaS",
                "channels": ["Direct Sales", "SEO"],
                "customer_segments": ["Developers", "Startups"],
                "key_partners": ["Cloud Providers", "Accelerators"],
                "cost_structure": ["Server Costs", "Salaries"],
                "value_proposition": "We help developers test AI services faster."
            },
            "mvp_features": [{"name": "Feature 1", "description": "Desc 1", "priority": 1}]
        }
        try:
            resp = await client.post("http://localhost:8000/api/grounded/canvas/generate", json=canvas_payload)
            print(f"Canvas Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Canvas Error: {resp.text[:500]}")
        except Exception as e:
            print(f"Canvas Exception: {e}")

        # 2. Test Pitch Deck
        print("\n--- Testing Pitch Deck Generator ---")
        # Pitch deck uses same input schema as Canvas (StartupIdea)
        try:
            resp = await client.post("http://localhost:8000/api/grounded/pitch/generate", json=canvas_payload)
            print(f"Pitch Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Pitch Error: {resp.text[:500]}")
        except Exception as e:
            print(f"Pitch Exception: {e}")

        # 3. Test Idea Generator
        print("\n--- Testing Idea Generator ---")
        idea_payload = {
            "wizard_input": {
                "industry": "SaaS",
                "target_audience": "Small Business",
                "problem_space": "Accounting",
                "budget": 5000,
                "skills": ["Coding", "Marketing"],
                "skill_level": "intermediate",
                "timeline": "3 months",
                "time_frame": "3_months"  # Ensure enum match
            },
            "num_ideas": 1,
            "contrarian_override": False
        }
        try:
            resp = await client.post("http://localhost:8000/api/grounded/ideas/generate", json=idea_payload)
            print(f"Idea Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Idea Error: {resp.text[:500]}")
        except Exception as e:
            print(f"Idea Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_all())
