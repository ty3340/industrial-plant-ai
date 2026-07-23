"""RAG-specific config: where the maintenance docs and vector store live.
Model factories live in shared/llm.py.
"""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))


# Source markdown documents (committed; you edit these).
DOCS_PATH = os.getenv(
    "MAINTENANCE_DOCS_PATH",
    os.path.join(_REPO_ROOT, "data", "maintenance"),
)

# Persisted Chroma vector store (generated; git-ignored).
CHROMA_PATH = os.getenv(
    "MAINTENANCE_CHROMA_PATH",
    os.path.join(_REPO_ROOT, "data", "maintenance", "chroma_db"),
)

COLLECTION_NAME = "maintenance_docs"
