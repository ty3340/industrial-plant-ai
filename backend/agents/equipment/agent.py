"""Equipment Monitoring agent — an agent over the OPC UA MCP tools."""

import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

from shared.llm import get_model

MCP_URL = os.getenv("BATCH_PLANT_MCP_URL", "http://127.0.0.1:8000/mcp")

PROMPT = (
    "You are the Equipment Monitoring agent for a batch plant. "
    "Use the available tools to read current tank material levels and machine "
    "states, then report them clearly with units."
)


def _mcp_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "batch_plant": {
                "transport": "streamable_http",     # exact literal for adapters 0.3.0
                "url": MCP_URL,
            }
        }
    )


async def build_equipment_agent():
    """Load the OPC UA MCP tools and build the agent.

    Async because MCP tool discovery is a network call — the MCP server
    (mcp_server/batch_plant_functions.py) and the simulator behind it must be
    running.
    """
    tools = await _mcp_client().get_tools()
    return create_agent(
        model=get_model(),
        tools=tools,
        name="equipment_agent",
        system_prompt=PROMPT,
    )
