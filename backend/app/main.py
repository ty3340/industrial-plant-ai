import asyncio
import logging
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.models.schemas import QueryRequest, QueryResponse
from agents.orchestrator import answer_query

load_dotenv()  # must run before agent imports read OPENAI_API_KEY etc.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
log = logging.getLogger("batch_plant.api")

QUERY_TIMEOUT_S = int(os.getenv("QUERY_TIMEOUT_S", "180"))
OPC_SERVER_URL = os.getenv("OPC_SERVER_URL", "opc.tcp://localhost:26543/BatchPlantServer")
MCP_URL = os.getenv("BATCH_PLANT_MCP_URL", "http://127.0.0.1:8000/mcp")

app = FastAPI(title="Agentic AI for Industrial Systems")

# Allow the Vite dev server to call this API directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/deep")
async def health_deep():
    """Probe each upstream dependency; 503 with per-dependency detail if any is down."""
    from asyncua import Client as OpcClient
    import httpx

    checks = {}
    try:
        opc = OpcClient(OPC_SERVER_URL)
        await asyncio.wait_for(opc.connect(), timeout=5)
        await opc.disconnect()
        checks["opcua_simulator"] = "ok"
    except Exception as e:
        checks["opcua_simulator"] = f"down ({e.__class__.__name__})"

    try:
        async with httpx.AsyncClient() as hc:
            # Any HTTP response (even 4xx) proves the MCP server is listening;
            # only a connection error means it's down.
            await hc.get(MCP_URL, timeout=5)
        checks["mcp_server"] = "ok"
    except Exception as e:
        checks["mcp_server"] = f"down ({e.__class__.__name__})"

    healthy = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ok" if healthy else "degraded", "checks": checks},
    )


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    log.info("query received: %r", req.question)
    t0 = time.perf_counter()
    try:
        resp = await asyncio.wait_for(answer_query(req.question), timeout=QUERY_TIMEOUT_S)
    except TimeoutError:
        log.error("query timed out after %ss: %r", QUERY_TIMEOUT_S, req.question)
        raise HTTPException(
            status_code=504,
            detail=f"Query timed out after {QUERY_TIMEOUT_S}s — plant data sources may be slow or down.",
        )
    except Exception:
        log.exception("query failed: %r", req.question)
        raise HTTPException(
            status_code=502,
            detail="Query failed — check the OPC UA simulator (:26543) and MCP server (:8000); see /health/deep.",
        )
    log.info("query answered in %.1fs", time.perf_counter() - t0)
    return resp
