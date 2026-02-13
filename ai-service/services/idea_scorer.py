"""
Idea Scoring Service
Multi-dimensional scoring for startup ideas
"""

import json
from typing import Optional
from utils.openai_helper import get_openai_client, get_model_name, create_chat_completion
from models.schemas import StartupIdea, IdeaScore, WizardInput


class IdeaScorerService:
    def __init__(self):
        # Uses Azure OpenAI if configured, falls back to regular OpenAI
        self.client = get_openai_client()
        self.model = get_model_name()
        
        # Scoring weights
        self.weights = {
            "market_size": 0.30,
            "differentiation": 0.25,
            "execution_complexity": 0.25,
            "capital_intensity": 0.20
        }
    
    def score_idea(self, idea: StartupIdea, wizard_input: Optional[WizardInput] = None) -> IdeaScore:
        """Score a startup idea across multiple dimensions"""
        
        # If no OpenAI client available, use heuristic scoring
        if not self.client:
            return self._calculate_heuristic_score(idea, wizard_input)
        
        try:
            prompt = self._build_scoring_prompt(idea, wizard_input)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            scores = json.loads(response.choices[0].message.content)
            return self._parse_scores(scores)
            
        except Exception as e:
            # Return heuristic scores if API fails
            return self._calculate_heuristic_score(idea, wizard_input)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert startup analyst. Score ideas objectively based on:

1. **Market Size (0-100)**: TAM potential, growth rate, timing
2. **Differentiation (0-100)**: Uniqueness, competitive moat, innovation
3. **Execution Complexity (0-100)**: Higher = easier to execute. Consider technical, regulatory, operational hurdles
4. **Capital Intensity (0-100)**: Higher = less capital needed. Consider infrastructure, inventory, team costs

Be honest and critical. Most ideas should score between 40-75. Only exceptional ideas score 80+.
Respond in JSON format."""

    def _build_scoring_prompt(self, idea: StartupIdea, wizard_input: Optional[WizardInput]) -> str:
        budget_context = f"with ${wizard_input.budget} budget" if wizard_input else ""
        
        return f"""Score this startup idea {budget_context}:

**Name:** {idea.name}
**Tagline:** {idea.tagline}
**Description:** {idea.description}
**Target Customer:** {idea.target_customer}
**Problem Solved:** {idea.problem_solved}
**MVP Features:** {[f.name for f in idea.mvp_features]}
**Business Model:** Revenue via {', '.join(idea.business_model.revenue_streams)}
**Estimated Cost:** ${idea.estimated_initial_cost}

Return JSON:
{{
  "market_size": <0-100>,
  "differentiation": <0-100>,
  "execution_complexity": <0-100>,
  "capital_intensity": <0-100>,
  "reasoning": {{
    "market_size": "brief reason",
    "differentiation": "brief reason",
    "execution_complexity": "brief reason",
    "capital_intensity": "brief reason"
  }}
}}"""

    def _parse_scores(self, data: dict) -> IdeaScore:
        """Parse API response into IdeaScore"""
        market = data.get("market_size", 50)
        diff = data.get("differentiation", 50)
        exec_comp = data.get("execution_complexity", 50)
        capital = data.get("capital_intensity", 50)
        
        # Calculate weighted overall score
        overall = int(
            market * self.weights["market_size"] +
            diff * self.weights["differentiation"] +
            exec_comp * self.weights["execution_complexity"] +
            capital * self.weights["capital_intensity"]
        )
        
        return IdeaScore(
            market_size=market,
            differentiation=diff,
            execution_complexity=exec_comp,
            capital_intensity=capital,
            overall=overall
        )
    
    def _calculate_heuristic_score(self, idea: StartupIdea, wizard_input: Optional[WizardInput]) -> IdeaScore:
        """Calculate heuristic scores when API unavailable"""
        
        # Base scores
        market_size = 55
        differentiation = 50
        execution_complexity = 60
        capital_intensity = 70
        
        # Adjust based on cost vs budget
        if wizard_input and idea.estimated_initial_cost <= wizard_input.budget * 0.5:
            capital_intensity += 15
        
        # Adjust based on MVP complexity
        must_have_features = len([f for f in idea.mvp_features if f.priority == 1])
        if must_have_features <= 2:
            execution_complexity += 10
        
        # Cap scores at 100
        market_size = min(market_size, 100)
        differentiation = min(differentiation, 100)
        execution_complexity = min(execution_complexity, 100)
        capital_intensity = min(capital_intensity, 100)
        
        overall = int(
            market_size * self.weights["market_size"] +
            differentiation * self.weights["differentiation"] +
            execution_complexity * self.weights["execution_complexity"] +
            capital_intensity * self.weights["capital_intensity"]
        )
        
        return IdeaScore(
            market_size=market_size,
            differentiation=differentiation,
            execution_complexity=execution_complexity,
            capital_intensity=capital_intensity,
            overall=overall
        )
    
    def score_ideas_batch(self, ideas: list[StartupIdea], wizard_input: Optional[WizardInput] = None) -> list[StartupIdea]:
        """Score multiple ideas and return them with scores attached"""
        scored_ideas = []
        for idea in ideas:
            idea.score = self.score_idea(idea, wizard_input)
            scored_ideas.append(idea)
        
        # Sort by overall score descending
        scored_ideas.sort(key=lambda x: x.score.overall if x.score else 0, reverse=True)
        return scored_ideas


# Singleton instance
idea_scorer = IdeaScorerService()
