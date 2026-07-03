from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    file_name: str
    status: str
    metadata_: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    tenant_id: str
    uploaded_by: str

class DocumentInDB(DocumentBase):
    id: str
    tenant_id: str
    uploaded_by: str
    file_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentInDB):
    pass
