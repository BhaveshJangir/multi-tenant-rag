# Backend Structure and Flow

This backend is built using **FastAPI** (Python). It is designed as a **Modular Monolith**, meaning all the code runs in a single server instance but is cleanly separated into logical folders so it can easily scale or be split into microservices later.

## 📂 Directory Structure

```text
backend/
├── app/
│   ├── api/          # API Routers (Endpoints) grouped by version
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py      # Login and user registration
│   │           ├── documents.py # File upload and document listing
│   │           └── chat.py      # LangGraph chat endpoints
│   ├── core/         # Core application configurations
│   │   ├── config.py # Environment variables (Pydantic BaseSettings)
│   │   ├── security.py # Password hashing (bcrypt) and JWT generation
│   │   └── agent.py  # LangChain/LangGraph workflow definitions
│   ├── db/           # Database connections
│   │   ├── session.py # SQLAlchemy setup (Postgres/SQLite)
│   │   └── vector_store.py # Qdrant vector database setup
│   ├── models/       # Database Models (SQLAlchemy)
│   │   ├── user.py
│   │   ├── tenant.py
│   │   └── document.py
│   ├── schemas/      # Pydantic Models (Data Validation)
│   │   ├── user.py
│   │   ├── token.py
│   │   └── document.py
│   ├── main.py       # FastAPI application initialization & middleware
│   └── worker.py     # Background tasks (Parsing, Chunking, Embedding)
├── requirements.txt  # Python dependencies
└── alembic/          # Database migration scripts
```

## ⚙️ Environment Configuration

For security, this application does not hardcode sensitive information (like API keys or Database Passwords). Instead, we use `python-dotenv` combined with Pydantic `BaseSettings`.

When you deploy or run this application, you must configure your environment variables:
1. Copy the provided `.env.example` file and rename it to `.env`.
2. Open `.env` and fill in your actual `OPENAI_API_KEY` and any other required secrets.

FastAPI automatically loads these variables at startup via `app/core/config.py`.

## 🔄 The Flow of the Backend

When a user interacts with the application, data flows through the backend in a specific sequence:

### 1. HTTP Request Arrival (`main.py`)
Every request first hits `main.py`. Here, FastAPI checks the CORS middleware to ensure the request is coming from an allowed domain (like our Angular frontend). 

### 2. Routing (`app/api/v1/endpoints/`)
The request is routed to the appropriate file based on the URL. For example, a `POST /upload` request goes to `documents.py`.

### 3. Data Validation (`app/schemas/`)
Before the endpoint code even runs, FastAPI uses our Pydantic schemas to validate the incoming JSON body. If the user forgets to include a required field, FastAPI automatically returns a `422 Unprocessable Entity` error.

### 4. Dependency Injection (Authentication & DB)
FastAPI injects required tools into the endpoint function using `Depends()`. 
- `Depends(get_db)` gives the endpoint a safe connection to the database.
- `Depends(get_current_active_user)` intercepts the `Authorization` header, decodes the JWT, verifies the user exists, and passes the `User` object into the endpoint. If the token is invalid, the request is rejected immediately with a `401 Unauthorized`.

### 5. Business Logic & Background Tasks
Inside the endpoint, the business logic runs.
- **For a Chat Request**: The request is sent to `app/core/agent.py`. The LangGraph agent retrieves documents from Qdrant (`app/db/vector_store.py`), combines them with the prompt, queries the LLM, and returns the generated answer.
- **For an Upload Request**: The file is saved to the disk, a record is added to the SQL database using `app/models/`, and a background task is triggered inside `app/worker.py`. The background worker extracts the text, splits it into chunks, generates embeddings using `SentenceTransformers`, and uploads them to Qdrant.

### 6. HTTP Response
Finally, the endpoint returns a Python dictionary or Pydantic object. FastAPI automatically converts this into a JSON string and sends it back to the frontend with an HTTP `200 OK` status.
