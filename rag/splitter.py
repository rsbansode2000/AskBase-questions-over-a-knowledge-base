"""Document chunking configuration."""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    """Split pages while preserving page metadata for source citations."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata["chunk_number"] = index
        chunk.metadata["page_number"] = int(chunk.metadata.get("page", 0)) + 1
    return chunks
