from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    session_id: str

class ChatMessage(ChatMessageBase):
    id: str
    session_id: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionCreate(ChatSessionBase):
    tenant_id: str
    user_id: str

class ChatSession(ChatSessionBase):
    id: str
    tenant_id: str
    user_id: str
    created_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    query: str
