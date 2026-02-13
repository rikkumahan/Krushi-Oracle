"""
Keyword Extraction Service - LLM-powered keyword generation
Extracts relevant search keywords from idea descriptions for market research
"""

import httpx
import json
from typing import List, Dict
from pydantic import BaseModel

from utils.openai_helper import get_openai_client, get_model_name
import logging

logger = logging.getLogger(__name__)

class KeywordExtractionRequest(BaseModel):
    idea_name: str
    idea_description: str
    industry: str
    target_audience: str
    num_keywords: int = 5

class KeywordExtractionResponse(BaseModel):
    primary_keywords: List[str]
    related_keywords: List[str]
    reasoning: str

class KeywordExtractorService:
    """
    Uses OpenAI (or Azure) to extract relevant search keywords from idea descriptions.
    These keywords are then used for Google Trends analysis.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key # Manual override if needed
        self.model = model
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = get_openai_client()
        return self._client

    def _get_model(self):
        return self.model or get_model_name()
    
    async def extract_keywords(self, request: KeywordExtractionRequest) -> KeywordExtractionResponse:
        """
        Extract search keywords that potential customers would use.
        
        Returns:
            - primary_keywords: Main keywords (3-5) for Google Trends
            - related_keywords: Secondary keywords for comparison
            - reasoning: Brief explanation of keyword selection
        """
        client = self._get_client()
        if not client:
            return self._mock_keywords(request)
        
        system_prompt = """You are a market research expert specializing in keyword analysis.
Your task is to identify the exact search terms that potential customers would use when looking for solutions in this space.

Focus on:
1. High-intent commercial keywords (what people search when ready to buy/use)
2. Natural language queries (how people actually search)
3. Competitor/category keywords (existing solutions in this space)
4. Problem-focused keywords (the pain point being solved)

Return ONLY valid JSON."""

        user_prompt = f"""
Idea: {request.idea_name}
Description: {request.idea_description}
Industry: {request.industry}
Target Audience: {request.target_audience}

Extract {request.num_keywords} primary search keywords that potential customers would use to find this solution.
Include both short-tail (1-2 words) and long-tail (3-4 words) keywords.

Return as JSON:
{{
  "primary_keywords": ["keyword1", "keyword2", ...],
  "related_keywords": ["related1", "related2", ...],
  "reasoning": "Brief explanation of why these keywords were chosen"
}}
"""
        
        try:
            response = client.chat.completions.create(
                model=self._get_model(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            return KeywordExtractionResponse(
                primary_keywords=data.get("primary_keywords", [])[:request.num_keywords],
                related_keywords=data.get("related_keywords", [])[:5],
                reasoning=data.get("reasoning", "Keywords extracted based on idea analysis")
            )
                
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return self._mock_keywords(request)
                
        except Exception as e:
            print(f"Keyword extraction error: {e}")
            return self._mock_keywords(request)
    
    def _mock_keywords(self, request: KeywordExtractionRequest) -> KeywordExtractionResponse:
        """Fallback keywords when API is unavailable"""
        # Simple heuristic-based extraction
        industry_lower = request.industry.lower()
        
        primary = [
            f"{industry_lower} software",
            request.idea_name.lower(),
            f"{industry_lower} tool"
        ]
        
        related = [
            f"best {industry_lower} solution",
            f"{request.target_audience.lower()} {industry_lower}"
        ]
        
        return KeywordExtractionResponse(
            primary_keywords=primary[:request.num_keywords],
            related_keywords=related,
            reasoning="Mock keywords (API key not configured)"
        )
