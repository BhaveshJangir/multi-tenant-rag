# 02 - FastAPI Backend: Detailed Notes

## 1. What is FastAPI?
FastAPI is one of the fastest Python web frameworks available today. Built on top of Starlette (for web routing) and Pydantic (for data validation), it was designed from the ground up to support asynchronous programming. 

In traditional frameworks like Django or Flask, a slow database query blocks the entire server worker, meaning other users have to wait. FastAPI uses `asyncio`, allowing the server to handle thousands of concurrent requests by pausing execution while waiting for network I/O.

## 2. Pydantic and Data Validation
A massive portion of backend bugs come from bad data (e.g., expecting a number but receiving a string). Pydantic forces type safety.
You define a schema as a Python class. When JSON data hits your API, FastAPI intercepts it and passes it through Pydantic. If the data is missing fields or has the wrong types, FastAPI automatically returns a perfectly formatted `422 Unprocessable Entity` error before your actual endpoint code even runs. This drastically reduces boilerplate code.

## 3. Dependency Injection
FastAPI has a built-in Dependency Injection system via the `Depends()` function. 
A "Dependency" is just a function that runs *before* your endpoint. It's used to:
1. Extract the database session and pass it to the route.
2. Read the `Authorization` header, decode the JWT, verify the user, and pass the user object to the route.
By centralizing this logic in dependencies, your actual API endpoints become incredibly short and focused solely on business logic.

## 4. OpenAPI and Swagger UI
FastAPI automatically reads your endpoint definitions, Pydantic models, and docstrings to generate an OpenAPI specification (formerly Swagger). 
Without writing any extra code, you get an interactive documentation page at `http://localhost:8000/docs`. This allows frontend developers to instantly see what endpoints exist, what JSON body they require, and even test them directly in the browser.

---

## Interview Questions (Beginner to Intermediate)

**Q1: Why choose FastAPI over Django or Flask for AI?**
> **A:** AI apps require heavy I/O operations (calling external LLMs, querying vector databases). FastAPI's asynchronous nature (`asyncio`) handles these concurrently without blocking the server.

**Q2: What is the purpose of Pydantic?**
> **A:** Data validation and type coercion.
> ```python
> class UserLogin(BaseModel):
>     username: str
>     password: str
> # FastAPI automatically rejects requests missing these fields.
> ```

**Q3: How does FastAPI handle CORS (Cross-Origin Resource Sharing)?**
> **A:** Using `CORSMiddleware` to define which frontend domains (origins) can access the API.
> ```python
> app.add_middleware(
>     CORSMiddleware,
>     allow_origins=["http://localhost:4200"],
>     allow_methods=["*"]
> )
> ```

**Q4: Can you explain Dependency Injection in FastAPI?**
> **A:** Dependency Injection is a design pattern. In FastAPI, `Depends()` automatically runs a function and injects the result into the endpoint.
> ```python
> @app.get("/me")
> def get_me(user: User = Depends(get_current_user)):
>     return user
> ```

**Q5: What is synchronous vs asynchronous code?**
> **A:** Sync blocks the thread while waiting for a response. Async (`await`) frees the thread to handle other users.
> ```python
> # Async prevents blocking the whole server while waiting for the LLM!
> response = await llm_client.generate("Hello")
> ```

**Q6: What is OpenAPI?**
> **A:** A standard specification for defining REST APIs. FastAPI auto-generates Swagger UI at `/docs` by reading your Pydantic models.

**Q7: How do you handle errors in FastAPI?**
> **A:** By raising an `HTTPException`.
> ```python
> if not user:
>     raise HTTPException(status_code=404, detail="User not found")
> ```

**Q8: What is an API Router?**
> **A:** `APIRouter` allows splitting a massive app into smaller, manageable files (e.g., `users.py`, `docs.py`) and including them in `main.py` using `app.include_router()`.

**Q9: How does FastAPI use Python Type Hints?**
> **A:** It uses them for validation, editor autocomplete, and documentation generation. If you specify `id: int`, sending `"abc"` throws a clean 422 Unprocessable Entity error.

**Q10: What server runs FastAPI?**
> **A:** FastAPI is a framework, not a server. We use **Uvicorn**, an ASGI (Asynchronous Server Gateway Interface) server, to run it.
