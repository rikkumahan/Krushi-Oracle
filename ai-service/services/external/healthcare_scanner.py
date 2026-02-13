"""
Healthcare Scanner Service - Specialized validation for healthcare and biotech startups
Analyzes clinical trials data to gauge research intensity and therapy category competition.
"""

import httpx
import logging
from typing import Dict, List, Optional
import asyncio

logger = logging.getLogger(__name__)

class HealthcareScannerService:
    """
    Scans ClinicalTrials.gov for medical/biotech signals.
    Provides data on trial counts and therapy area density.
    """
    
    def __init__(self):
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def scan_market(self, primary_keyword: str) -> Dict:
        """
        Run a healthcare sector scan.
        """
        logger.info(f"Scanning healthcare market for: {primary_keyword}")
        
        trial_data = await self._get_clinical_trials(primary_keyword)
        
        # Calculate specialized medical interest score
        medical_score = self._calculate_medical_score(trial_data)
        
        return {
            "medical_score": medical_score,
            "clinical_trials": trial_data,
            "data_source": "Healthcare Matrix (ClinicalTrials.gov)"
        }

    async def _get_clinical_trials(self, keyword: str) -> Dict:
        """Fetch trial counts from ClinicalTrials.gov"""
        # API V2 endpoint for studies
        url = f"https://clinicaltrials.gov/api/v2/studies?query.cond={keyword}&pageSize=1"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    total_count = data.get("totalCount", 0)
                    
                    # High count = High specialized interest and validation
                    density = "High" if total_count > 500 else "Medium" if total_count > 50 else "Low"
                    
                    return {
                        "trial_count": total_count,
                        "density": density,
                        "status": "success"
                    }
                return self._mock_healthcare(keyword)
        except Exception as e:
            logger.error(f"Healthcare scan error: {e}")
            return self._mock_healthcare(keyword)

    def _calculate_medical_score(self, trials: Dict) -> int:
        """Combine signals into a 0-100 medical interest score"""
        # We treat medical interest as a proxy for market size/validation
        # 100+ trials is a very strong therapy area
        count = trials.get("trial_count", 0)
        score = min(count * 2, 100) if count > 0 else 50
        
        return int(score)

    def _mock_healthcare(self, keyword: str) -> Dict:
        return {"trial_count": 8, "density": "Low", "status": "mock"}
