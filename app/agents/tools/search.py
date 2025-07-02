from langchain_community.tools import DuckDuckGoSearchRun

def get_tools():
    """Returns a list of tools that the agent can use."""
    return [DuckDuckGoSearchRun()]
