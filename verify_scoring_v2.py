
import requests
import json

# URL for the V2 Scoring Endpoint (Python Service)
url = "http://127.0.0.1:8002/api/v2/score-idea"

# Comprehensive payload matching IdeaScoreRequest model
payload = {
    "idea_name": "AI Meal Planner for Busy Professionals",
    "idea_description": "Personalized meal plans with grocery lists and recipe videos using generative AI.",
    "target_market": "Busy professionals aged 25-45 in urban areas",
    
    # Market Signals
    "monthly_searches": 25000,
    "growth_rate_30d": 0.15,
    "youtube_video_count": 350,
    "youtube_total_views": 1800000,
    "reddit_post_count": 120,
    "reddit_total_score": 2400,
    
    # News Signals
    "wikipedia_daily_views": 850,
    "news_articles_30d": 45,
    "news_unique_sources": 12,
    
    # Competitive Data
    "competitor_count": 25,
    "top_player_market_shares": [30, 20, 15, 10, 5],
    "new_entrants_12m": 8,
    "exits_12m": 3,
    "substitute_count": 12,
    
    # Tech Stack
    "tech_stack": {
        "technologies": ["Next.js", "FastAPI", "PostgreSQL", "Prisma", "Vercel"],
        "team_experience": {
            "Next.js": "FAMILIAR",
            "FastAPI": "FAMILIAR",
            "PostgreSQL": "BEGINNER",
            "Prisma": "FAMILIAR",
            "Vercel": "EXPERT"
        }
    },
    
    # Capital
    "estimated_capital_needed": 150000
}

headers = {
    "Content-Type": "application/json"
}

print(f"🚀 Testing V2 Scoring Engine at {url}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS! Scoring Engine V2 is Working.")
        print(f"MVS Score: {data['mvs_score']}/100 ({data['mvs_grade']})")
        print(f"Validation Class: {data['validation_class']}")
        print("\nDimension Scores:")
        for dim, score in data['dimension_scores'].items():
            print(f"  - {dim.capitalize()}: {score}")
        print("\nRecommendations:")
        for rec in data['recommendations'][:3]:
            print(f"  - {rec}")
    else:
        print(f"❌ FAILED: {response.text}")

except Exception as e:
    print(f"Error: {e}")
