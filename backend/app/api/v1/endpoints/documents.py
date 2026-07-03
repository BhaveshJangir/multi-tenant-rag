import shutil
import uuid
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import Document as DocumentSchema
from app.worker import process_document

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_manager_or_admin),
):
    """
    Upload a document for processing (Admin/Manager only).
    """
    allowed_extensions = {".pdf", ".txt", ".csv", ".docx", ".pptx", ".xlsx", ".html", ".eml"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    doc_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save to DB
    document = Document(
        id=doc_id,
        tenant_id=current_user.tenant_id,
        uploaded_by=current_user.id,
        file_name=file.filename,
        file_url=str(file_path),
        status="pending",
        metadata_={"original_name": file.filename, "size": os.path.getsize(file_path)}
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Queue background processing (Using FastAPI background tasks for simplicity in local dev instead of full celery for this demo)
    background_tasks.add_task(process_document, doc_id, str(file_path), current_user.tenant_id)
    
    # Alternatively via Celery:
    # celery_app.send_task("app.worker.process_document", args=[doc_id, str(file_path), current_user.tenant_id])

    return document
