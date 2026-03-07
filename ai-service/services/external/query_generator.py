"""
Platform-Specific Query Generator Service
==========================================
Generates tailored search queries optimized for each external API's 'search culture'.

Why:
  Sending the same keyword to Reddit, YouTube, News, and Wikipedia is naive.
  Each platform has distinct search norms. One LLM call upfront generates 4
  distinct, high-yield queries, which are then dispatched in parallel.

Usage:
  query_gen = QueryGeneratorService()
  queries = await query_gen.generate("TaxOptAI", "B2B SaaS that uses AI...")
  # queries.reddit_query  -> "tired of manual tax reconciliation errors"
  # queries.youtube_query -> "best AI tax automation software 2024"
  # queries.news_query    -> "accounting tech startup AI tax compliance"
  # queries.wikipedia_query -> "Tax_software"
"""

import json
import asyncio
import logging
from pydantic import BaseModel
from typing import Optional

from utils.openai_helper import get_openai_client, get_model_name

logger = logging.getLogger(__name__)


class QuerySet(BaseModel):
    """Platform-specific search queries generated for a startup idea."""
    reddit_query: str
    youtube_query: str
    news_query: str
    wikipedia_query: str  # Must be an exact Wikipedia article title (e.g. "Tax_software")


class QueryGeneratorService:
    """
    One lightweight LLM call that generates 4 culture-aware search queries,
    one per external API platform.

    Downstream scrapers stay deterministic; all intelligence lives here.
    """

    _SYSTEM_PROMPT = """You are a search query expert for market research platforms. 
Given a startup idea, generate EXACTLY 4 search queries, one tailored to each platform below.

PLATFORM RULES:
- reddit_query: A raw, emotionally honest pain-point phrase that startup founders or professionals might search or post about. Sound like a frustrated human, not a marketer. Max 8 words.
- youtube_query: A tutorial, comparison or review-style search phrase. People search YouTube to learn or compare. Max 6 words.
- news_query: An industry/investment/trend phrase. Written like a Bloomberg or TechCrunch headline topic. Max 5 words.
- wikipedia_query: CRITICAL — This must be an EXACT Wikipedia article title (e.g. "Tax_software", "Machine_learning", "Accounting"). Use underscores for spaces. Short proper noun. This will be used as a URL path, so it MUST resolve to a real Wikipedia article.

Return ONLY valid JSON with these exact keys."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = get_openai_client()
        return self._client

    async def generate(
        self,
        idea_name: str,
        description: str,
        primary_keyword: Optional[str] = None
    ) -> QuerySet:
        """
        Generate platform-specific queries. Falls back gracefully if LLM fails.
        """
        client = self._get_client()
        fallback_kw = primary_keyword or idea_name.lower()

        if not client:
            return self._fallback(fallback_kw)

        user_prompt = f"""Startup Idea: {idea_name}
Description: {description}
Core Keyword: {fallback_kw}

Generate the 4 platform-specific search queries.

Return as JSON:
{{
  "reddit_query": "...",
  "youtube_query": "...",
  "news_query": "...",
  "wikipedia_query": "..."
}}"""

        try:
            def _call():
                return client.chat.completions.create(
                    model=get_model_name(),
                    messages=[
                        {"role": "system", "content": self._SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.4,
                    max_tokens=200
                )

            response = await asyncio.to_thread(_call)
            data = json.loads(response.choices[0].message.content)

            queries = QuerySet(
                reddit_query=data.get("reddit_query", fallback_kw),
                youtube_query=data.get("youtube_query", fallback_kw),
                news_query=data.get("news_query", fallback_kw),
                wikipedia_query=data.get("wikipedia_query", fallback_kw)
            )

            logger.info(
                f"QueryGenerator — reddit='{queries.reddit_query}' | "
                f"youtube='{queries.youtube_query}' | "
                f"news='{queries.news_query}' | "
                f"wikipedia='{queries.wikipedia_query}'"
            )
            return queries

        except Exception as e:
            logger.warning(f"QueryGeneratorService LLM call failed: {e}. Using fallback queries.")
            return self._fallback(fallback_kw)

    def _fallback(self, keyword: str) -> QuerySet:
        """Safe fallback: use the primary keyword for all platforms."""
        return QuerySet(
            reddit_query=keyword,
            youtube_query=keyword,
            news_query=keyword,
            wikipedia_query=keyword.replace(" ", "_").title()
        )
