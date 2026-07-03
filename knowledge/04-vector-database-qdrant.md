# 04 - Vector Databases (Qdrant): Detailed Notes

## 1. The Need for Vector Databases
Traditional SQL databases search using lexical matching. If you query `WHERE text LIKE '%dog%'`, it will look for the exact letters D-O-G. It has no concept of what a dog is. If a document only contains the word "puppy" or "canine", the SQL database will not find it.

To solve this, we convert text into **Embeddings**. An embedding model (like OpenAI's `text-embedding-ada-002` or open-source `SentenceTransformers`) reads the text and outputs an array of floating-point numbers (e.g., `[0.12, -0.45, 0.89...]`). These numbers represent the semantic meaning of the text in a highly-dimensional mathematical space. In this space, the array for "dog" and the array for "puppy" point in almost the exact same direction.

A **Vector Database** is purpose-built to store these arrays and perform rapid mathematical calculations to find the closest vectors to a given query vector.

## 2. How Qdrant Achieves Speed (HNSW)
If you have 10 million vectors and a user asks a question, comparing the query vector against all 10 million vectors using cosine similarity (a process called k-NN or Exact Search) would take several seconds. This is unacceptable for a chat interface.

Qdrant (and most modern vector DBs) uses **Approximate Nearest Neighbor (ANN)** search, specifically an algorithm called **HNSW** (Hierarchical Navigable Small World). 
HNSW builds a multi-layered graph. The top layers have very few nodes (vectors) with long connections, acting like an "expressway". The bottom layers contain all the nodes. When searching, the algorithm starts at the top, quickly jumps to the general vicinity of the target, and then drops down through the layers to find the exact nearest neighbors. This reduces search time from seconds to milliseconds, even on billions of vectors.

## 3. Metadata Filtering (Pre vs Post)
In a multi-tenant application, you absolutely cannot allow Tenant A to search Tenant B's documents. Therefore, every vector stored must have metadata (a JSON payload) attached to it, like `{"tenant_id": "123"}`.

- **Post-filtering**: The database runs the vector search first to find the top 100 closest documents, and *then* throws away the ones that don't belong to Tenant A. If 90 of those documents belonged to Tenant B, Tenant A only gets 10 results. This degrades search quality.
- **Pre-filtering**: The database applies the filter *during* the graph traversal. Qdrant dynamically adjusts the HNSW graph to only search through nodes that belong to Tenant A, guaranteeing a full list of top results without data leakage.

---

## Interview Questions (Beginner to Intermediate)

**Q1: What is an Embedding?**
> **A:** A numerical representation of semantic meaning as an array of floating-point numbers.
> ```python
> model = SentenceTransformer('all-MiniLM-L6-v2')
> vector = model.encode("Hello world") # Returns [0.12, -0.05, ...]
> ```

**Q2: How do Vector Databases find similar documents?**
> **A:** Using distance metrics like Cosine Similarity (measuring the angle between vectors) or Euclidean Distance (straight-line distance).

**Q3: Why not use a regular SQL database for semantic search?**
> **A:** SQL relies on exact keyword matching. Vector DBs understand the "meaning" of a query. Searching "canines" in a vector DB will successfully find documents about "dogs".

**Q4: How does Qdrant search millions of vectors so fast?**
> **A:** Using HNSW (Hierarchical Navigable Small World) graphs to zoom in on approximate nearest neighbors instantly, rather than comparing the query against every single vector (which would be O(N)).

**Q5: Pre-filtering vs Post-filtering?**
> **A:** Pre-filtering filters metadata *during* the graph search, guaranteeing exact matches without losing top-K results. Post-filtering filters *after*, which can result in empty responses.
> ```python
> # Qdrant Pre-filtering example
> models.Filter(must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value="123"))])
> ```

**Q6: Dense vs Sparse vectors?**
> **A:** Dense vectors (like the ones from SentenceTransformers) represent semantic meaning (floats). Sparse vectors represent exact keyword frequencies and mostly contain zeros (like BM25 or SPLADE).

**Q7: How do you update a document in a Vector DB?**
> **A:** You re-embed the new text and perform an `Upsert` operation using the exact same Point ID to overwrite the old vector.

**Q8: What is dimension size?**
> **A:** The number of floats in the array. `all-MiniLM-L6-v2` is 384. OpenAI `text-embedding-3-small` is 1536. Higher dimensions capture more nuance but require more RAM to store.

**Q9: Why does Qdrant usually run entirely in RAM (memory)?**
> **A:** Vector math (calculating distance between thousands of float arrays) requires extremely fast read speeds. Reading from disk (SSD) would be too slow for real-time chat retrieval.

**Q10: What is a Collection in Qdrant?**
> **A:** Similar to a Table in SQL. All vectors in a collection must share the exact same dimension size and distance metric.
