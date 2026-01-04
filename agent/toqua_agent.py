"""
Orchestrates API and visualization tools
"""

from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from agent.tools import (
    get_ship_performance_data,
    display_performance_graph,
    list_available_ships,
)

load_dotenv()


class ToquaShipAgent:
    """
    Agentic chatbot for ship performance analysis.

    The agent can:
    1. Query ship performance data across speed ranges and environmental conditions
    2. Create interactive fuel curve visualizations
    3. List available ships
    4. Chain multiple tools together (e.g., API → Graph)
    """

    def __init__(self, model="qwen/qwen3-32b", temperature=0.7):
        """
        Initialize the agent.

        Args:
            model: LLM model (default: qwen/qwen3-32b)
            temperature: LLM temperature (0=deterministic, 1=creative)
        """

        # Verify API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment. ")

        # System prompt
        self.system_prompt = f"""You are a maritime intelligence assistant for ship performance analysis for Toqua. Today is {datetime.now(timezone.utc)}.

You help users understand ship performance using:
1. **get_ship_performance_data**: Get fuel consumption, RPM, power, emissions, etc data across speed ranges
2. **display_performance_graph**: Visualize speed vs fuel relationship
3. **list_available_ships**: See available ships in the fleet

## Example Workflow

User: "Show me the fuel consumption for vessel 9999999"

Your response:
1. Call `get_ship_performance_data` with imo=9999999
2. Extract the data without changing any values
3. Call `display_performance_graph` with that data

If visualization succeeds, mention that the graph is ready for display."""

        # Initialize LLM
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
        )

        # Define tools
        self.tools = [
            get_ship_performance_data,
            display_performance_graph,
            list_available_ships,
        ]

        # Create agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
        )

