"""
Domain Defaults Configuration
Centralized source of truth for industry-specific benchmarks.
Used to ground generators in realistic data when live data is unavailable.
"""

from typing import Dict, Any, List

# Default fallback if industry is unknown
DEFAULT_INDUSTRY_CONFIG = {
    "cpc": 2.50,
    "gross_margin": 0.50,
    "arpu_monthly": 30.0,
    "churn_rate": 0.05,
    "conversion_rate": 0.02,
    "traffic_channels": ["Google Search", "Facebook", "Instagram"],
    "keywords_context": ["business", "service", "product"]
}

DOMAIN_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "saas": {
        "cpc": 5.00, 
        "gross_margin": 0.80,
        "arpu_monthly": 50.0,
        "churn_rate": 0.05,
        "conversion_rate": 0.02,
        "traffic_channels": ["LinkedIn", "Google Search", "Twitter"],
        "keywords_context": ["software", "automation", "platform"]
    },
    "fintech": {
        "cpc": 8.50,
        "gross_margin": 0.65,
        "arpu_monthly": 20.0,
        "churn_rate": 0.04,
        "conversion_rate": 0.03,
        "traffic_channels": ["Google Search", "Affiliate", "Finance Blogs"],
        "keywords_context": ["investing", "finance", "money"]
    },
    "edtech": {
        "cpc": 3.20,
        "gross_margin": 0.70,
        "arpu_monthly": 200.0, # One-time courses often, or monthly
        "churn_rate": 0.08,
        "conversion_rate": 0.025,
        "traffic_channels": ["Facebook", "YouTube", "Instagram"],
        "keywords_context": ["course", "learning", "skills"]
    },
    "ecommerce": {
        "cpc": 1.10,
        "gross_margin": 0.45,
        "arpu_monthly": 60.0, # Average Order Value
        "churn_rate": 0.0, # N/A for transactional, effectively 100% re-acquisition
        "conversion_rate": 0.03,
        "traffic_channels": ["Instagram", "Google Shopping", "TikTok"],
        "keywords_context": ["buy", "shop", "store"]
    },
    "marketplace": {
        "cpc": 1.50,
        "gross_margin": 0.20, # Take rate
        "arpu_monthly": 15.0, # Commission per user
        "churn_rate": 0.10,
        "conversion_rate": 0.02,
        "traffic_channels": ["Google Search", "Social Media", "Referral"],
        "keywords_context": ["connect", "find", "hire"]
    },
    "healthtech": {
        "cpc": 4.50,
        "gross_margin": 0.60,
        "arpu_monthly": 40.0,
        "churn_rate": 0.06,
        "conversion_rate": 0.02,
        "traffic_channels": ["Google Search", "Facebook", "Health Forums"],
        "keywords_context": ["health", "care", "wellness"]
    },
    "ai tools": {
        "cpc": 2.50,
        "gross_margin": 0.75,
        "arpu_monthly": 25.0,
        "churn_rate": 0.07,
        "conversion_rate": 0.02,
        "traffic_channels": ["Twitter", "ProductHunt", "Reddit"],
        "keywords_context": ["ai", "generator", "tool"]
    },
    "b2b services": {
        "cpc": 6.00,
        "gross_margin": 0.50,
        "arpu_monthly": 1000.0,
        "churn_rate": 0.02,
        "conversion_rate": 0.01,
        "traffic_channels": ["LinkedIn", "Email", "Clutch"],
        "keywords_context": ["agency", "consulting", "service"]
    },
    "hardware": {
        "cpc": 2.00,
        "gross_margin": 0.40,
        "arpu_monthly": 200.0, # Unit price
        "churn_rate": 0.0,
        "conversion_rate": 0.015,
        "traffic_channels": ["YouTube", "TechRadar", "Unboxing Videos"],
        "keywords_context": ["device", "gadget", "smart"]
    },
    "mobile app": {
        "cpc": 0.80,
        "gross_margin": 0.70, # App store takes 30%
        "arpu_monthly": 5.0,
        "churn_rate": 0.15,
        "conversion_rate": 0.05, # App store conversion
        "traffic_channels": ["App Store Ads", "Instagram", "TikTok"],
        "keywords_context": ["app", "mobile", "ios"]
    },
    "content/media": {
        "cpc": 0.50,
        "gross_margin": 0.90,
        "arpu_monthly": 0.50, # Ads revenue per user
        "churn_rate": 0.20,
        "conversion_rate": 0.10, # Visit to subscriber
        "traffic_channels": ["Social Media", "SEO", "Newsletter"],
        "keywords_context": ["blog", "news", "video"]
    },
    "real estate": {
        "cpc": 10.00,
        "gross_margin": 0.90, # Agent commission margin
        "arpu_monthly": 5000.0, # Transaction fee
        "churn_rate": 0.0,
        "conversion_rate": 0.005,
        "traffic_channels": ["Zillow", "Google Search", "Facebook"],
        "keywords_context": ["home", "property", "buy"]
    }
}

def get_domain_config(industry: str) -> Dict[str, Any]:
    """
    Get benchmarks for a specific industry.
    Performs fuzzy matching to find the best fit.
    """
    if not industry:
        return DEFAULT_INDUSTRY_CONFIG
        
    key = industry.lower()
    
    # Exact match check
    if key in DOMAIN_BENCHMARKS:
        return DOMAIN_BENCHMARKS[key]
        
    # Substring match
    for benchmark_key, config in DOMAIN_BENCHMARKS.items():
        if benchmark_key in key or key in benchmark_key:
            return config
            
    # Category mapping fallback
    mappings = {
        "retail": "ecommerce",
        "construction": "b2b services",
        "consulting": "b2b services",
        "automotive": "hardware",
        "food": "ecommerce", # Rough proxy for D2C/Restaurant
        "education": "edtech"
    }
    
    for map_key, map_target in mappings.items():
        if map_key in key:
            return DOMAIN_BENCHMARKS.get(map_target, DEFAULT_INDUSTRY_CONFIG)
            
    return DEFAULT_INDUSTRY_CONFIG
