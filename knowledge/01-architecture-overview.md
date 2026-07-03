# 01 - Architecture Overview: Detailed Notes

## 1. Introduction to the Project
The **Enterprise Knowledge Assistant** is designed to solve a critical problem in modern corporations: employees spend too much time searching for internal information across scattered documents. This platform serves as a centralized hub where organizations can upload their proprietary data (PDFs, presentations, emails, and spreadsheets) and query it using natural language. 

Unlike public models like ChatGPT, which are trained on public data and do not know your company's secrets, this system uses a technique called Retrieval-Augmented Generation (RAG). It keeps data private and secure.

## 2. Multi-Tenant Architecture Deep Dive
In enterprise software (B2B SaaS), you often serve multiple companies from the same application. 
- **Single-Tenant**: Every company gets its own separate server and separate database. This is highly secure but incredibly expensive and hard to maintain.
- **Multi-Tenant (Our Approach)**: All companies share the same servers, the same database, and the same Vector Store. 

### How do we keep data isolated?
We achieve strict data isolation using **Logical Separation**:
1. **Database Level**: Every table (Users, Documents, Chat History) has a `tenant_id` column. Every SQL query strictly filters by `tenant_id == current_user.tenant_id`.
2. **Vector Store Level**: Qdrant supports payload (metadata) filtering. Every vector uploaded contains a payload with `{"tenant_id": "abc"}`. When searching, Qdrant physically ignores vectors that don't match the user's tenant ID, preventing data leakage.

## 3. The Three-Tier System Architecture
The application is structured into three highly decoupled layers:

### A. Presentation Layer (Frontend)
- **Technology**: Angular 17, Tailwind CSS.
- **Responsibility**: It is a Single Page Application (SPA) running entirely in the user's browser. It is strictly responsible for rendering the UI and handling user interactions. 
- **Security**: It never connects to the database directly and never stores secrets. It communicates exclusively via REST API calls.

### B. Application Layer (Backend)
- **Technology**: FastAPI (Python), Uvicorn.
- **Responsibility**: The "brain" of the operation. It receives HTTP requests, verifies the JWT token to ensure the user is authenticated, enforces Role-Based Access Control (RBAC), and orchestrates the RAG pipeline.
- **Background Workers**: Heavy tasks (like parsing a 100-page PDF) are offloaded to background threads. This ensures the main server thread remains free to handle incoming chat requests, preventing the site from crashing under load.

### C. Data Layer
- **Relational Database (PostgreSQL/SQLite)**: Stores structured, tabular data. This is where we keep user profiles, tenant configurations, and metadata about uploaded documents.
- **Vector Database (Qdrant)**: Stores unstructured data converted into mathematical arrays (Embeddings). This is highly optimized for semantic similarity search.

---

## Interview Questions (Beginner to Intermediate)

**Q1: What is a "Multi-Tenant" architecture?**
> **A:** Multi-tenancy is an architecture where a single instance of a software application serves multiple customers (tenants). Each tenant's data is isolated and remains invisible to other tenants.
> ```python
> # Example of multi-tenant query in SQLAlchemy
> db.query(Document).filter(
>     Document.tenant_id == current_user.tenant_id
> ).all()
> ```

**Q2: Why decouple the frontend from the backend via an API?**
> **A:** Decoupling allows independent scaling, parallel development, and technology flexibility. The frontend handles UI, the backend handles business logic. It also allows the backend API to be reused by other clients (e.g., a mobile app or a partner API).

**Q3: Why use background tasks for document ingestion?**
> **A:** Parsing a 100-page PDF blocks the main thread. Background tasks allow immediate API response while processing happens asynchronously.
> ```python
> @app.post("/upload")
> async def upload_doc(background_tasks: BackgroundTasks):
>     background_tasks.add_task(process_pdf, file_path)
>     return {"status": "Processing started"}
> ```

**Q4: What is a monolithic architecture vs microservices?**
> **A:** A monolith bundles all components into one codebase. Microservices split them. We use a **modular monolith**—single backend, cleanly separated folders. This makes it easy to split into microservices (like a separate ingestion service) later if scaling demands it.

**Q5: How do we ensure backend scalability?**
> **A:** We use a Stateless Backend (JWTs instead of session memory) and Asynchronous I/O (`async def`) so multiple requests run concurrently.

**Q6: What is the purpose of the Presentation Layer?**
> **A:** It acts strictly as a client to render data. It never performs sensitive operations (like hashing passwords) to prevent exposing logic or API keys to the browser.

**Q7: How does the backend communicate with the Data Layer securely?**
> **A:** Through environment variables containing connection strings, never hardcoded in the source. We use an ORM to prevent SQL injection.
> ```python
> DATABASE_URL = os.getenv("DB_URL")
> engine = create_engine(DATABASE_URL)
> ```

**Q8: What is a RESTful API?**
> **A:** An architectural style where endpoints represent resources (like `/documents`) and use standard HTTP methods (GET, POST, DELETE).

**Q9: Why use Docker in this architecture?**
> **A:** Docker containerizes the database, vector store, and backend, ensuring that "it works on my machine" translates perfectly to production servers.

**Q10: How do we handle heavy load on the background worker?**
> **A:** If traffic spikes, we can use a message broker like **Redis + Celery**, allowing us to run multiple worker servers dedicated entirely to consuming the parsing queue.
