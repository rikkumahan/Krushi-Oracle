import requests
from typing import List, Dict
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ProductHuntSearcher:
    """Searches Product Hunt for similar startups"""
    
    def __init__(self):
        self.api_key = os.getenv("PRODUCTHUNT_API_TOKEN")
        self.base_url = "https://api.producthunt.com/v2/api/graphql"
    
    def search_companies(self, keywords: List[str], limit: int = 10) -> List[Dict]:
        """Search Product Hunt for similar products using GraphQL API"""
        
        if not self.api_key:
            print("WARNING: PRODUCTHUNT_API_TOKEN not found in environment. Using mock results.")
            return self._get_mock_results(keywords, limit)

    def _get_mock_results(self, keywords: List[str], limit: int) -> List[Dict]:
        """Return deterministic mock results when API key is missing"""
        mock_data = [
            {"name": "EnergyWise", "tagline": "AI home energy savings", "description": "Intelligent thermostat control.", "website": "https://energywise.example.com", "createdAt": "2021-01-01T00:00:00Z", "votesCount": 450},
            {"name": "PowerSync", "tagline": "Grid optimization for home", "description": "Manage appliance power cycles.", "website": "https://powersync.example.com", "createdAt": "2022-05-12T00:00:00Z", "votesCount": 1200},
            {"name": "GreenMeter", "tagline": "Realtime usage tracking", "description": "Visualize your energy waste.", "website": "https://greenmeter.example.com", "createdAt": "2020-11-20T00:00:00Z", "votesCount": 890},
            {"name": "EcoHub", "tagline": "Smart energy dashboard", "description": "One place to manage everything.", "website": "https://ecohub.example.com", "createdAt": "2023-02-14T00:00:00Z", "votesCount": 2100}
        ]
        
        results = []
        for i, mock in enumerate(mock_data[:limit]):
            results.append({
                "name": mock["name"],
                "description": mock["tagline"] + " " + mock["description"],
                "url": mock["website"],
                "source": "producthunt",
                "metadata": {
                    "upvotes": mock["votesCount"],
                    "launch_date": mock["createdAt"],
                    "topics": ["Energy", "Smart Home", "AI"]
                }
            })
        return results
            
        results = []
        
        # We search for each keyword to maximize breadth
        for keyword in keywords:
            query = """
            query($search: String!) {
              posts(first: 5, searchQuery: $search) {
                edges {
                  node {
                    name
                    tagline
                    description
                    votesCount
                    createdAt
                    website
                    topics {
                        name
                    }
                  }
                }
              }
            }
            """
            
            variables = {"search": keyword}
            
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"query": query, "variables": variables},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("posts", {}).get("edges", [])
                    
                    for post in posts:
                        node = post["node"]
                        results.append({
                            "name": node["name"],
                            "description": node.get("tagline", "") + " " + node.get("description", ""),
                            "url": node.get("website"),
                            "source": "producthunt",
                            "metadata": {
                                "upvotes": node.get("votesCount"),
                                "launch_date": node.get("createdAt"),
                                "topics": [t["name"] for t in node.get("topics", [])]
                            }
                        })
                else:
                    print(f"Product Hunt API error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error searching Product Hunt for '{keyword}': {e}")
        
        # Deduplicate by name (case-insensitive)
        seen = set()
        unique_results = []
        for r in results:
            name_lower = r["name"].lower().strip()
            if name_lower not in seen:
                seen.add(name_lower)
                unique_results.append(r)
        
        return unique_results[:limit]
