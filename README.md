# Company Q&A Assistant

A modern **Flask + LangChain + Ollama Retrieval-Augmented Generation (RAG)** application that allows users to ask questions about company documents. The application automatically generates embeddings for uploaded PDFs, stores them in **ChromaDB**, and answers questions using **Gemma 2B** with semantic search.

---

## Application Preview

<img width="950" height="674" alt="Screenshot 2026-09-10 115639" src="https://github.com/user-attachments/assets/848c6b5d-7c10-4ef6-a2f8-fe2f2fe64547" />

---

## Features

- 🤖 AI-powered Question & Answer system
- 📄 Upload company PDF documents
- 🔍 Semantic Search using Chroma Vector Database
- 🧠 Retrieval-Augmented Generation (RAG)
- ⚡ Ollama Embeddings (`nomic-embed-text`)
- 💬 Chat interface similar to ChatGPT
- 📚 Source page and chunk references
- 📊 Confidence score for retrieved context
- 🔐 Admin Dashboard
- 📱 Fully responsive Bootstrap 5 UI
- ♻️ Automatic embedding reuse using SHA-256 hash comparison
- 🗂️ Persistent Chroma Vector Database
- 🚀 Fast document retrieval

---

# Project Architecture

```
                        Admin Uploads PDF
                                │
                                ▼
                     PyPDFLoader (Load PDF)
                                │
                                ▼
            RecursiveCharacterTextSplitter
                                │
                                ▼
      Ollama Embeddings (nomic-embed-text)
                                │
                                ▼
                  Chroma Vector Database
                                │
                                ▼
                 Similarity Search (k = 3)
                                │
                                ▼
                 ChatOllama (gemma:2b)
                                │
                                ▼
                      AI Generated Answer
```

---

# Project Structure

```
Company-QA-Assistant/
│
├── app.py
│
├── rag/
│   ├── loader.py
│   ├── splitter.py
│   ├── embeddings.py
│   ├── vectorstore.py
│   └── chat.py
│
├── templates/
│   ├── index.html
│   ├── chat.html
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── 404.html
│   └── 500.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── uploads/
├── chroma_db/
├── metadata.json
├── requirements.txt
└── README.md
```

---

# Technologies Used

- Python
- Flask
- LangChain
- Ollama
- ChromaDB
- PyPDFLoader
- RecursiveCharacterTextSplitter
- Bootstrap 5
- HTML
- CSS
- JavaScript

---

# How It Works

1. Admin logs into the dashboard.
2. Admin uploads a PDF document.
3. Existing PDF (if any) is automatically deleted.
4. PDF is loaded using **PyPDFLoader**.
5. Document is split into chunks using **RecursiveCharacterTextSplitter**.
6. Embeddings are generated using **nomic-embed-text**.
7. Embeddings are stored in **ChromaDB**.
8. Metadata is saved in **metadata.json**.
9. Users can ask questions from the uploaded document.
10. Relevant chunks are retrieved using semantic similarity search.
11. **Gemma 2B** generates answers based only on retrieved context.

---

---

# Setup

Create a virtual environment

```powershell
python -m venv .venv
```

Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies

```powershell
pip install -r requirements.txt
```

Install Ollama models

```powershell
ollama pull nomic-embed-text
ollama pull gemma:2b
```

Run Flask application

```powershell
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# Admin Credentials

Email

```
user@123
```

Password

```
user@123
```

---

# Document Lifecycle

- Supports PDF files up to **25 MB**
- Only one PDF is active at a time
- Uploading a new PDF automatically removes the previous document
- SHA-256 hash comparison prevents unnecessary embedding generation
- Existing embeddings are reused whenever the uploaded file is unchanged
- A new document automatically recreates the Chroma collection and updates metadata
- Admin can rebuild embeddings or delete the complete knowledge base

---

# Future Improvements

- Support DOCX and TXT documents
- Streaming LLM responses
- User authentication
- Conversation memory
- Multi-document knowledge base
- Citation highlighting
- Docker deployment
- AWS deployment
- Role-based access control

---

# Author

**Rohit Bansode**

GitHub: https://github.com/rsbansode2000
