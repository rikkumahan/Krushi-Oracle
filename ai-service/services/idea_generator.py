"""
Idea Generator Service (FastAPI/Pydantic V2)
Uses OpenAI via async HTTP to generate startup ideas based on wizard input
"""

import os
import json
import uuid
import httpx
from typing import List, Dict, Any, Optional
from models.schemas import (
    WizardInput, 
    StartupIdea, 
    MVPFeature, 
    BusinessModelSnippet,
    IdeaGenerationResponse
)

class IdeaGeneratorService:
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = model
    
    async def generate_ideas(self, wizard_input: WizardInput, num_ideas: int = 5, contrarian_override: bool = False) -> IdeaGenerationResponse:
        """
        Generate startup ideas based on wizard input using async HTTP.
        """
        
        prompt = self._build_prompt(wizard_input, num_ideas, contrarian_override)
        system_prompt = self._get_system_prompt(contrarian_override)
        
        if not self.api_key:
            return self._generate_stub_ideas(wizard_input, num_ideas)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.9 if contrarian_override else 0.7, # Higher temp for contrarian
            "max_tokens": 4000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                ideas_data = json.loads(content)
                
                ideas = self._parse_ideas(ideas_data)
                
                return IdeaGenerationResponse(
                    ideas=ideas,
                    generation_id=str(uuid.uuid4()),
                    input_summary=f"Industry: {wizard_input.industry}, Audience: {wizard_input.target_audience}, Budget: ${wizard_input.budget}, Contrarian: {contrarian_override}"
                )
            
        except Exception as e:
            print(f"Error generating ideas: {e}")
            return self._generate_stub_ideas(wizard_input, num_ideas)
    

    def _get_system_prompt(self, contrarian_override: bool) -> str:
        base_prompt = """You are Nova, an expert startup advisor and idea generator. 
You help founders discover viable business ideas based on their skills, interests, and constraints.

**Chain of Thought Generation Process:**
1. **Analyze Constraints:** Deeply understand the user's budget, skills, and time frame.
2. **Identify Market Patterns:** Look for standard problems in the target industry.
3. **Lateral Thinking:** Apply business models from other industries to this one (e.g., "Uber for X", "Airbnb for Y").
4. **Synthesize:** Generate ideas that fit the constraints but offer a unique angle.

Your ideas should be:
- Practical and achievable with the given budget
- Specific with clear problem-solution fit
- Include actionable MVP features
"""
        if contrarian_override:
            base_prompt += """
**CONTRARIAN OVERRIDE ACTIVE:**
- IGNORE conventional wisdom.
- Look for "Bad Ideas" that are actually good (Peter Thiel's zero to one).
- Focus on unproven, high-risk/high-reward angles.
- It is okay if the idea seems initially "too niche" or "weird".
- Challenge the user's stated interests if a massive opportunity exists adjacent to them.
"""
        else:
            base_prompt += """
- Aligned with current market trends
- Low risk, high validation probability
"""

        base_prompt += "\nAlways respond in valid JSON format."
        return base_prompt

    def _build_prompt(self, wizard_input: WizardInput, num_ideas: int, contrarian_override: bool) -> str:
        prompt = f"""Generate {num_ideas} startup ideas for a founder with the following profile:

**Industry Focus:** {wizard_input.industry}
**Target Audience:** {wizard_input.target_audience}  
**Technical Skill Level:** {wizard_input.skill_level.value}
**Starting Budget:** ${wizard_input.budget}
**Time to Market Goal:** {wizard_input.time_frame.value.replace('_', ' ')}
**Interests:** {wizard_input.interests or 'Not specified'}
**Location:** {wizard_input.location or 'Global'}
"""
        if contrarian_override:
            prompt += "\n**IMPORTANT:** The user has enabled CONTRARIAN MODE. taking big swings. Do not generate safe, generic SaaS ideas. Generate polarized, opinionated ideas that might fail but could be massive.\n"

        prompt += """
For each idea, provide:
1. A catchy name and one-line tagline
2. 2-3 sentence description
3. The specific problem being solved
4. Target customer persona
5. 3 MVP features (with priority 1-3)
6. Business model canvas snippet (revenue streams, key partners, cost structure, value proposition, customer segments, channels)
7. One moonshot growth channel
8. Estimated initial cost

Return as JSON with this structure:
{
  "ideas": [
    {
      "id": "unique-id",
      "name": "Startup Name",
      "tagline": "One-liner",
      "description": "Description",
      "target_customer": "Customer persona",
      "problem_solved": "Problem statement",
      "mvp_features": [
        {"name": "Feature", "description": "Desc", "priority": 1}
      ],
      "business_model": {
        "revenue_streams": ["stream1"],
        "key_partners": ["partner1"],
        "cost_structure": ["cost1"],
        "value_proposition": "Value prop",
        "customer_segments": ["segment1"],
        "channels": ["channel1"]
      },
      "moonshot_channel": "Growth strategy",
      "estimated_initial_cost": 1000
    }
  ]
}"""
        return prompt

    def _parse_ideas(self, data: dict) -> List[StartupIdea]:
        """Parse JSON response into StartupIdea objects using Pydantic"""
        ideas = []
        for idea_data in data.get("ideas", []):
            try:
                # Pydantic handles validation and type conversion
                idea = StartupIdea(
                    id=idea_data.get("id", str(uuid.uuid4())),
                    name=idea_data.get("name", "Untitled"),
                    tagline=idea_data.get("tagline", ""),
                    description=idea_data.get("description", ""),
                    target_customer=idea_data.get("target_customer", ""),
                    problem_solved=idea_data.get("problem_solved", ""),
                    mvp_features=[MVPFeature(**f) for f in idea_data.get("mvp_features", [])],
                    business_model=BusinessModelSnippet(**idea_data.get("business_model", {})),
                    moonshot_channel=idea_data.get("moonshot_channel", ""),
                    estimated_initial_cost=int(idea_data.get("estimated_initial_cost", 0))
                )
                ideas.append(idea)
            except Exception as e:
                print(f"Error parsing idea: {e}")
                continue
        return ideas

    def _generate_stub_ideas(self, wizard_input: WizardInput, num_ideas: int) -> IdeaGenerationResponse:
        """Generate stub ideas when API is unavailable"""
        prefix = "Contrarian" if getattr(wizard_input, 'contrarian_override', False) else "Nova"
        stub_ideas = [
            StartupIdea(
                id=str(uuid.uuid4()),
                name=f"{prefix} Demo Idea {i+1}",
                tagline=f"AI-powered solution for {wizard_input.industry}",
                description=f"A {wizard_input.industry} startup targeting {wizard_input.target_audience}",
                target_customer=wizard_input.target_audience,
                problem_solved=f"Key challenges in {wizard_input.industry}",
                mvp_features=[
                    MVPFeature(name="Core Feature", description="Main functionality", priority=1),
                    MVPFeature(name="Dashboard", description="Analytics view", priority=2),
                    MVPFeature(name="Integrations", description="Third-party connections", priority=3)
                ],
                business_model=BusinessModelSnippet(
                    revenue_streams=["Subscription", "Transaction fees"],
                    key_partners=["Technology providers", "Industry experts"],
                    cost_structure=["Development", "Marketing", "Operations"],
                    value_proposition=f"Streamlined solution for {wizard_input.target_audience}",
                    customer_segments=[wizard_input.target_audience],
                    channels=["Direct sales", "Content marketing", "Partnerships"]
                ),
                moonshot_channel="Viral product-led growth",
                estimated_initial_cost=min(wizard_input.budget, 5000)
            )
            for i in range(num_ideas)
        ]
        
        return IdeaGenerationResponse(
            ideas=stub_ideas,
            generation_id=str(uuid.uuid4()),
            input_summary=f"[STUB] Industry: {wizard_input.industry}"
        )
