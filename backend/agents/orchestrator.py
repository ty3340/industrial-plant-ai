"""Orchestrator — a LangGraph supervisor delegating to the material, equipment,
and maintenance agents. Exposes answer_query(question), which app/main.py calls.
"""

from langgraph_supervisor import create_supervisor
from shared.llm import get_model
from shared.models.schemas import QueryResponse
from agents.material.agent import build_material_agent
from agents.equipment.agent import build_equipment_agent
from agents.maintenance.agent import build_maintenance_agent


SUPERVISOR_PROMPT = (
    "You are the orchestrator for a batch plant. You manage three specialists:\n"
    "  - material_agent: computes litres of each raw material a production run needs.\n"
    "  - equipment_agent: reports live tank levels (litres) and machine states.\n"
    "  - maintenance_agent: checks maintenance schedules, calibration status, equipment "
    "reliability, and overdue/expired items from the maintenance documents.\n"
    "Raw-material-to-tank mapping: Material A is in tank 1, Material B in tank 2, "
    "Material C in tank 3.\n\n"
    "Routing:\n"
    "  - Maintenance / calibration / reliability / equipment-health questions → maintenance_agent.\n"
    "  - Material-requirement questions → material_agent.\n"
    "  - Live tank levels / machine states → equipment_agent.\n\n"
    "For a PRODUCTION-FEASIBILITY question (e.g. 'can we produce N batches of Product X?'), "
    "delegate to ALL THREE: material_agent for the requirements, equipment_agent for current "
    "tank levels and machine states, and maintenance_agent for maintenance/calibration/"
    "reliability blockers. Production is POSSIBLE only if (a) every material's requirement is "
    "met by its tank level, (b) machines are usable, AND (c) maintenance_agent reports no "
    "BLOCK condition (imminent PM conflict, health below minimum, expired product-critical "
    "calibration, or critical reliability issue). Surface any maintenance WARNING/ALARM even "
    "when production is still possible.\n"
    "Give a clear decision with the numbers and reasoning, and end with a final line in "
    "exactly this format:\n"
    "VERDICT: POSSIBLE   or   VERDICT: NOT POSSIBLE"
)



_graph = None   # compiled supervisor, built once (lazily) on first request


async def _get_graph():
    global _graph
    if _graph is None:
        equipment_agent = await build_equipment_agent()      # loads MCP tools (async)
        workflow = create_supervisor(
            [build_material_agent(), equipment_agent, build_maintenance_agent()],
            model=get_model(),
            prompt=SUPERVISOR_PROMPT,
        )
        _graph = workflow.compile()
    return _graph


async def answer_query(question: str) -> QueryResponse:
    graph = await _get_graph()
    result = await graph.ainvoke({"messages": [{"role": "user", "content": question}]})
    return QueryResponse(answer=result["messages"][-1].content)


