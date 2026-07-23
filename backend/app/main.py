from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.models.schemas import QueryRequest, QueryResponse
from agents.orchestrator import answer_query

load_dotenv()  # must run before agent imports read OPENAI_API_KEY etc.

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


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    return await answer_query(req.question)
