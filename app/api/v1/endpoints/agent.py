from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, AsyncGenerator
from app.agents.base import Agent
from app.agents.toolbelt import get_tools

router = APIRouter()

async def stream_agent_response(data: Dict) -> AsyncGenerator[str, None]:
    """
    Runs the agent and streams the response back chunk by chunk.
    """
    try:
        agent = Agent(tools=get_tools())
        # The agent's run method is now expected to be an async generator
        async for chunk in agent.run(data):
            yield chunk
    except Exception as e:
        # In a real-world scenario, you'd want more robust error logging here.
        # For now, we'll just yield an error message.
        yield f"DEPLOYMENT_CHECK_V3 - Error: {str(e)}"

@router.post("/run")
async def run_agent(data: Dict):
    """
    Run the agent with the provided input data and stream the results.
    """
    return StreamingResponse(stream_agent_response(data), media_type="text/event-stream")