from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from typing import AsyncGenerator, Dict

from app.core.config import settings
from .toolbelt import get_tools
from app.agents.gemini_client import stream_gemini_response

# This is a standard ReAct (Reasoning and Acting) prompt template.
# It instructs the agent on how to think, act, and observe.
template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

def create_agent_executor():
    """
    Creates and configures the main agent executor.
    """
    prompt = PromptTemplate.from_template(template)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",  # Updated model name
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7,
        convert_system_message_to_human=True
    )
    
    tools = get_tools()
    
    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True, # Set to False in production
        handle_parsing_errors=True # Gracefully handle when the agent messes up formatting
    )
    
    return agent_executor

# Add this at the end of base.py
class Agent:
    def __init__(self, tools=None):
        self.tools = tools or get_tools()
        self.agent_executor = create_agent_executor()
    
    async def run(self, data: dict) -> AsyncGenerator[str, None]:
        # In a test environment, yield a single mock response chunk and exit.
        if settings.ENVIRONMENT == "test":
            yield "This is a mock response for testing."
            return

        # Prepare messages for Gemini API
        user_message = data.get("task", "")
        conversation_history = data.get("history", [])

        # Format as list of {"role": ..., "parts": [...]}
        messages = []
        for entry in conversation_history:
            messages.append({"role": "user", "parts": [entry.get("user")]})
            if entry.get("ai"):
                messages.append({"role": "model", "parts": [entry.get("ai")]})
        messages.append({"role": "user", "parts": [user_message]})

        # Stream the response from the Gemini client
        async for chunk in stream_gemini_response(messages):
            yield chunk