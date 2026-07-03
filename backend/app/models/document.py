from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Document(Base):
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenant.id"), nullable=False)
    uploaded_by = Column(String, ForeignKey("user.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=True) # S3/MinIO URL
    status = Column(String, default="pending") # pending, processing, processed, error
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant")
    uploader = relationship("User")
