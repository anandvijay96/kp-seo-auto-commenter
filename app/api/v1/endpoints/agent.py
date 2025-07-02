from fastapi import APIRouter, HTTPException
from typing import Dict
from app.agents.base import Agent
from app.agents.toolbelt import get_tools

router = APIRouter()

@router.post("/run")
async def run_agent(data: Dict) -> Dict:
    """
    Run the agent with the provided input data.
    
    Args:
        data: Input data for the agent to process
            - task: The type of task to perform
            - parameters: Any additional parameters needed for the task
    
    Returns:
        Dict: Response containing task status and results
    """
    try:
        # Initialize the agent with available tools
        agent = Agent(tools=get_tools())
        
        # Run the agent with the provided data
        result = await agent.run(data)
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))