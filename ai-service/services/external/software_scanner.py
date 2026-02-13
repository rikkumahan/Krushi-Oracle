"""
Software Scanner Service - Specialized validation for software startups
Analyzes GitHub repositories and NPM packages to gauge developer interest and library saturation.
"""

import httpx
import logging
from typing import Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class SoftwareScannerService:
    """
    Scans GitHub and NPM for technical signals.
    Provides data on repository counts, star averages, and package popularity.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def scan_market(self, primary_keyword: str) -> Dict:
        """
        Run a full technical scan for a software keyword.
        """
        logger.info(f"Scanning software market for: {primary_keyword}")
        
        # Run scans in parallel
        github_task = self._get_github_signals(primary_keyword)
        npm_task = self._get_npm_signals(primary_keyword)
        
        github_data, npm_data = await asyncio.gather(github_task, npm_task)
        
        # Calculate specialized technical score (0-100)
        tech_score = self._calculate_tech_score(github_data, npm_data)
        
        return {
            "tech_score": tech_score,
            "github": github_data,
            "npm": npm_data,
            "data_source": "Technical Matrix (GitHub + NPM)"
        }

    async def _get_github_signals(self, keyword: str) -> Dict:
        """Fetch repository count and engagement from GitHub"""
        url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page=1"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    total_count = data.get("total_count", 0)
                    
                    # High count = High saturation or high interest. 
                    # We treat >10k as "High Saturated", 1k-10k as "Growing", <1k as "Blue Ocean"
                    saturation = "High" if total_count > 10000 else "Medium" if total_count > 1000 else "Low"
                    
                    return {
                        "repo_count": total_count,
                        "saturation": saturation,
                        "status": "success"
                    }
                return self._mock_github(keyword)
        except Exception as e:
            logger.error(f"GitHub scan error: {e}")
            return self._mock_github(keyword)

    async def _get_npm_signals(self, keyword: str) -> Dict:
        """Fetch package popularity from NPM"""
        url = f"https://registry.npmjs.org/-/v1/search?text={keyword}&size=5"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    objects = data.get("objects", [])
                    
                    # Sum up popularity of top 5 packages
                    total_popularity = sum([obj.get("score", {}).get("detail", {}).get("popularity", 0) for obj in objects])
                    avg_popularity = (total_popularity / len(objects) * 100) if objects else 0
                    
                    return {
                        "package_count": data.get("total", 0),
                        "avg_popularity": int(avg_popularity),
                        "status": "success"
                    }
                return self._mock_npm(keyword)
        except Exception as e:
            logger.error(f"NPM scan error: {e}")
            return self._mock_npm(keyword)

    def _calculate_tech_score(self, github: Dict, npm: Dict) -> int:
        """Combine signals into a 0-100 technical interest score"""
        # We favor growing popularity (NPM) over pure repo count (GitHub)
        github_val = min(github.get("repo_count", 0) / 100, 50)  # Caps at 50 points
        npm_val = min(npm.get("avg_popularity", 0) / 2, 50)     # Caps at 50 points
        
        return int(github_val + npm_val)

    def _mock_github(self, keyword: str) -> Dict:
        return {"repo_count": 450, "saturation": "Low", "status": "mock"}

    def _mock_npm(self, keyword: str) -> Dict:
        return {"package_count": 12, "avg_popularity": 65, "status": "mock"}
