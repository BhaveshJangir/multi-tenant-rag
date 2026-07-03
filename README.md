# Enterprise Knowledge Assistant

A production-grade, multi-tenant Retrieval-Augmented Generation (RAG) platform. It allows organizations to securely upload various document formats, index them, and chat with them using intelligent LangGraph-based agents.

## Features

* **Multi-Tenant Architecture**: Strict data isolation at the database and vector store levels.
* **Multi-Format Document Support**: Seamlessly ingest PDF, DOCX, PPTX, XLSX, CSV, TXT, HTML, and EML.
* **Intelligent RAG Workflow**: Implements a LangGraph agent workflow with Retrieval and Guardrails.
* **Hybrid Search**: Advanced context retrieval combining Dense embeddings (SentenceTransformers) and keyword search.
* **Custom Authentication**: Built from scratch using FastAPI, JWT, and Passlib.
* **Angular Frontend**: A modern, responsive UI built with Tailwind CSS.
* **Observability**: Tracing and LLM monitoring integrated via Langfuse.

## Tech Stack

* **Backend**: FastAPI, Python 3.9+, SQLAlchemy (Async), Alembic
* **Frontend**: Angular 17, Tailwind CSS
* **Vector Store**: Qdrant (In-Memory for local dev, Docker for production)
* **LLM & Orchestration**: LangChain, LangGraph, LiteLLM / OpenAI
* **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
* **Observability**: Langfuse

## Quickstart

### 1. Start the Backend
```bash
cd backend
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

### 2. Start the Frontend
```bash
cd frontend
# Install dependencies
npm install

# Run the Angular app
npm run start
```
Go to `http://localhost:4200` to start exploring!

## Knowledge Base & Interview Prep
We have documented the core concepts and technologies used in this project in the `knowledge/` directory. This is perfect for beginners or anyone preparing for a Generative AI Engineer interview! Check out:
- `01-architecture-overview.md`
- `02-fastapi-backend.md`
- `03-database-and-auth.md`
- `04-vector-database-qdrant.md`
- `05-rag-and-hybrid-search.md`
- `06-langchain-and-langgraph.md`
