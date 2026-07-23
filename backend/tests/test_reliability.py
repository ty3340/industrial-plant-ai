"""Failure-path tests for /query — errors must map to clean HTTP statuses."""
import asyncio

from fastapi.testclient import TestClient

import app.main as main
from shared.models.schemas import QueryResponse

client = TestClient(main.app)


def test_query_maps_upstream_failure_to_502(monkeypatch):
    async def broken_answer(question: str) -> QueryResponse:
        raise ConnectionRefusedError("simulator down")
    monkeypatch.setattr(main, "answer_query", broken_answer)   # patch where it's USED

    resp = client.post("/query", json={"question": "Can we produce 1 batch of Product A?"})
    assert resp.status_code == 502
    assert "health/deep" in resp.json()["detail"]


def test_query_times_out_to_504(monkeypatch):
    async def slow_answer(question: str) -> QueryResponse:
        await asyncio.sleep(10)
    monkeypatch.setattr(main, "answer_query", slow_answer)
    monkeypatch.setattr(main, "QUERY_TIMEOUT_S", 1)   # don't wait 180s in a test

    resp = client.post("/query", json={"question": "slow question"})
    assert resp.status_code == 504
