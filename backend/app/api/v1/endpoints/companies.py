from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity
from app.models.company import Company
from app.schemas.common import MessageResponse
from app.schemas.company import (
    CompanyResponse,
    CompanyCreate,
    CompanyUpdate,
)

router = APIRouter()


@router.get(
    "/companies",
    response_model=list[CompanyResponse],
    summary="List companies",
    description="Daftar semua perusahaan.",
)
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).order_by(Company.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/companies/{id}",
    response_model=CompanyResponse,
    summary="Detail company",
    description="Detail perusahaan berdasarkan ID.",
)
async def get_company(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return c


@router.post(
    "/companies",
    response_model=CompanyResponse,
    status_code=201,
    summary="Buat perusahaan",
    description="Mendaftarkan perusahaan baru.",
)
async def create_company(request: Request, body: CompanyCreate, db: AsyncSession = Depends(get_db)):
    c = Company(**body.model_dump())
    db.add(c)
    await db.flush()
    await db.refresh(c)
    
    # Log activity
    await log_activity(
        db=db,
        request=request,
        user_id=None,  # Can extract from JWT if available
        actor_name="System",
        actor_role="system",
        action="create",
        resource_type="company",
        resource_id=c.id,
        resource_name=c.name,
        new_data=body.model_dump(),
        details=f"Perusahaan {c.name} berhasil dibuat"
    )
    
    return c


@router.put(
    "/companies/{id}",
    response_model=CompanyResponse,
    summary="Update perusahaan",
    description="Update data perusahaan.",
)
async def update_company(id: str, body: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(c, key, val)
    await db.flush()
    await db.refresh(c)
    return c


@router.delete(
    "/companies/{id}",
    response_model=MessageResponse,
    summary="Hapus perusahaan",
    description="Hapus perusahaan berdasarkan ID.",
)
async def delete_company(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    await db.delete(c)
    await db.flush()
    return MessageResponse(message="Dihapus", code=200)
