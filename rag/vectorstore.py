"""Persistent Chroma lifecycle and document metadata for the RAG app."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from langchain_chroma import Chroma

from .embeddings import EMBEDDING_MODEL, create_embeddings
from .loader import load_pdf
from .splitter import split_documents

COLLECTION_NAME = "company_documents"
METADATA_FILENAME = "metadata.json"


class VectorStoreService:
    """Keep one uploaded PDF and one persistent Chroma collection in sync."""

    def __init__(self, persist_directory: Path, upload_directory: Path):
        self.persist_directory = Path(persist_directory)
        self.upload_directory = Path(upload_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        self.embeddings = create_embeddings()
        self.vector_store: Chroma | None = None

    @property
    def metadata_path(self) -> Path:
        return self.persist_directory.parent / METADATA_FILENAME

    def load_metadata(self) -> dict:
        try:
            return json.loads(self.metadata_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def save_metadata(self, metadata: dict) -> None:
        self.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _new_store(self) -> Chroma:
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_directory),
        )

    def load_vector_store(self) -> Chroma:
        if self.vector_store is None:
            self.vector_store = self._new_store()
        return self.vector_store

    def process_uploaded_file(self, path: Path, display_name: str, digest: str, force: bool = False) -> dict:
        """Index a new PDF or reuse the existing collection for the same hash."""
        existing = self.load_metadata()
        active_path = self.upload_directory / str(existing.get("stored_name", ""))
        collection_ready = bool(existing.get("embedded")) and active_path.is_file()
        if not force and existing.get("hash") == digest and collection_ready:
            existing["file_name"] = display_name
            self.save_metadata(existing)
            self.vector_store = self._new_store()
            return {**self.status(), "skipped": True, "already_embedded": True}

        documents = load_pdf(path)
        chunks = split_documents(documents)
        if not chunks:
            raise ValueError("The PDF does not contain searchable text.")

        self.delete_collection(remove_metadata=False, remove_upload=False)
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=str(self.persist_directory),
        )
        metadata = {
            "file_name": display_name,
            "stored_name": path.name,
            "hash": digest,
            "embedded": True,
            "chunk_count": len(chunks),
            "collection_name": COLLECTION_NAME,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "page_count": len(documents),
            "embedding_model": EMBEDDING_MODEL,
        }
        self.save_metadata(metadata)
        return {**self.status(), "skipped": False, "already_embedded": False}

    def get_store(self) -> Chroma:
        if not self.load_metadata().get("embedded"):
            raise RuntimeError("No embedded document is ready for chat.")
        return self.load_vector_store()

    def delete_collection(self, remove_metadata: bool = True, remove_upload: bool = True) -> None:
        """Delete vectors, metadata, and the one active upload when requested."""
        try:
            self._new_store().delete_collection()
        except Exception:
            self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.vector_store = None
        if remove_upload:
            for file_path in self.upload_directory.glob("*"):
                if file_path.is_file():
                    file_path.unlink(missing_ok=True)
        if remove_metadata:
            self.metadata_path.unlink(missing_ok=True)

    def status(self) -> dict:
        metadata = self.load_metadata()
        stored_name = str(metadata.get("stored_name", ""))
        upload_exists = bool(stored_name) and (self.upload_directory / stored_name).is_file()
        ready = bool(metadata.get("embedded")) and upload_exists
        return {
            "file_name": metadata.get("file_name"),
            "filename": metadata.get("file_name"),
            "uploaded": upload_exists,
            "embedded": ready,
            "indexed": ready,
            "embedding_status": "Ready for Chat" if ready else "Waiting for document",
            "chunk_count": metadata.get("chunk_count", 0),
            "chunks": metadata.get("chunk_count", 0),
            "page_count": metadata.get("page_count", 0),
            "pages": metadata.get("page_count", 0),
            "uploaded_at": metadata.get("uploaded_at"),
            "hash": metadata.get("hash"),
            "collection_name": metadata.get("collection_name", COLLECTION_NAME),
            "embedding_model": metadata.get("embedding_model", EMBEDDING_MODEL),
            "llm_model": "gemma:2b",
            "database": "Connected" if ready else "Not initialized",
        }
