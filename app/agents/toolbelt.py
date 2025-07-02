from .tools.search import get_search_tool

def get_tools():
    """
    Returns a list of tools that the agent can use.
    """
    # In the future, we will add more tools here.
    tools = [
        get_search_tool()
    ]
    return tools