import pytest
import asyncio
from services.orchestrator import OrchestratorService
from core.grounded_dependencies import get_grounded_canvas, get_grounded_pitch

def test_orchestrator_has_tools():
    """Verify Orchestrator has the new grounded tools"""
    service = OrchestratorService()
    tool_names = [t["function"]["name"] for t in service.tools_schema]
    
    assert "generate_canvas" in tool_names
    assert "generate_pitch" in tool_names
    print("Orchestrator tools verified successfully.")

if __name__ == "__main__":
    test_orchestrator_has_tools()
