import httpx
import asyncio
import json

async def test_landing_page():
    """Test landing page endpoint and print detailed error"""
    payload = {
        "idea_name": "Test",
        "tagline": "Test tagline",
        "description": "Test description",
        "target_audience": "Test audience",
        "features": ["Feature 1"]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/grounded/landing-page/generate",
                json=payload
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_landing_page())
