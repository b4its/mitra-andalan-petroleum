from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
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
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="company",
        resource_id=c.id,
        resource_name=c.name,
        old_data=None,
        new_data=model_to_dict(c),
        details=f"Perusahaan {c.name} berhasil dibuat"
    )
    
    return c


@router.put(
    "/companies/{id}",
    response_model=CompanyResponse,
    summary="Update perusahaan",
    description="Update data perusahaan.",
)
async def update_company(request: Request, id: str, body: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(c)
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(c, key, val)
    await db.flush()
    await db.refresh(c)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="company",
        resource_id=c.id,
        resource_name=c.name,
        old_data=old_data,
        new_data=model_to_dict(c),
        details=f"Data perusahaan {c.name} berhasil diperbarui"
    )
    return c


@router.delete(
    "/companies/{id}",
    response_model=MessageResponse,
    summary="Hapus perusahaan",
    description="Hapus perusahaan berdasarkan ID.",
)
async def delete_company(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    company_name = c.name
    old_data = model_to_dict(c)
    await db.delete(c)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="company",
        resource_id=id,
        resource_name=company_name,
        old_data=old_data,
        new_data=None,
        details=f"Perusahaan {company_name} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
