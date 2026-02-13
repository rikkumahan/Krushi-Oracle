"""Simple test to check if the traffic endpoint is working at all"""
import urllib.request
import json

url = "http://127.0.0.1:8000/api/v2/verification/traffic"
data = {
    "idea_name": "Test Idea",
    "idea_description": "A simple test",
    "industry": "SaaS",
    "target_audience": "Everyone", 
    "budget": 1000.0
}

headers = {'Content-Type': 'application/json'}
json_data = json.dumps(data).encode('utf-8')
req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("SUCCESS!")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
