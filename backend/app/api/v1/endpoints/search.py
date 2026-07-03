from fastapi import APIRouter, Depends
from sentence_transformers import SentenceTransformer
from app.db.vector_store import qdrant_client, COLLECTION_NAME
from app.api import deps
from app.models.user import User

router = APIRouter()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

@router.post("/search")
async def search_documents(
    query: str,
    limit: int = 5,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Search for documents using Dense Retrieval (Qdrant).
    """
    query_vector = embedding_model.encode(query).tolist()
    
    # Perform vector search filtering by tenant_id to ensure tenant isolation
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        query_filter={
            "must": [
                {
                    "key": "tenant_id",
                    "match": {"value": current_user.tenant_id}
                }
            ]
        }
    )
    
    results = []
    for hit in search_result:
        results.append({
            "document_id": hit.payload.get("document_id"),
            "text": hit.payload.get("text"),
            "score": hit.score
        })
        
    return {"query": query, "results": results}
