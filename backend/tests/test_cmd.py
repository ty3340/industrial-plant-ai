import app.cmd as cmd
from shared.models.schemas import QueryResponse


def test_cmd_one_shot_prints_answer(monkeypatch, capsys):
    async def fake_answer(question: str) -> QueryResponse:
        return QueryResponse(answer=f"ANSWER for: {question}")
    monkeypatch.setattr(cmd, "answer_query", fake_answer)         # patch where it's used
    monkeypatch.setattr("sys.argv", ["cmd", "Can we make 3 batches of Product A?"])

    cmd.main()

    out = capsys.readouterr().out
    assert "ANSWER for: Can we make 3 batches of Product A?" in out
