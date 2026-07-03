# 05 - RAG and Hybrid Search: Detailed Notes

## 1. What is RAG?
**Retrieval-Augmented Generation (RAG)** is the industry-standard architecture for building enterprise AI applications. Large Language Models (LLMs) like GPT-4 are trained on vast amounts of public data, but they lack two crucial things:
1. **Private Data**: They don't know your company's internal documents or user data.
2. **Current Events**: Their knowledge cuts off at the end of their training run.

Instead of retraining (fine-tuning) the model on your private data (which is extremely expensive, hard to update, and causes massive security risks since models can't verify RBAC), we use RAG.
RAG works by intercepting the user's question, searching a database for relevant documents, and pasting those documents into the prompt. The LLM is instructed: "Answer the user's question, but *only* use the information provided in the context below."

## 2. The Chunking Strategy
You cannot feed a 100-page PDF directly into an embedding model or an LLM context window. It must be broken down.
**Chunking** is the process of splitting text into smaller pieces (e.g., 500-1000 characters). 
A critical aspect of chunking is **Overlap**. If a sentence is split perfectly in half across two chunks, the semantic meaning is destroyed. By adding an overlap (e.g., 200 characters), we ensure context flows smoothly from one chunk to the next.

## 3. Hybrid Search
Vector Search (Dense Retrieval) is magical for semantic matching, but it has a fatal flaw: it is terrible at exact keyword matching. If you are searching for a specific serial number like "XY-9942", semantic search might return documents about "XY-9943" because they are semantically identical, ignoring the specific characters.

**Hybrid Search** solves this by running two searches simultaneously:
1. **Dense Search**: For meaning and concepts (Vectors).
2. **Sparse Search (BM25)**: For exact keyword counting (TF-IDF).

The two lists of results are merged using an algorithm like **Reciprocal Rank Fusion (RRF)**, which assigns a score based on rank position rather than raw score. The resulting top documents offer the best of both worlds.

## 4. Other Advanced RAG Approaches
- **Re-ranking (Cross-Encoders)**: Fetching 50 documents using fast Hybrid Search, then using a much slower, more accurate neural network (a Cross-Encoder) to re-score and sort those 50 documents into a perfect top 5.
- **HyDE (Hypothetical Document Embeddings)**: Asking the LLM to generate a "fake" answer to the query first, and then embedding that fake answer to search the database. This bridges the vocabulary gap between a short question and a long, descriptive document.
- **GraphRAG**: Extracting entities (People, Places) and relationships into a Neo4j Knowledge Graph. Excellent for answering multi-hop questions like "How is John related to the Alpha Project?".

---

## Interview Questions (Beginner to Intermediate)

**Q1: What problem does RAG solve?**
> **A:** Hallucinations and knowledge cutoffs. It grounds LLM answers in private, factual data without needing to retrain the model.

**Q2: What is "Chunking" and why do we do it?**
> **A:** Splitting large text into smaller overlapping pieces so they fit inside an LLM's context window and preserve targeted meaning.
> ```python
> splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
> chunks = splitter.split_text(full_document_text)
> ```

**Q3: What is BM25?**
> **A:** An advanced algorithm for keyword counting (TF-IDF evolved) that penalizes overly common words (like "the") and rewards rare, specific words.

**Q4: What is Reciprocal Rank Fusion (RRF)?**
> **A:** An algorithm to combine Dense and Sparse (BM25) search rankings. `Score = 1 / (k + rank)`.

**Q5: Disadvantages of Fine-Tuning vs RAG?**
> **A:** Fine-tuning is extremely expensive, requires thousands of structured Q&A pairs, and makes it impossible to apply document-level access control. RAG allows instant updates and strict RBAC.

**Q6: What is the "Lost in the Middle" phenomenon?**
> **A:** LLMs pay strong attention to the start and end of a context window, but ignore the middle. Fetching top 5 chunks is often better than cramming the context window full with 20 chunks.

**Q7: What is Query Expansion?**
> **A:** Using an LLM to rewrite the user's query into synonyms or alternate phrasings to increase retrieval hit rates.

**Q8: What is HyDE (Hypothetical Document Embeddings)?**
> **A:** Asking the LLM to generate a "fake" answer to the user's query, embedding that fake answer, and using it to search the Vector DB.

**Q9: How do you evaluate a RAG system?**
> **A:** Using frameworks like Ragas or TruLens to measure Context Relevance (did we fetch the right document?) and Answer Faithfulness (did the LLM hallucinate based on the context provided?).

**Q10: What is GraphRAG?**
> **A:** Using a Knowledge Graph (Neo4j) to extract entities and relationships, allowing the LLM to traverse connections (e.g., "Who owns the company that makes X?") which traditional vector search struggles to answer.
