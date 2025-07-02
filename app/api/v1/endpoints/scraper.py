from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Dict, AsyncGenerator

from app.scraper.scraper import scrape_page
from app.agents.base import Agent
from app.agents.tools import get_tools

router = APIRouter()

async def stream_scrape_and_run_agent(data: Dict) -> AsyncGenerator[str, None]:
    """
    Streams the agent's response after scraping a URL.
    """
    url = data.get("url")
    task = data.get("task")
    history = data.get("history", [])

    if not url or not task:
        yield "Error: 'url' and 'task' are required fields."
        return

    try:
        # 1. Scrape the content from the URL
        yield "Scraping page...\n"
        scraped_content = await scrape_page(url)
        if scraped_content.startswith("Error:"):
            yield scraped_content
            return
        
        yield "Page scraped successfully. Generating response...\n"

        # 2. Prepare the new task for the agent, including the scraped content
        agent_task = {
            "task": f"Based on the following article content, please perform this task: '{task}'.\n\nArticle Content:\n---\n{scraped_content}\n---",
            "history": history
        }

        # 3. Run the agent with the new task
        agent = Agent(tools=get_tools())
        async for chunk in agent.run(agent_task):
            yield chunk

    except Exception as e:
        yield f"An unexpected error occurred: {str(e)}"


@router.post("/scrape-and-run")
async def scrape_and_run(data: Dict):
    """
    Scrapes a URL and then runs the agent on the content.
    Returns a streaming response.
    """
    return StreamingResponse(stream_scrape_and_run_agent(data), media_type="text/event-stream")
