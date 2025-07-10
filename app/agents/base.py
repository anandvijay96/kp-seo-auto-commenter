from langchain_google_vertexai import VertexAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from typing import AsyncGenerator, Dict, List, Any, Optional, Union
import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)

from app.core.config import settings
from .toolbelt import get_tools
from app.agents.tools.search import SearchTool
from app.memory.vector_memory import VectorMemory

# A more robust ReAct prompt template designed to handle complex, multi-step tasks.
# It guides the model to break down problems and follow a structured reasoning process.
template = """You are a helpful and diligent AI assistant. Your goal is to answer the user's question as accurately and completely as possible.

You have access to the following tools:
{tools}

To answer the question, you MUST use the following format:

Question: The user's input question you must answer.
Thought: You should always think about what to do. Break down the user's request into a step-by-step plan. Consider which tools you'll need and how to use them.
Action: The action to take, which must be one of [{tool_names}].
Action Input: The input to the action.
Observation: The result of the action.
... (this Thought/Action/Action Input/Observation sequence can repeat N times)

Thought: I have now gathered all the information needed and can answer the user's original question. I will now formulate the final answer.
Final Answer: The final, comprehensive answer to the user's original question. Make sure to address all parts of the request.

**Important Reminders:**
- If a task has multiple steps, address each one sequentially.
- Before providing the Final Answer, re-read the original Question to ensure your answer is complete.
- If you are confused or unsure what to do, state your confusion clearly.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

class Agent:
    def __init__(self, tools=None, model_name="gemini-2.5-pro", temperature=0.7, verbose=True):
        # Initialize the VertexAI model once
        self.llm = VertexAI(
            model_name=model_name,
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION,
            temperature=temperature,
        )

        if tools is None:
            self.tools = get_tools()
        else:
            self.tools = tools

        self.search_tool = SearchTool()
        self.conversation_history = []
        
        # Initialize the agent's memory
        self.memory = VectorMemory()

        prompt = ChatPromptTemplate.from_template(template)
        agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            max_iterations=15,  # Increase the iteration limit
            handle_parsing_errors=True  # Make the agent more robust
        )

    async def run(self, task: str, history: list) -> AsyncGenerator[str, None]:
        """
        Run the agent with the given task and history and stream the results.
        The agent will first retrieve relevant memories and then save the new interaction.
        """
        final_answer = ""
        try:
            # 1. Retrieve relevant memories
            retrieved_memories = self.memory.retrieve_memories(query=task)
            memory_context = "\n".join(retrieved_memories)
            
            # 2. Augment the task with memory context
            augmented_task = task
            if retrieved_memories:
                augmented_task = f"""Here is some relevant context from my memory based on the user's request:
{memory_context}

Based on this context, please fulfill the following request: {task}"""

            # Format the history for the agent
            chat_history = []
            for msg in history:
                chat_history.append(HumanMessage(content=msg["user"]))
                if msg.get("ai"):
                    chat_history.append(AIMessage(content=msg["ai"]))

            # Stream the response from the agent
            async for chunk in self.agent_executor.astream(
                {"input": augmented_task, "chat_history": chat_history}
            ):
                # The final answer is in the 'output' key. 
                # We check for it and clean it up before sending.
                if "output" in chunk:
                    final_answer = chunk["output"]
                    # Remove the "Final Answer:" prefix if it exists
                    if final_answer.startswith("Final Answer:"):
                        final_answer = final_answer.replace("Final Answer:", "").strip()
                    yield final_answer

            # 3. Save the interaction to memory after the stream is complete
            if final_answer:
                memory_doc = f"User task: {task}\nAgent response: {final_answer}"
                self.memory.add_memory(
                    document=memory_doc,
                    metadata={"task": task},
                    doc_id=uuid.uuid4().hex
                )

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            yield f"An error occurred: {e}"

    async def chat(self, query: str, history: list) -> str:
        # This method can be simplified or removed if only streaming is needed
        # For now, it will use the main run method's logic
        response_generator = self.run(query, history)
        final_answer = ""
        async for chunk in response_generator:
            if "> Final Answer:" in chunk:
                final_answer = chunk.split("> Final Answer:")[1].strip()
        return final_answer

def create_agent_executor() -> Agent:
    return Agent()