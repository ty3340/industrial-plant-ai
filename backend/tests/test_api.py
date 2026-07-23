
from fastapi.testclient import TestClient

import app.main as main
from shared.models.schemas import QueryResponse

client = TestClient(main.app)


def test_query_wires_through_to_orchestrator(monkeypatch):
    async def fake_answer(question: str) -> QueryResponse:
        return QueryResponse(answer=f"decision for: {question}")
    monkeypatch.setattr(main, "answer_query", fake_answer)   # patch where it's USED

    resp = client.post("/query", json={"question": "Can we make 3 batches of Product A?"})
    assert resp.status_code == 200
    assert resp.json()["answer"] == "decision for: Can we make 3 batches of Product A?"


def test_query_rejects_missing_question():
    resp = client.post("/query", json={})
    assert resp.status_code == 422


