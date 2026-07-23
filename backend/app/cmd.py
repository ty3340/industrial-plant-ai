"""CLI for the batch-plant orchestrator (runs the graph in-process).

    python -m app.cmd "Can we produce 3 batches of Product A?"   # one-shot
    python -m app.cmd                                            # interactive REPL

Needs the simulator (:26543) and MCP server (:8000) running, plus OPENAI_API_KEY.
"""


import argparse
import asyncio

from dotenv import load_dotenv
from agents.orchestrator import answer_query


async def _ask(question: str) -> None:
    resp = await answer_query(question)
    print(resp.answer)


async def _repl() -> None:
    print("Batch-plant assistant — ask a question (Ctrl+C to quit).")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return
        if question:
            await _ask(question)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Ask the batch plant a question.")
    parser.add_argument("question", nargs="?",
                        help="One-shot question; omit for interactive mode.")
    args = parser.parse_args()

    asyncio.run(_ask(args.question) if args.question else _repl())


if __name__ == "__main__":
    main()