from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import json
import httpx

class TechComponent(BaseModel):
    name: str
    description: str
    trl: int = Field(..., description="Technology Readiness Level (1-9)")
    complexity: str
    risk_type: str
    reasoning: str

class FeasibilityReport(BaseModel):
    idea_name: str
    components: List[TechComponent]
    overall_trl: int
    feasibility_score: int # 0-100
    mvp_time_estimate: str
    is_science_risk: bool
    summary: str

class TechFeasibilityService:
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = model
        
    async def analyze_feasibility(self, idea_name: str, idea_description: str) -> FeasibilityReport:
        """
        Analyzes the technical feasibility of an idea using LLM via async HTTP request.
        """
        if not self.api_key:
            return self._mock_response(idea_name)
            
        prompt = f"""
        Act as a CTO and Chief Engineer. Analyze the technical feasibility of this idea:
        
        Idea: {idea_name}
        Description: {idea_description}
        
        Task:
        1. Deconstruct this idea into 3-5 core technical components.
        2. Assign a Technology Readiness Level (TRL) from 1-9 for each component.
           - TRL 9: Proven in operational environment (e.g., SQL Database, React App)
           - TRL 1-4: Experimental proof of concept (e.g., Cold Fusion, Brain Interface)
        3. Identify the Risk Type: "Engineering" (Hard but solved physics) vs "Science" (Requires breakthrough).
        4. Estimate time to MVP for a small team (2-3 engineers).
        
        Return ONLY valid JSON in this format:
        {{
            "components": [
                {{ "name": "...", "description": "...", "trl": 9, "complexity": "Medium", "risk_type": "Engineering", "reasoning": "..." }}
            ],
            "overall_trl": 8,
            "feasibility_score": 85,
            "mvp_time_estimate": "3 months",
            "is_science_risk": false,
            "summary": "..."
        }}
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                data = json.loads(content)
                
                # Pydantic parsing
                components = [TechComponent(**c) for c in data.get("components", [])]
                
                return FeasibilityReport(
                    idea_name=idea_name,
                    components=components,
                    overall_trl=data.get("overall_trl", 5),
                    feasibility_score=data.get("feasibility_score", 50),
                    mvp_time_estimate=data.get("mvp_time_estimate", "Unknown"),
                    is_science_risk=data.get("is_science_risk", False),
                    summary=data.get("summary", "Analysis failed")
                )
            
        except Exception as e:
            print(f"Error in Tech Feasibility Analysis (Async HTTP): {e}")
            return self._mock_response(idea_name, error=str(e))

    def _mock_response(self, idea_name: str, error: str = None) -> FeasibilityReport:
        """Fallback mock response"""
        summary = "Mock analysis (OpenAI key missing or error)"
        if error:
            summary += f": {error}"
            
        return FeasibilityReport(
            idea_name=idea_name,
            components=[
                TechComponent(name="Frontend", description="React SPA", trl=9, complexity="Low", risk_type="Engineering", reasoning="Standard web tech"),
                TechComponent(name="Backend", description="FastAPI", trl=9, complexity="Low", risk_type="Engineering", reasoning="Standard web tech")
            ],
            overall_trl=9,
            feasibility_score=95,
            mvp_time_estimate="1 month",
            is_science_risk=False,
            summary=summary
        )
