from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class AuditLog(Base):
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenant.id"), nullable=False)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    action = Column(String, nullable=False) # e.g. login, upload, search, delete
    target_id = Column(String, nullable=True) # e.g. document_id
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant")
    user = relationship("User")
