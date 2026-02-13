"""
Configuration Loader Utilities

Helper functions to load JSON configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from functools import lru_cache


# Get config directory path (relative to this file)
CONFIG_DIR = Path(__file__).parent.parent / "config"


@lru_cache(maxsize=None)
def load_industry_assumptions() -> Dict[str, Any]:
    """
    Load industry-specific assumptions for TAM/SAM/SOM calculations.
    
    Returns dict with structure:
    {
        "saas": {"conversion_rate": 0.03, "arpu_annual": 100, ...},
        "ecommerce": {...},
        ...
    }
    """
    config_path = CONFIG_DIR / "industry_assumptions.json"
    
    if not config_path.exists():
        # Fallback to defaults if file missing
        return {
            "default": {
                "conversion_rate": 0.10,
                "arpu_annual": 50,
                "description": "Default conservative estimates"
            }
        }
    
    with open(config_path, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load_tech_stack_db() -> Dict[str, Any]:
    """
    Load technology stack database.
    
    Returns dict with structure:
    {
        "frontend": {"React": {...}, "Vue": {...}},
        "backend": {...},
        ...
    }
    """
    config_path = CONFIG_DIR / "tech_stack_db.json"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load_tech_interactions() -> Dict[str, Any]:
    """
    Load technology interaction matrix (synergies and conflicts).
    
    Returns dict with structure:
    {
        "synergies": [...],
        "conflicts": [...]
    }
    """
    config_path = CONFIG_DIR / "tech_interactions.json"
    
    if not config_path.exists():
        return {"synergies": [], "conflicts": []}
    
    with open(config_path, 'r') as f:
        return json.load(f)


def get_industry_assumptions(industry: str = "default") -> Dict[str, float]:
    """
    Get assumptions for a specific industry.
    
    Args:
        industry: Industry type (saas, ecommerce, consumer_app, marketplace, default)
    
    Returns:
        Dict with conversion_rate and arpu_annual
    """
    all_assumptions = load_industry_assumptions()
    
    # Normalize industry name
    industry_key = industry.lower().replace(" ", "_").replace("-", "_")
    
    # Return industry-specific or default
    return all_assumptions.get(industry_key, all_assumptions.get("default", {
        "conversion_rate": 0.10,
        "arpu_annual": 50
    }))


# Clear cache function (useful for testing or hot-reload)
def clear_config_cache():
    """Clear all cached configurations"""
    load_industry_assumptions.cache_clear()
    load_tech_stack_db.cache_clear()
    load_tech_interactions.cache_clear()
