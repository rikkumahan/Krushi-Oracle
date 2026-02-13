"""Test with provided keywords to bypass LLM extraction"""
import urllib.request
import json

url = "http://127.0.0.1:8000/api/v2/verification/traffic"
data = {
    "idea_name": "Test Idea",
    "idea_description": "A simple test",
    "industry": "SaaS",
    "target_audience": "Everyone",
    "budget": 1000.0,
    "keywords": ["saas software", "project management", "cloud tools"]  # Provide keywords manually
}

headers = {'Content-Type': 'application/json'}
json_data = json.dumps(data).encode('utf-8')
req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req, timeout=45) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("✅ SUCCESS!")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
