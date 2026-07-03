from qdrant_client import QdrantClient
from qdrant_client.http import models

# Use in-memory Qdrant client for local development without Docker
qdrant_client = QdrantClient(location=":memory:")

COLLECTION_NAME = "enterprise_documents"

def init_qdrant():
    try:
        collections = qdrant_client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        if not exists:
            # We will use SentenceTransformers (all-MiniLM-L6-v2) which outputs 384 dimensions
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=384, 
                    distance=models.Distance.COSINE
                ),
            )
            print(f"Collection '{COLLECTION_NAME}' created.")
    except Exception as e:
        print(f"Failed to initialize Qdrant: {e}")
