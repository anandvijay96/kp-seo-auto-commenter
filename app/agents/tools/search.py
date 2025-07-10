from typing import Optional
from langchain_community.tools import DuckDuckGoSearchRun
from app.scraper.scraper import scrape_page

class SearchTool:
    async def analyze_url(self, url: str) -> str:
        """Analyze a webpage by fetching and extracting its content."""
        try:
            # Use our Playwright-based scraper for better content extraction
            content = await scrape_page(url)
            
            # Truncate if too long
            max_length = 4000  # Adjust based on model's context window
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            return content
        except Exception as e:
            return f"Error analyzing URL: {str(e)}"

    async def search(self, query: str) -> str:
        """Search the web using DuckDuckGo."""
        # For MVP, we'll just analyze URLs directly
        # Web search can be added in a future iteration
        if query.startswith(('http://', 'https://')):
            return await self.analyze_url(query)
        return f"Direct web search not implemented yet. Please provide a URL to analyze."

def get_tools():
    """Returns a list of tools that the agent can use."""
    return [DuckDuckGoSearchRun()]
