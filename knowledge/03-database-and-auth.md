# 03 - Database and Authentication: Detailed Notes

## 1. Object-Relational Mappers (ORMs)
Writing raw SQL queries (like `SELECT * FROM users WHERE id = 5`) inside your Python code is generally a bad idea for three reasons:
1. It is highly susceptible to **SQL Injection** attacks if string formatting is used improperly.
2. It makes the code hard to read and maintain.
3. It tightly couples your application to a specific database dialect (e.g., changing from SQLite to PostgreSQL would require rewriting hundreds of queries).

**SQLAlchemy** solves this. It acts as a bridge, mapping Python classes to Database Tables. You interact with Python objects, and SQLAlchemy handles the translation to highly-optimized, secure SQL under the hood.

## 2. Database Migrations with Alembic
When building an application, your database schema changes constantly. You add a `profile_picture` column to the Users table, or create a whole new `ChatHistory` table.
If you were using raw SQL, you'd have to manually log into the production database and run `ALTER TABLE` commands. This is dangerous and prone to human error.
**Alembic** acts as version control for your database. It compares your Python models to the current state of the database and generates a "migration script". You can easily roll the database forward (`alembic upgrade head`) or backward (`alembic downgrade -1`), ensuring your database schema is always in sync with your code without dropping existing data.

## 3. JWT Authentication Security
JSON Web Tokens (JWT) are the modern standard for stateless authentication.
Unlike session cookies (which require the server to store a session ID in its memory or database), a JWT contains the user's identity right inside the token payload (e.g., `{"sub": "user_123", "role": "admin"}`).

### The Flow:
1. The user logs in with an email and password.
2. The server hashes the password (using `bcrypt`), compares it to the database, and if successful, generates a JWT.
3. The server signs the JWT using a highly secure, secret string (`SECRET_KEY`).
4. The client receives the JWT and stores it (usually in local storage or an HttpOnly cookie).
5. On every subsequent request, the client sends the JWT in the `Authorization: Bearer <token>` header.
6. The server receives the token, recalculates the signature using its `SECRET_KEY`, and if the signatures match, the server *knows* the token is authentic and hasn't been tampered with. It grants access without needing to query the database.

---

## Interview Questions (Beginner to Intermediate)

**Q1: What is Authentication vs Authorization?**
> **A:** Authentication is logging in (verifying identity). Authorization is checking if that identity has permissions (RBAC).

**Q2: Why hash passwords instead of encrypting?**
> **A:** Encryption is reversible if you have the key. Hashing is a one-way mathematical street. Even if the database is stolen, passwords cannot be read.
> ```python
> from passlib.context import CryptContext
> pwd_context = CryptContext(schemes=["bcrypt"])
> # We only ever store this hash, never the raw string
> hashed = pwd_context.hash("my_password")
> ```

**Q3: What happens if a JWT is stolen?**
> **A:** The attacker has full access until the token expires. That's why we use short lifetimes (e.g., 15 mins) and enforce HTTPS to prevent interception.

**Q4: How does Alembic handle database migrations?**
> **A:** It generates scripts with `upgrade()` and `downgrade()` functions using safe `ALTER TABLE` commands, preserving existing data.

**Q5: What are the benefits of an ORM?**
> **A:** Prevents SQL injection, allows OOP programming, and makes the code database-agnostic.
> ```python
> # Safe (ORM):
> db.query(User).filter(User.name == input_name).all()
> # Unsafe (SQL Injection risk):
> # cursor.execute(f"SELECT * FROM users WHERE name = '{input_name}'")
> ```

**Q6: What is a Refresh Token?**
> **A:** A long-lived token (stored securely, often in HttpOnly cookies) used to silently request new, short-lived Access Tokens in the background without asking the user to log in again.

**Q7: How is a JWT structured?**
> **A:** Three parts separated by dots: Header, Payload (contains claims like `user_id`), and Signature (to verify authenticity).

**Q8: Can anyone read a JWT payload?**
> **A:** YES! Base64 decoding reveals the payload. You should **never** put passwords or sensitive PII in a JWT. The signature only prevents *tampering*, not reading.

**Q9: What is the "N+1 query problem" in ORMs?**
> **A:** When you query a list of 100 users, and then loop through them to fetch their company, resulting in 101 separate SQL queries. It severely degrades performance and is usually solved via eager loading (`joinedload()`).

**Q10: Why use UUIDs instead of auto-incrementing integers for IDs?**
> **A:** Integers are predictable (if my ID is 5, I might try to fetch ID 4). UUIDs are random and unguessable, making the API significantly more secure against scraping and unauthorized access.
