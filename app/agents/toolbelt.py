from .tools import get_tools as get_search_tools

__all__ = ["get_tools"]

def get_tools():
    """
    This is the main toolbelt for the agent.
    It aggregates all the individual tools from the `tools` package.
    """
    # In the future, we will add more tools here.
    all_tools = []
    all_tools.extend(get_search_tools())
    return all_tools