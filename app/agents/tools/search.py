from langchain_community.tools import DuckDuckGoSearchRun

def get_search_tool():
    """Returns a tool that allows the agent to search the web."""
    return DuckDuckGoSearchRun()
