from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
import os

LLM_MODEL = os.getenv("LLM_MODEL", "openai:gpt-4.1")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def get_model():
    return init_chat_model(
        LLM_MODEL,
        temperature=0.2,
        timeout = 60,
        max_retries = 3,
    )


def get_embeddings():
    return OpenAIEmbeddings(model=EMBED_MODEL)