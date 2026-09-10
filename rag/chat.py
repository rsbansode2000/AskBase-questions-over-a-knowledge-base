"""Context retrieval and Ollama answer generation."""

from __future__ import annotations

from datetime import datetime

from langchain_ollama import ChatOllama

from .prompt import RAG_PROMPT
from .vectorstore import VectorStoreService


class ChatService:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.llm = ChatOllama(model="gemma:2b", temperature=0, base_url="http://localhost:11434")

    def answer(self, question: str) -> dict:
        store = self.vector_store.get_store()
        results = store.similarity_search_with_relevance_scores(question, k=3)
        if not results:
            return {
                "answer": "I could not find this information in the uploaded document.",
                "sources": [],
                "context": "",
            }
        context = "\n\n".join(document.page_content for document, _score in results)
        prompt = RAG_PROMPT.format(context=context, question=question)
        response = self.llm.invoke(prompt)
        status = self.vector_store.status()
        sources = [
            {
                "document": status.get("file_name"),
                "page": document.metadata.get("page_number", int(document.metadata.get("page", 0)) + 1),
                "chunk": document.metadata.get("chunk_number", index),
                "confidence": round(float(score), 3),
                "relevant_chunk": document.page_content[:240],
            }
            for index, (document, score) in enumerate(results, start=1)
        ]
        return {
            "answer": str(response.content).strip(),
            "context": context,
            "sources": sources,
            "timestamp": datetime.now().strftime("%H:%M"),
        }
