from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.post("/tenants", response_model=dict)
async def create_tenant(
    name: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new tenant (Should be a superadmin endpoint, simplified for demo)
    """
    result = await db.execute(select(Tenant).filter(Tenant.name == name))
    tenant = result.scalars().first()
    if tenant:
        raise HTTPException(status_code=400, detail="Tenant already exists")
    
    tenant = Tenant(id=str(uuid.uuid4()), name=name)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return {"id": tenant.id, "name": tenant.name}

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/", response_model=List[UserSchema])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve users. Only admin can do this, and only for their tenant.
    """
    result = await db.execute(
        select(User).filter(User.tenant_id == current_user.tenant_id).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users
