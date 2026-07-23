"""Reader tool for the maintenance RAG — semantic search over the persisted store."""
from langchain_core.tools import tool
from langchain_chroma import Chroma

from shared.llm import get_embeddings
from agents.maintenance.config import CHROMA_PATH, COLLECTION_NAME

_store_instance = None


def get_store() -> Chroma:
    global _store_instance
    if _store_instance is None:
        _store_instance = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_PATH,
        )
    return _store_instance



@tool
def search_maintenance_docs(query: str) -> str:
    """Search the equipment maintenance documents (preventive-maintenance schedules,
    activity reports, and calibration certificates) for information relevant to the
    query. Use for questions about maintenance timing, equipment health, calibration
    status, spare parts, or past repairs. Returns the most relevant excerpts."""
    
    docs = get_store().similarity_search(query, k=4)
    if not docs:
        return "No relevant maintenance documentation found."
    return "\n\n---\n\n".join(
        f"[{d.metadata.get('source', 'unknown')}]\n{d.page_content.strip()}"
        for d in docs
    )
