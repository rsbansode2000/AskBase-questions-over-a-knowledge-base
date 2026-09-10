# Company Q&A Assistant

A Flask Retrieval-Augmented Generation application for asking questions about one active company PDF.

## Architecture

- `app.py`: Flask routes, demo admin session, upload policy, and chat history.
- `rag/loader.py`: `PyPDFLoader` page-aware PDF extraction.
- `rag/splitter.py`: `RecursiveCharacterTextSplitter` chunking.
- `rag/embeddings.py`: `OllamaEmbeddings(model="nomic-embed-text")`.
- `rag/vectorstore.py`: persistent `Chroma` collection lifecycle and `metadata.json`.
- `rag/chat.py`: k=3 similarity retrieval and `ChatOllama(model="gemma:2b")` answers.
- `templates/`: Bootstrap 5 public, chat, login, dashboard, upload, and error pages.
- `static/`: responsive CSS and chat/upload JavaScript.

## Sample chat experience

The chat page shows the active knowledge base, embedding model, chunk count, and upload time above the conversation. Each answer includes the source pages and chunks used to generate it.

| Current knowledge base | Chunks | Embedding model | Last uploaded |
| --- | ---: | --- | --- |
| `SQL.pdf` | 96 | `nomic-embed-text` | `2026-09-10 11:01` |

> **You · 11:55**  
> explain select query

> **Assistant · 11:55**  
> Sure, here's the answer to your question:
> 
> **What is Query Optimization?**  
> Query optimization is a technique used to improve the execution speed of database queries by optimizing the execution plan.
> 
> **What is the Difference Between Stored Procedure and Function in SQL?**  
> A stored procedure is a pre-compiled query stored in the database, while a function is a reusable block of SQL code that can be called multiple times.
> 
> **What is Nested Query?**  
> A nested query is a query written inside another query to retrieve data based on the result of the inner query.

_Retrieved sources appear below every answer, including the document name, page, chunk, and confidence score._

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install Ollama, start it, and pull the exact models:

```powershell
ollama pull nomic-embed-text
ollama pull gemma:2b
```

Run the app:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

## Admin demo credentials

- Email: `user@123`
- Password: `user@123`

## Document lifecycle

Only PDF files up to 25 MB are accepted. The active source is stored in `uploads/`; uploading a new PDF removes the previous PDF. Its SHA-256 hash is compared with `metadata.json`. Matching content reuses the existing `chroma_db/` collection without regenerating embeddings. A changed PDF creates a fresh `company_documents` collection and updates metadata.

The admin dashboard also supports rebuilding embeddings and deleting the complete knowledge base, including the PDF, Chroma collection, metadata, and session chat history.
