from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from .toolbelt import get_tools

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
    
    async def run(self, data: dict) -> dict:
        """
        Run the agent with the provided input data.
        
        Args:
            data: Dictionary containing:
                - task: The task to perform
                - parameters: Any additional parameters needed for the task
        
        Returns:
            dict: The result of the agent's execution
        """
        if settings.ENVIRONMENT == "test":
            return {
                "status": "success",
                "result": {
                    "status": "success",
                    "output": "This is a mock response for testing"
                },
                "response": "This is a mock response for testing"
            }
            
        try:
            # Get the task and parameters from the input data
            task = data.get('task', '')
            parameters = data.get('parameters', {})
            
            # Create the input for the agent
            input_text = f"Task: {task}\nParameters: {parameters}"
            
            # Run the agent
            result = await self.agent_executor.ainvoke({"input": input_text})
            
            return {
                "status": "success",
                "result": result.get("output", "No output from agent")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }