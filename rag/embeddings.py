"""Ollama embedding model configuration."""

from langchain_ollama import OllamaEmbeddings

EMBEDDING_MODEL = "nomic-embed-text"


def create_embeddings() -> OllamaEmbeddings:
    """Create the configured Ollama embedding client."""
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url="http://localhost:11434",
    )
