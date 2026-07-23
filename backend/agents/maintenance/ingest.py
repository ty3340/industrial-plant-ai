"""Ingestion pipeline (the WRITER) for the maintenance RAG.

Loads the .md docs, splits them into chunks, embeds them, and (re)writes the
persisted Chroma store. Run whenever the documents change:

    python -m agents.maintenance.ingest
"""
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter
from langchain_chroma import Chroma

from shared.llm import get_embeddings
from agents.maintenance.config import DOCS_PATH, CHROMA_PATH, COLLECTION_NAME




def _load_docs() -> list[Document]:
    """Read every .md file in DOCS_PATH into a Document (plain pathlib — no loader dep)."""
    docs = []
    for path in sorted(Path(DOCS_PATH).glob("*.md")):
        docs.append(Document(page_content=path.read_text(encoding="utf-8"),
                             metadata={"source": path.name}))
    return docs


def ingest() -> int:
    """(Re)build the vector store from the docs. Returns the number of chunks indexed."""
    docs = _load_docs()
    if not docs:
        raise SystemExit(f"No .md files found in {DOCS_PATH}")

    chunks = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

    # Clean slate so re-running is deterministic (like seed_data's DELETE-before-INSERT).
    if Path(CHROMA_PATH).exists():
        shutil.rmtree(CHROMA_PATH)

    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),          # OpenAI embeddings — needs OPENAI_API_KEY
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,       # auto-persists to disk
    )
    return len(chunks)


if __name__ == "__main__":
    load_dotenv()
    n = ingest()
    print(f"Indexed {n} chunks from {DOCS_PATH} -> {CHROMA_PATH}")
