from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenant.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="Employee") # Admin, Manager, Employee
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant")
