"""
Conversational Orchestrator with Function Calling
Uses LLM to manage dialogue AND trigger deterministic tools when ready.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import json
import logging
from datetime import datetime

from utils.openai_helper import get_openai_client, get_model_name

logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class OrchestratorResponse(BaseModel):
    reply: str
    tool_results: List[Dict[str, Any]] = []  # Results from deterministic tools
    suggested_actions: List[str] = []
    extracted_data: Optional[Dict] = None
    confidence: float = 0.0

class OrchestratorService:
    """
    Manages conversation AND triggers deterministic tools via function calling.
    """
    
    SYSTEM_PROMPT = """
You are Nova, an elite startup validation AI with access to deterministic analysis tools.

YOUR ROLE:
1. Converse naturally to understand the user's startup idea
2. When you have enough info (Idea Name, Description, Target Market), AUTOMATICALLY call the scoring tools
3. Present results in a professional, actionable format

REQUIRED INFO:
- Idea Name
- Problem/Solution Description  
- Target Market/Audience
- Sector (SaaS, E-commerce, Marketplace, etc.)

TOOLS AVAILABLE:
- score_idea: Deterministic MVS scoring (0-100)
- explain_score: Strategic audit with VC-level insights
- estimate_traffic: Market size estimation
- generate_canvas: Create a Lean Canvas business model
- generate_pitch: Create a Pitch Deck presentation

BEHAVIOR:
- Ask 1-2 clarifying questions if idea is vague
- Once you have enough info, CALL score_idea immediately
- After scoring, CALL explain_score to provide strategic context
- Use markdown formatting for readability
- Be encouraging but rigorous

CRITICAL: Do NOT ask permission to run analysis. Just do it when ready.
"""

    def __init__(self):
        self.history_limit = 10
        self.client = get_openai_client()
        if not self.client:
            raise RuntimeError("OpenAI client not available")
        
        # Define tools schema
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "score_idea",
                    "description": "Score a startup idea using deterministic MVS engine. Returns market, differentiation, execution, and capital scores.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "idea_name": {"type": "string", "description": "Name of the startup idea"},
                            "idea_description": {"type": "string", "description": "Brief description of the idea"},
                            "target_market": {"type": "string", "description": "Target market or customer segment"},
                            "sector": {"type": "string", "description": "Industry sector (e.g., SaaS, E-commerce, Marketplace)"}
                        },
                        "required": ["idea_name", "idea_description", "target_market"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "explain_score",
                    "description": "Get strategic audit and VC-level explanation of the score. Call AFTER score_idea.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "idea_name": {"type": "string", "description": "Name of the idea (must match scored idea)"},
                            "question": {"type": "string", "description": "What to explain (e.g., 'Why this score?', 'What are the risks?')"}
                        },
                        "required": ["idea_name", "question"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "estimate_traffic",
                    "description": "Estimate monthly traffic and market size for the idea.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "idea_name": {"type": "string"},
                            "idea_description": {"type": "string"},
                            "industry": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "budget": {"type": "number", "description": "Monthly ad budget (minimum 100)"}
                        },
                        "required": ["idea_name", "idea_description", "industry", "target_audience", "budget"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_canvas",
                    "description": "Generate a Lean Canvas for the startup idea. Returns 9-block business model.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "idea_name": {"type": "string"},
                            "idea_description": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "problem_solved": {"type": "string"}
                        },
                        "required": ["idea_name", "idea_description", "target_audience"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_pitch",
                    "description": "Generate a 10-slide Pitch Deck. Returns slide content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "idea_name": {"type": "string"},
                            "idea_description": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "problem_solved": {"type": "string"}
                        },
                "required": ["idea_name", "idea_description", "target_audience"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_landing_page",
                    "description": "Generate a high-conversion Landing Page with copy grounded in validation data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "idea_name": {"type": "string"},
                            "idea_description": {"type": "string"},
                            "target_audience": {"type": "string"},
                            "tagline": {"type": "string", "description": "Catchy single-sentence value prop"},
                            "style": {"type": "string", "description": "Design style (e.g., 'Modern SaaS', 'Minimalist', 'Enterprise')"}
                        },
                        "required": ["idea_name", "idea_description", "target_audience"]
                    }
                }
            }
        ]

    async def process_message_stream(self, history: List[ChatMessage]):
        """
        Generator that yields SSE events:
        - {"type": "token", "content": "..."}
        - {"type": "status", "content": "..."}
        - {"type": "tool_result", "content": ...}
        """
        try:
            # Prepare messages
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
            for msg in history[-self.history_limit:]:
                messages.append({"role": msg.role, "content": msg.content})
            
            tool_results = []
            max_iterations = 3
            
            for iteration in range(max_iterations):
                # Request streaming completion
                stream = self.client.chat.completions.create(
                    model=get_model_name(),
                    messages=messages,
                    tools=self.tools_schema,
                    tool_choice="auto",
                    temperature=0.7,
                    stream=True
                )
                
                # Accumulators for streaming response
                current_content = ""
                tool_calls = []
                
                for chunk in stream:
                    try:
                        if not chunk.choices:
                            continue
                            
                        delta = chunk.choices[0].delta
                        
                        # 1. Handle Text Content
                        if delta.content:
                            current_content += delta.content
                            yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"

                        # 2. Handle Tool Calls (Accumulate deltas)
                        if delta.tool_calls:
                            for tool_call_chunk in delta.tool_calls:
                                index = tool_call_chunk.index
                                
                                # Ensure list is large enough
                                while len(tool_calls) <= index:
                                    tool_calls.append({
                                        "id": "", 
                                        "function": {"name": "", "arguments": ""}
                                    })
                                
                                # Append ID
                                if tool_call_chunk.id:
                                    tool_calls[index]["id"] += tool_call_chunk.id
                                
                                # Append Name
                                if tool_call_chunk.function.name:
                                    tool_calls[index]["function"]["name"] += tool_call_chunk.function.name
                                    
                                # Append Arguments
                                if tool_call_chunk.function.arguments:
                                    tool_calls[index]["function"]["arguments"] += tool_call_chunk.function.arguments
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}", exc_info=True)
                        continue

                # Check if we have tool calls to execute
                if not tool_calls:
                    # No tools called, we are done
                    break
                
                # Append assistant's full message (with tool calls) to history
                # We need to reconstruct the message object correctly for the next API call
                assistant_msg = {
                    "role": "assistant",
                    "content": current_content if current_content else None,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": tc["function"]
                        } for tc in tool_calls
                    ]
                }
                messages.append(assistant_msg)
                
                # Execute Tools
                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    tool_id = tc["id"]
                    try:
                        args = json.loads(tc["function"]["arguments"])
                        yield f"data: {json.dumps({'type': 'status', 'content': f'Executing {tool_name}...'})}\n\n"
                        
                        # Execute
                        logger.info(f"Orchestrator streaming tool: {tool_name}")
                        result = await self._execute_tool(tool_name, args)
                        
                        # Add to results
                        tool_results.append({
                            "tool": tool_name,
                            "arguments": args,
                            "result": result
                        })
                        
                        # Yield result for UI
                        yield f"data: {json.dumps({'type': 'tool_result', 'tool': tool_name, 'content': result})}\n\n"
                        
                        # Append tool output to history
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": json.dumps(result, default=str)
                        })
                        
                    except json.JSONDecodeError:
                        logger.error(f"Failed to decode arguments for {tool_name}")
                        yield f"data: {json.dumps({'type': 'error', 'content': f'Failed to parse arguments for {tool_name}'})}\n\n"

            # Final check (if loop finished normally via break or max iterations)
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    async def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Execute a deterministic tool by calling the actual V2 endpoints
        """
        # Import here to avoid circular dependencies
        from routers.scoring_v2 import explain_score, ExplainRequest, get_agent
        from routers.verification import estimate_traffic, TrafficEstimateRequest
        from verification.dependencies import get_universal_validator
        from verification.universal_validator import UniversalValidationRequest
        
        try:
            if tool_name == "score_idea":
                # Use Universal Validator which calls REAL APIs (Google Trends, YouTube, Reddit)
                request = UniversalValidationRequest(
                    idea_name=arguments["idea_name"],
                    idea_description=arguments["idea_description"],
                    target_market=arguments["target_market"],
                    sector=arguments.get("sector", "SaaS"),
                    keywords=[]  # Auto-generated by validator if empty
                )
                
                validator = get_universal_validator()
                result = await validator.validate(request)
                
                # Convert to score-like response
                return {
                    "mvs_score": result.overall_confidence,
                    "mvs_grade": self._score_to_grade(result.overall_confidence),
                    "validation_class": result.validation_class,
                    "recommendations": result.recommendations,
                    "dimension_scores": {
                        "market": result.google_trends_score,
                        "differentiation": result.competitive_moat_score,
                        "execution": result.execution_risk_score,
                        "capital": result.capital_efficiency_score
                    },
                    "data_source": "Universal Validator (Real APIs)",
                    "api_calls_made": ["Google Trends", "YouTube", "Reddit", "News API", "Wikipedia"]
                }
            
            elif tool_name == "explain_score":
                request = ExplainRequest(
                    idea_name=arguments["idea_name"],
                    question=arguments.get("question", "Provide a strategic audit of this idea.")
                )
                
                agent = get_agent()
                result = await explain_score(request, agent)
                return result.model_dump()
            
            elif tool_name == "estimate_traffic":
                request = TrafficEstimateRequest(
                    idea_name=arguments.get("idea_name", "Unknown Idea"),
                    idea_description=arguments.get("idea_description", ""),
                    industry=arguments.get("industry", "Technology"),
                    target_audience=arguments.get("target_audience", "General Public"),
                    budget=float(arguments.get("budget", 500))
                )
                
                from core.grounded_dependencies import get_traffic_estimator
                service = get_traffic_estimator()
                result = await service.estimate_traffic(request)
                return result.model_dump()
            
            elif tool_name == "generate_canvas":
                from core.grounded_dependencies import get_grounded_canvas
                from models.schemas import StartupIdea
                
                # Create minimal idea object to pass to generator
                idea = StartupIdea(
                    id="orchestrator_gen",
                    name=arguments["idea_name"],
                    description=arguments["idea_description"],
                    target_customer=arguments["target_audience"],
                    problem_solved=arguments.get("problem_solved", "")
                )
                
                generator = get_grounded_canvas()
                # Run the generator (it handles validation internally)
                canvas_data = await generator.generate_canvas(idea)
                return {"canvas": canvas_data.get("canvas", {})}
            
            elif tool_name == "generate_pitch":
                from core.grounded_dependencies import get_grounded_pitch
                from models.schemas import StartupIdea
                
                idea = StartupIdea(
                    id="orchestrator_gen",
                    name=arguments["idea_name"],
                    description=arguments["idea_description"],
                    target_customer=arguments["target_audience"],
                    problem_solved=arguments.get("problem_solved", "")
                )
                
                generator = get_grounded_pitch()
                pitch_data = await generator.generate_pitch(idea)
                # Only return the slides to keep context size manageable for the LLM
                return {"slides": pitch_data.get("slides", [])}

            elif tool_name == "generate_landing_page":
                from core.grounded_dependencies import get_grounded_landing_page
                from services.grounded_landing_page_generator import LandingPageRequest
                
                req = LandingPageRequest(
                    idea_name=arguments["idea_name"],
                    tagline=arguments.get("tagline", "The Future of " + arguments["idea_name"]),
                    description=arguments["idea_description"],
                    target_audience=arguments["target_audience"],
                    features=[], # Generator will auto-generate or use defaults
                    style_preference=arguments.get("style", "Modern SaaS")
                )
                
                generator = get_grounded_landing_page()
                result = await generator.generate_page(req)
                dump = result.model_dump()
                return {
                    "html_content": dump.get("html_content"),
                    "preview_url": dump.get("preview_url")
                }

            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
