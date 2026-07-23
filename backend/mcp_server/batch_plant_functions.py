"""
batch_plant_functions.py — OPC UA client + FastMCP server for the batch plant.
The ONLY component that talks OPC UA directly; re-exposes plant data as MCP tools
served over streamable HTTP at http://127.0.0.1:8000/mcp.

Run in its own terminal:  python mcp_server/batch_plant_functions.py
"""
import os
import json
from enum import IntEnum
from typing import Dict

from asyncua import Client
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# host/port define where the streamable-HTTP endpoint is served; FastMCP mounts
# it at the "/mcp" path by default.
mcp_server = FastMCP("batch_plant_opcua", host="127.0.0.1", port=8000)

SERVER_URL = os.getenv("OPC_SERVER_URL", "opc.tcp://localhost:26543/BatchPlantServer")


class NodeIds:
    """OPC UA node addresses — must match data/simulator/opcua_server.py."""
    TANK1_LEVEL_NODE_ID = "ns=2;i=328"
    TANK2_LEVEL_NODE_ID = "ns=2;i=352"
    TANK3_LEVEL_NODE_ID = "ns=2;i=376"
    MIXER_STATE_NODE_ID = "ns=3;s=MixerState"
    REACTOR_STATE_NODE_ID = "ns=3;s=ReactorState"
    FILLER_STATE_NODE_ID = "ns=3;s=FillerState"


class MachineState(IntEnum):
    DISABLED = 0
    IDLE = 1
    RUNNING = 2
    STARVED = 3
    BLOCKED = 4
    PLANNED_DOWNTIME = 5
    UNPLANNED_DOWNTIME = 6
    OTHER = 7


class OPCUABatchPlantClient:
    """OPC UA client for batch plant operations."""

    def __init__(self, server_url: str = None):
        self.server_url = server_url or SERVER_URL
        self.client = None

    async def connect(self):
        self.client = Client(self.server_url)
        await self.client.connect()          # anonymous — no username/password

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def get_material_availability(self) -> Dict[str, float]:
        """Read the three tank levels (litres)."""
        try:
            tank1 = await self.client.get_node(NodeIds.TANK1_LEVEL_NODE_ID).read_value()
            tank2 = await self.client.get_node(NodeIds.TANK2_LEVEL_NODE_ID).read_value()
            tank3 = await self.client.get_node(NodeIds.TANK3_LEVEL_NODE_ID).read_value()
            return {
                "tank1_material_level": float(tank1),
                "tank2_material_level": float(tank2),
                "tank3_material_level": float(tank3),
            }
        except Exception as e:
            print(f"Error reading material levels: {e}")
            raise

    async def get_machine_states(self) -> Dict[str, str]:
        """Read the three machine states, converting the int codes to strings."""
        try:
            mixer = await self.client.get_node(NodeIds.MIXER_STATE_NODE_ID).read_value()
            reactor = await self.client.get_node(NodeIds.REACTOR_STATE_NODE_ID).read_value()
            filler = await self.client.get_node(NodeIds.FILLER_STATE_NODE_ID).read_value()
            return {
                "mixer_state": self._int_to_state_string(mixer),
                "reactor_state": self._int_to_state_string(reactor),
                "filler_state": self._int_to_state_string(filler),
            }
        except Exception as e:
            print(f"Error reading machine states: {e}")
            raise

    def _int_to_state_string(self, state_int: int) -> str:
        """Map an OPC UA int code to a state name, or a sentinel if unknown."""
        try:
            return MachineState(state_int).name.lower()
        except ValueError:
            return f"unknown_state_{state_int}"


# --- MCP tools (the decorator registers each and returns the plain function,
#     so they stay directly awaitable for in-process smoke tests) ---

@mcp_server.tool()
async def get_material_availability() -> str:
    """Return current tank material levels as a JSON string."""
    client = OPCUABatchPlantClient()
    try:
        await client.connect()
        return json.dumps(await client.get_material_availability(), indent=2)
    finally:
        await client.disconnect()


@mcp_server.tool()
async def get_machine_states() -> str:
    """Return current machine states as a JSON string."""
    client = OPCUABatchPlantClient()
    try:
        await client.connect()
        return json.dumps(await client.get_machine_states(), indent=2)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    # Serves the tools at http://127.0.0.1:8000/mcp
    mcp_server.run(transport="streamable-http")
