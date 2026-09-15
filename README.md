# Agentic AI for Industrial Systems — Batch Plant Assistant

A multi-agent AI system that answers natural-language questions about a
simulated chemical **batch plant** — including the headline question:

> _"Can we produce N batches of Product X right now?"_

To answer, a supervisor agent coordinates three specialists that pull from three
different real-world data sources — a recipe database, live machine/tank
telemetry over the **OPC UA** industrial protocol, and a set of maintenance
documents searched via **RAG**. The result is a decision with the numbers,
the reasoning, and a final `VERDICT: POSSIBLE` / `NOT POSSIBLE`.

This is a learning / portfolio project: the _architecture_ mirrors how real
industrial-AI systems are built, while the _maturity_ is prototype (see
[Architecture & Limitations](#architecture--limitations)).

---

## Architecture

```
  Browser
  React + Vite  (:5173)
        │  HTTP POST /query   { "question": "..." }
        ▼
  FastAPI  (:8001)                     ← the only REST layer
        │  in-process call: answer_query(question)
        ▼
  Orchestrator  (LangGraph supervisor)  ← routes in natural language, not URLs
        ├────────────────┬───────────────────────────┐
        ▼                ▼                           ▼
  material_agent    equipment_agent            maintenance_agent
        │                │                           │
        │                │  MCP tools (streamable     │  RAG retrieval
        │                │  HTTP)                     │
        ▼                ▼                           ▼
  SQLite            FastMCP server (:8000)      Chroma vector store
  plant.db          │  OPC UA client            (maintenance/*.md)
  (recipes)         ▼
                    OPC UA simulator (:26543)
                    (live tank levels + machine states)
```

**Why so few HTTP endpoints?** The business logic lives in the orchestrator +
agents, not in the API. FastAPI is a thin doorway that exposes `answer_query()`
over HTTP; the same function is called directly by the CLI and the eval harness
with no web server involved. Routing between specialists happens in the
supervisor's prompt (natural language), which is why one `/query` endpoint
covers what would otherwise be many REST routes.

### The four processes

| Process          | Port  | Framework             | Role                                        |
| ---------------- | ----- | --------------------- | ------------------------------------------- |
| React frontend   | 5173  | Vite                  | Chat UI                                     |
| REST API         | 8001  | **FastAPI** / uvicorn | Exposes `/query`, `/health`, `/health/deep` |
| MCP server       | 8000  | **FastMCP** (`mcp`)   | Wraps OPC UA reads as MCP tools             |
| OPC UA simulator | 26543 | **asyncua**           | Fake plant emitting live telemetry          |

> Note: the MCP server owns port **8000**, so the FastAPI app runs on **8001**.

---

## Tech stack

- **Orchestration:** LangGraph (`langgraph-supervisor`), LangChain 1.0
- **LLM:** OpenAI `gpt-4.1` (configurable), `text-embedding-3-small` for RAG
- **Tools protocol:** MCP via `langchain-mcp-adapters` + `FastMCP`
- **Industrial protocol:** OPC UA via `asyncua`
- **RAG:** Chroma + `langchain-text-splitters`
- **API:** FastAPI + Pydantic + uvicorn
- **Data:** SQLite (recipes)
- **Frontend:** React + Vite
- **Testing:** pytest (24 tests) + a custom eval harness

---

## Prerequisites

- **Python 3.12**
- **Node.js 18+** (for the frontend)
- An **OpenAI API key**

---

## Setup

All backend commands assume the repo root as the working directory unless noted.

### 1. Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt   # for tests
```

### 2. Environment variables

Copy the example env file to a root `.env` and fill in your key:

```powershell
Copy-Item backend/.env.example .env
```

At minimum set `OPENAI_API_KEY`. `python-dotenv` walks up the tree, so one root
`.env` serves every subsystem. Optional knobs: `LLM_MODEL`, `OPC_SERVER_URL`,
`QUERY_TIMEOUT_S` (default 180), `PLANT_DB_PATH`.

### 3. Generate the two data artifacts

These are **git-ignored** and must be built once (and after any data change):

```powershell
cd backend
python data/static_data/seed_data.py        # builds plant.db (recipes)
python -m agents.maintenance.ingest          # builds the Chroma vector store
```

### 4. Frontend dependencies

```powershell
cd frontend
npm install
```

---

## Running the app

Start the four processes in this order, each in its own terminal, with the
venv activated for the backend ones.

**Terminal 1 — OPC UA simulator (:26543)**

```powershell
cd backend
python data/simulator/opcua_server.py
```

**Terminal 2 — MCP server (:8000)**

```powershell
cd backend
python mcp_server/batch_plant_functions.py
```

**Terminal 3 — FastAPI (:8001)**

```powershell
cd backend
uvicorn app.main:app --port 8001
```

**Terminal 4 — Frontend (:5173)**

```powershell
cd frontend
npm run dev
```

Open <http://localhost:5173> and ask a question. The first query is slow — the
supervisor graph is compiled lazily on the first request.

### Don't want the UI?

The same brain is reachable without the frontend or FastAPI:

```powershell
cd backend
python -m app.cmd "Can we produce 3 batches of Product A?"   # one-shot
python -m app.cmd                                            # interactive REPL
```

(Still needs the simulator + MCP server running.)

---

## Run with Docker (one command)

The whole stack runs in containers — no need for four separate terminals.

**Windows + OneDrive note:** if the project sits on your Desktop, Windows keeps it
inside OneDrive, and Docker can't build from a OneDrive-synced folder. The included
`docker-run.ps1` sidesteps this by building from a local copy — run it instead of
`docker compose up`:

```powershell
.\docker-run.ps1
```

Then open <http://localhost:5173>. Stop the stack with:

```powershell
docker compose -f "C:\dev\Industrial-AI-Project\docker-compose.yml" down
```

---

## Example questions

- `Can we produce 3 batches of Product A?` — full feasibility (all three agents)
- `What are the current tank levels?` — equipment agent
- `How much Material B does one batch of Product C need?` — material agent
- `Are there any overdue calibrations or maintenance blockers?` — maintenance agent

---

## API reference

| Method | Path           | Purpose                                                              |
| ------ | -------------- | -------------------------------------------------------------------- |
| `GET`  | `/health`      | Liveness — is the API process up? (instant, no dependencies)         |
| `GET`  | `/health/deep` | Readiness — probes the OPC UA sim + MCP server; `503` if any is down |
| `POST` | `/query`       | `{ "question": "..." }` → `{ "answer": "..." }`                      |

`/query` failure modes are mapped to clean statuses: **504** on timeout,
**502** on an upstream failure (with an actionable message), **422** on a
missing/empty question.

---

## Testing & evaluation

**Unit / integration tests** (no external services needed — upstreams are mocked):

```powershell
cd backend
python -m pytest -q          # 24 tests
```

**Eval harness** — runs feasibility cases end-to-end and checks the verdict.
Requires the simulator + MCP server running, the vector store built, and a
freshly restarted simulator (tanks at full initial levels):

```powershell
cd backend
python -m eval.run_eval
```

Cases live in [`backend/eval/eval_cases.json`](backend/eval/eval_cases.json).

---

## Project structure

```
Industrial-AI-Project/
├── backend/
│   ├── app/                  # FastAPI app + CLI (thin layer over answer_query)
│   ├── agents/
│   │   ├── orchestrator.py   # LangGraph supervisor
│   │   ├── material/         # recipe math over SQLite
│   │   ├── equipment/        # live telemetry via MCP tools
│   │   └── maintenance/      # RAG over maintenance docs (ingest + agent)
│   ├── mcp_server/           # FastMCP server wrapping the OPC UA client
│   ├── data/
│   │   ├── simulator/        # asyncua OPC UA simulator
│   │   ├── static_data/      # seed_data.py → plant.db
│   │   └── maintenance/      # source .md docs + generated chroma_db/
│   ├── shared/               # llm.py, pydantic schemas
│   ├── eval/                 # eval harness + cases
│   └── tests/                # pytest suite
└── frontend/                 # React + Vite chat UI
```

---

## Architecture & Limitations

The architecture is deliberately industry-aligned: a real industrial protocol
(OPC UA), the current agent-tooling standard (MCP), a supervisor/specialist
multi-agent pattern, and an eval harness. What separates this **prototype**
from a production industrial system is intentional and worth naming:

- **Security.** No API authentication; anonymous OPC UA (real plants require
  certificate-based encryption per IEC 62443); an open MCP endpoint. Safe on
  localhost, not beyond it.
- **Trust model.** An LLM's free-text verdict should not gate real production
  decisions. Production would add deterministic guardrails around the LLM, a
  human in the loop, and a far larger eval set (there are 3 cases today).
- **Observability.** Basic request logging exists; there is no distributed
  tracing (e.g. LangSmith / OpenTelemetry) to explain _why_ an agent answered
  as it did.

- **Operations.** Containerized with Docker Compose, but no CI pipeline yet. Data
  lives in local SQLite/Chroma

- **State.** Each query is stateless — no conversation memory across turns.

### Roadmap

- [ ] Structured `verdict` field in `QueryResponse` (+ a green/red badge in the UI)
- [ ] Expand the eval set (maintenance-blocker and machine-down `NOT POSSIBLE` cases)
- [ ] Dockerize the four processes (`docker-run.ps1` / `docker compose`)
- [ ] Structured logging / tracing
- [ ] Conversation memory and response streaming
