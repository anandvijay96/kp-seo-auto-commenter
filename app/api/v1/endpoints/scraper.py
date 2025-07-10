from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, AsyncGenerator, Optional, List
from pydantic import BaseModel

from app.scraper.scraper import scrape_page
from app.agents.base import Agent, create_agent_executor
from .agent import ChatMessage # Import ChatMessage for the request model

router = APIRouter()

class ScraperRequest(BaseModel):
    url: str
    task: str
    history: Optional[List[ChatMessage]] = None

async def stream_scrape_and_run_agent(request: ScraperRequest, agent: Agent) -> AsyncGenerator[str, None]:
    """
    Streams the agent's response after scraping a URL.
    """
    url = request.url
    task = request.task
    history = [msg.dict() for msg in (request.history or [])]

    try:
        # 1. Scrape the content from the URL
        yield "Scraping page...\n"
        scrape_result = await scrape_page(url)
        
        if scrape_result["error"]:
            yield f"Error: {scrape_result['error']}\n"
            return
        
        yield "Page scraped successfully. Generating response...\n"

        # 2. Prepare the new task for the agent, including the scraped content and metadata
        metadata = scrape_result["metadata"]
        content = scrape_result["content"]
        
        # Create a clear, structured context message with the scraped data.
        scraped_context_message = f"""I have scraped the content from the URL '{url}'. Here is the data:

Article Metadata:
- Title: {metadata.get('title', 'N/A')}
- Description: {metadata.get('description', 'N/A')}

Full Article Content:
---
{content}
---

Now, please perform the following task: '{task}'"""

        # The agent's 'run' method expects a 'task' and 'history'.
        # We'll provide the context and the user's task in the 'task' field,
        # and pass the existing conversation history separately.
        agent_task = {
            "task": scraped_context_message,
            "history": history
        }

        # 3. Run the agent with the new task
        async for chunk in agent.run(task=scraped_context_message, history=history):
            yield chunk

    except Exception as e:
        yield f"An unexpected error occurred: {str(e)}"


@router.post("/scrape-and-run")
async def scrape_and_run(request: ScraperRequest, agent: Agent = Depends(create_agent_executor)) -> StreamingResponse:
    """
    Scrapes a URL and then runs the agent on the content.
    Returns a streaming response.
    """
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not request.task:
        raise HTTPException(status_code=400, detail="Task is required")
        
    return StreamingResponse(
        stream_scrape_and_run_agent(request, agent), 
        media_type="text/event-stream"
    )
