"""
opcua_server.py — a dummy OPC UA server simulating the batch plant, so agents can
read live tank levels + machine states with no real hardware.

Nodes it exposes (clients depend on these exact IDs):
    Tanks   (ns=2): i=328 Tank1Level, i=352 Tank2Level, i=376 Tank3Level  (Double, L)
    Machines(ns=3): s=MixerState, s=ReactorState, s=FillerState          (Int32)
Machine states: 0 DISABLED 1 IDLE 2 RUNNING 3 STARVED 4 BLOCKED 5 PLANNED_DOWN
                6 UNPLANNED_DOWN 7 OTHER

Run in its own terminal:  python data/simulator/opcua_server.py
"""
import asyncio
import os
import random

from asyncua import Server, ua

ENDPOINT = os.getenv("OPC_SERVER_URL", "opc.tcp://0.0.0.0:26543/BatchPlantServer")

# High initial levels on purpose so several batches are possible.
INITIAL_TANK_LEVELS = {1: 8000.0, 2: 13032.0, 3: 18947.0}
INITIAL_MACHINE_STATES = {"MixerState": 2, "ReactorState": 1, "FillerState": 2}


async def main() -> None:
    server = Server()
    await server.init()
    server.set_endpoint(ENDPOINT)
    server.set_server_name("BatchPlantServer")
    server.set_security_policy([ua.SecurityPolicyType.NoSecurity])  # anonymous access

    # Register namespaces so tanks land on index 2 and machines on index 3.
    # ns_tanks =2 and ns_machines =3
    ns_tanks = await server.register_namespace("http://batchplant.example/tanks")
    ns_machines = await server.register_namespace("http://batchplant.example/machines")

    #ensure namespace is right
    assert ns_tanks == 2 and ns_machines == 3, (
        f"Unexpected namespace indices: tanks={ns_tanks}, machines={ns_machines}"
    )

    objects = server.nodes.objects

    # Tank level variables (numeric node IDs in ns=2).

    """
    Objects
    │
    ├── Tank1Level
    │      NodeId = ns=2;i=328
    │      Value  = 7988.4
    │      Type   = Double
    │
    ├── Tank2Level
    │      NodeId = ns=2;i=352
    │      Value  = 13015.2
    │      Type   = Double
    """

    tank_nodes = {}
    tank_node_ids = {1: 328, 2: 352, 3: 376}
    for tank_num, ident in tank_node_ids.items():
        node = await objects.add_variable(
            ua.NodeId(ident, ns_tanks), 
            f"Tank{tank_num}Level",
            INITIAL_TANK_LEVELS[tank_num], 
            ua.VariantType.Double,
        )
        await node.set_writable()
        tank_nodes[tank_num] = node

    # Machine state variables (string node IDs in ns=3).
    for name, initial in INITIAL_MACHINE_STATES.items():
        node = await objects.add_variable(
            ua.NodeId(name, ns_machines), 
            name, 
            initial, 
            ua.VariantType.Int32,
        )
        await node.set_writable()

    print(f"OPC UA simulator running at: {ENDPOINT}")
    print("Press Ctrl+C to stop.")

    async with server:
        while True:
            await asyncio.sleep(2)
            # Gentle random walk so the data looks "live" but stays above recipe needs.
            for node in tank_nodes.values():
                current = await node.read_value()
                await node.write_value(max(500.0, current + random.uniform(-25, 10)))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
