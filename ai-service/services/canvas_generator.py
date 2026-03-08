"""
Canvas Generator Service
Generates export artifacts: Lean Canvas, One-Pager, Pitch Outline
"""

from typing import Dict, Optional
from models.schemas import StartupIdea
from utils.openai_helper import get_openai_client, get_model_name, create_chat_completion
from services.explanatory.strategic_audit_agent import StrategicTools
from services.idea_scorer_v2.engine import ScoringResult
from utils.redis_cache import safe_cache_get, CacheKey


class CanvasGeneratorService:
    
    def __init__(self):
        self.client = get_openai_client()
        self.model = get_model_name()

    def generate_lean_canvas(self, idea: StartupIdea) -> Dict[str, str]:
        """Generate Lean Canvas for an idea using Strategic Reasoning Agent"""
        
        # 1. Try to use Strategic Reasoning Agent with Deterministic Audit Trail
        if self.client:
            try:
                # Attempt to get cached scoring result from Redis
                cache_key = CacheKey.scoring_result(idea.name)
                scoring_result = safe_cache_get(cache_key)
                
                if scoring_result:
                    # Stage 1: Strategic Deep Dive (Using StrategicTools)
                    tools = StrategicTools(scoring_result)
                    
                    # Fetch deterministic data points
                    market_data = tools.get_market_segments(industry=idea.sector or "default")
                    moat_data = tools.get_competitive_moat()
                    risk_data = tools.get_execution_risk()
                    
                    # Construct professional audit analysis for the LLM
                    audit_analysis = {
                        "tam": market_data["tam_usd"],
                        "sam": market_data["sam_usd"],
                        "som": market_data["som_year3_usd"],
                        "moat": moat_data["strategic_insight"],
                        "risk": risk_data["risk_factors"][0]["description"] if risk_data["risk_factors"] else "High technical complexity",
                        "market_structure": moat_data["market_structure"]
                    }
                    
                    # Stage 2: Artifact Extraction (Mapping analysis to blocks)
                    display_canvas = self._generate_strategic_canvas(idea, audit_analysis)
                    
                    if display_canvas:
                         # Add reasoning metadata for the UI (Professional touch)
                         display_canvas["_strategic_moat"] = audit_analysis["moat"]
                         display_canvas["_market_size_tam"] = f"${audit_analysis['tam']:,}"
                         return display_canvas
                else:
                    # Fallback to simple strategic audit if no scoring result cached
                    audit_analysis = self._perform_strategic_audit(idea)
                    display_canvas = self._generate_strategic_canvas(idea, audit_analysis)
                    if display_canvas:
                        return display_canvas
            except Exception as e:
                import logging
                logging.error(f"Strategic Canvas generation error: {e}")
                
        # 2. Fallback: Deterministic Template (Legacy Logic)
        return {
            "problem": idea.problem_solved,
            "solution": idea.description,
            "unique_value_proposition": idea.business_model.value_proposition,
            "unfair_advantage": idea.moonshot_channel,
            "customer_segments": ", ".join(idea.business_model.customer_segments),
            "key_metrics": "CAC, LTV, Retention",
            "channels": ", ".join(idea.business_model.channels),
            "cost_structure": ", ".join(idea.business_model.cost_structure),
            "revenue_streams": ", ".join(idea.business_model.revenue_streams)
        }

    def _perform_strategic_audit(self, idea: StartupIdea) -> Dict[str, str]:
        """Stage 1: Analyze the idea for deep strategic moats and risks"""
        prompt = f"""
        Conduct a 60-second strategic audit of this startup idea:
        
        Idea: {idea.name}
        Description: {idea.description}
        Target: {idea.target_customer}
        
        Identify:
        1. THE MOAT: What is the defensible 'Unfair Advantage'?
        2. THE SHOWSTOPPER: What is the #1 risk that kills this?
        3. THE IDEAL ADOPTER: Who is the highly specific early adopter?
        
        Return a JSON object: {{"moat": "...", "risk": "...", "adopter": "..."}}
        """
        
        response = create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        import json
        return json.loads(response.choices[0].message.content)

    def _generate_strategic_canvas(self, idea: StartupIdea, audit: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Stage 2: Use the strategic audit to populate the final Lean Canvas"""
        prompt = f"""
        Act as a Veteran Startup Consultant. Create a VC-ready Lean Canvas.
        
        **Strategic Context**:
        - Moat: {audit.get('moat')}
        - Primary Risk: {audit.get('risk')}
        - Target Persona: {audit.get('adopter')}
        
        **Startup Details**:
        - Name: {idea.name}
        - Description: {idea.description}
        
        Populate the Lean Canvas with high-density, professional insights.
        Return JSON with these exact keys:
        {{
            "problem": "Top 3 systemic problems",
            "solution": "3 core solution pillars",
            "unique_value_proposition": "High-impact UVP",
            "unfair_advantage": "Defensible moat (use Audit context)",
            "customer_segments": "Specific segments (starting with {audit.get('adopter')})",
            "key_metrics": "North Star Metric + 2 secondary",
            "channels": "Primary, Secondary, and Experimental channels",
            "cost_structure": "Realistic cost drivers",
            "revenue_streams": "Monetization strategy"
        }}
        """
        
        response = create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        import json
        return json.loads(response.choices[0].message.content)

    def generate_one_pager(self, idea: StartupIdea) -> str:
        """Generate executive summary one-pager"""
        score_section = ""
        if idea.score:
            score_section = f"""
## Opportunity Score: {idea.score.overall}/100
- Market Size: {idea.score.market_size}/100
- Differentiation: {idea.score.differentiation}/100  
- Execution Ease: {idea.score.execution_complexity}/100
- Capital Efficiency: {idea.score.capital_intensity}/100
"""
        
        features_list = "\n".join([
            f"- **{f.name}** (P{f.priority}): {f.description}" 
            for f in idea.mvp_features
        ])
        
        return f"""# {idea.name}

> {idea.tagline}

## The Problem
{idea.problem_solved}

## Our Solution  
{idea.description}

## Target Customer
{idea.target_customer}
{score_section}
## MVP Features
{features_list}

## Business Model
**Revenue:** {', '.join(idea.business_model.revenue_streams)}
**Channels:** {', '.join(idea.business_model.channels)}

## Initial Investment
${idea.estimated_initial_cost:,}

## Growth Strategy
{idea.moonshot_channel}

---
*Generated by Nova*
"""

    def generate_pitch_outline(self, idea: StartupIdea) -> Dict[str, str]:
        """Generate 5-slide pitch deck outline"""
        return {
            "slide_1_title": f"{idea.name} - {idea.tagline}",
            "slide_2_problem": f"**Problem:** {idea.problem_solved}\n\n*Who feels this?* {idea.target_customer}",
            "slide_3_solution": f"**Solution:** {idea.description}\n\n**Key Features:**\n" + 
                "\n".join([f"• {f.name}: {f.description}" for f in idea.mvp_features[:3]]),
            "slide_4_business_model": f"**How We Make Money:**\n" +
                "\n".join([f"• {r}" for r in idea.business_model.revenue_streams]) +
                f"\n\n**Launch Cost:** ${idea.estimated_initial_cost:,}",
            "slide_5_ask": f"**Growth Strategy:** {idea.moonshot_channel}\n\n" +
                f"**Key Partners:** {', '.join(idea.business_model.key_partners)}"
        }
    
    def generate_html_lean_canvas(self, idea: StartupIdea) -> str:
        """Generate HTML version of Lean Canvas"""
        canvas = self.generate_lean_canvas(idea)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lean Canvas - {idea.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', system-ui, sans-serif; background: #0a0a0a; color: #fff; padding: 2rem; }}
        .canvas {{ display: grid; grid-template-columns: repeat(5, 1fr); grid-template-rows: repeat(2, 1fr); gap: 1px; background: #333; border: 1px solid #333; max-width: 1200px; margin: 0 auto; }}
        .canvas-cell {{ background: #1a1a1a; padding: 1rem; min-height: 150px; }}
        .canvas-cell h3 {{ color: #00ff88; font-size: 0.75rem; text-transform: uppercase; margin-bottom: 0.5rem; letter-spacing: 0.05em; }}
        .canvas-cell p {{ font-size: 0.875rem; line-height: 1.5; color: #ccc; }}
        .title {{ text-align: center; margin-bottom: 2rem; }}
        .title h1 {{ font-size: 2rem; color: #00ff88; }}
        .title p {{ color: #888; margin-top: 0.5rem; }}
        .problem {{ grid-row: span 2; }}
        .solution {{ grid-row: span 2; }}
    </style>
</head>
<body>
    <div class="title">
        <h1>{idea.name}</h1>
        <p>{idea.tagline}</p>
    </div>
    <div class="canvas">
        <div class="canvas-cell problem">
            <h3>Problem</h3>
            <p>{canvas['problem']}</p>
        </div>
        <div class="canvas-cell solution">
            <h3>Solution</h3>
            <p>{canvas['solution']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Unique Value Proposition</h3>
            <p>{canvas['unique_value_proposition']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Unfair Advantage</h3>
            <p>{canvas['unfair_advantage']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Customer Segments</h3>
            <p>{canvas['customer_segments']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Key Metrics</h3>
            <p>{canvas['key_metrics']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Channels</h3>
            <p>{canvas['channels']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Cost Structure</h3>
            <p>{canvas['cost_structure']}</p>
        </div>
        <div class="canvas-cell">
            <h3>Revenue Streams</h3>
            <p>{canvas['revenue_streams']}</p>
        </div>
    </div>
</body>
</html>"""


# Singleton instance
canvas_generator = CanvasGeneratorService()
