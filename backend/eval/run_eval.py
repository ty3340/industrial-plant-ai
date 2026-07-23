"""Eval harness for the batch-plant orchestrator.

Runs each case in eval_cases.json through answer_query, extracts the VERDICT,
compares to the expected value, prints a report, and exits non-zero on any fail.

Precondition: simulator + MCP server running, the maintenance vector store built
(python -m agents.maintenance.ingest), OPENAI_API_KEY set, and the simulator
freshly restarted (tanks at full initial levels).

"""
import asyncio
import json
import os
import re
import sys

from dotenv import load_dotenv

from agents.orchestrator import answer_query

CASES_PATH = os.path.join(os.path.dirname(__file__), "eval_cases.json")


def extract_verdict(answer: str) -> str:
    """Return 'POSSIBLE', 'NOT POSSIBLE', or 'UNKNOWN' from an answer string."""
    m = re.search(r"VERDICT:\s*(NOT\s+POSSIBLE|POSSIBLE)", answer, re.IGNORECASE)
    if m:
        return "NOT POSSIBLE" if "NOT" in m.group(1).upper() else "POSSIBLE"
    low = answer.lower()                       # fallback (order matters!)
    if "not possible" in low:
        return "NOT POSSIBLE"
    if "possible" in low:
        return "POSSIBLE"
    return "UNKNOWN"


async def main() -> int:
    load_dotenv()
    with open(CASES_PATH) as f:
        cases = json.load(f)

    passed = 0
    for i, case in enumerate(cases, 1):
        resp = await answer_query(case["question"])
        got = extract_verdict(resp.answer)
        expected = case["expect"].upper()
        ok = got == expected
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] case {i}: expected {expected!r}, got {got!r}")
        print(f"        Q: {case['question']}")
        if not ok:
            print(f"        A: {resp.answer.strip()[:300]}")

    print(f"\n{passed}/{len(cases)} passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
