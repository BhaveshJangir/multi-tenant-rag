from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    role: str = "Employee"

class UserCreate(UserBase):
    password: str
    tenant_id: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass
