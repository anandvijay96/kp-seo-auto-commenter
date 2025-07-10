from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from app.agents.base import Agent, create_agent_executor

router = APIRouter()

class ChatMessage(BaseModel):
    user: str
    ai: Optional[str] = None

class AgentRequest(BaseModel):
    task: str
    history: Optional[List[ChatMessage]] = None

@router.post("/run")
async def run_agent(request: AgentRequest, agent: Agent = Depends(create_agent_executor)) -> StreamingResponse:
    """
    Run the agent with the provided input data and stream the results.
    """
    async def stream_generator():
        try:
            task = request.task
            history = [msg.dict() for msg in (request.history or [])]

            if not task:
                yield "Error: Task cannot be empty."
                return

            async for chunk in agent.run(task, history):
                yield chunk
        except Exception as e:
            # In a real-world scenario, you'd want more robust error logging here.
            yield f"Error: {str(e)}"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")