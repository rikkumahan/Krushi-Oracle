
import requests
import json

url = "http://localhost:8000/api/ideas/generate"
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

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
