
import requests
import json

# Call the JAVA backend on port 8080
url = "http://localhost:8080/api/ideas/generate"
payload = {
    "wizard_input": {
        "industry": "SaaS",
        "target_audience": "Developers",
        "skill_level": "beginner",
        "budget": 5000,
        "time_frame": "1_month"
    },
    "num_ideas": 5,
    "contrarian_override": False
}
headers = {
    "Content-Type": "application/json"
}

print(f"Calling Java Gateway at {url}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ SUCCESS! Java gateway successfully calling Python service.")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"Error: {e}")
