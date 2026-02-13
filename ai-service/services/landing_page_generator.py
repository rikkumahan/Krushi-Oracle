from pydantic import BaseModel
import os
import httpx
import re
from typing import Optional

class LandingPageRequest(BaseModel):
    idea_name: str
    tagline: str
    description: str
    target_audience: str
    features: list[str]
    style_preference: str = "Modern SaaS" # Modern, Minimalist, Bold

class LandingPageResponse(BaseModel):
    html_content: str
    preview_url: Optional[str] = None # For future use

from utils.openai_helper import get_openai_client, get_model_name
from services.landing_page_components import ComponentTemplates, LandingPageComponentSet
import json
import logging

logger = logging.getLogger(__name__)

class LandingPageGeneratorService:
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if not self._client:
            self._client = get_openai_client()
        return self._client

    def _get_model(self):
        return self.model or get_model_name()

    async def generate_page(self, request: LandingPageRequest) -> LandingPageResponse:
        """
        Generates a premium landing page using Component-Based CRO architecture.
        """
        client = self._get_client()
        if not client:
            return LandingPageResponse(html_content="<h1>LLM Client Missing. Mock Landing Page.</h1>")
            
        try:
            # Stage 1: Copywriting Agent (AIDA Framework)
            component_data = await self._generate_cro_copy(request)
            
            # Stage 2: Visual Assembly
            html = self._assemble_components(component_data, request.idea_name)
            
            return LandingPageResponse(html_content=html)
            
        except Exception as e:
            logger.error(f"Error in Pro Landing Page generation: {e}")
            return LandingPageResponse(html_content=f"<h1>Error generating pro page: {str(e)}</h1>")

    async def _generate_cro_copy(self, request: LandingPageRequest) -> LandingPageComponentSet:
        """Use LLM to generate section-specific conversion-optimized copy"""
        client = self._get_client()
        
        prompt = f"""
        Act as a Landing Page Expert and CRO Specialist. Generate high-conversion copy for this startup.
        
        Startup: {request.idea_name}
        Mission: {request.description}
        Target: {request.target_audience}
        Features: {', '.join(request.features)}
        
        Follow the AIDA framework:
        1. Attention: Punchy Hero headline and subheadline.
        2. Interest: Benefits-driven feature descriptions.
        3. Desire: Pricing tiers that create clear value.
        4. Action: Compelling CTA.
        
        Return a JSON object matching this schema exactly:
        {{
            "hero": {{
                "headline": "Magnetic headline",
                "subheadline": "Benefit-driven subheadline",
                "cta_text": "Action-oriented CTA",
                "image_url": "Image keywords"
            }},
            "features": {{
                "title": "Why people choose us",
                "features": [
                    {{"title": "Feature 1", "description": "Outcome-focused description", "icon": "fa-cloud"}},
                    {{"title": "Feature 2", "description": "Outcome-focused description", "icon": "fa-bolt"}},
                    {{"title": "Feature 3", "description": "Outcome-focused description", "icon": "fa-shield-halved"}}
                ]
            }},
            "pricing": {{
                "options": [
                    {{
                        "name": "Starter",
                        "price": "$29/mo",
                        "description": "For individuals",
                        "features": ["Feature A", "Feature B"],
                        "is_popular": false
                    }},
                    {{
                        "name": "Pro",
                        "price": "$99/mo",
                        "description": "For growing teams",
                        "features": ["All Starter", "Feature C", "Priority Support"],
                        "is_popular": true
                    }},
                    {{
                        "name": "Enterprise",
                        "price": "Custom",
                        "description": "For large organizations",
                        "features": ["All Pro", "Dedicated Manager", "SLA"],
                        "is_popular": false
                    }}
                ]
            }},
            "footer_text": "Short brand mission statement"
        }}
        """
        
        response = client.chat.completions.create(
            model=self._get_model(),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        data = json.loads(response.choices[0].message.content)
        return LandingPageComponentSet(**data)

    def _assemble_components(self, data: LandingPageComponentSet, title: str) -> str:
        """Deterministic assembly of UI components"""
        html_bits = [
            ComponentTemplates.render_hero(data.hero),
            ComponentTemplates.render_features(data.features),
            ComponentTemplates.render_pricing(data.pricing)
        ]
        
        return ComponentTemplates.render_full_page("".join(html_bits), title)
