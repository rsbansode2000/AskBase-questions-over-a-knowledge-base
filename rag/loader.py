"""PDF loading helpers."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(path: Path):
    """Load a PDF into page-aware LangChain documents."""
    try:
        documents = PyPDFLoader(str(path)).load()
    except Exception as exc:
        raise ValueError("The PDF appears to be corrupted or unreadable.") from exc
    if not any(document.page_content.strip() for document in documents):
        raise ValueError("The PDF does not contain extractable text.")
    return documents
