from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.supplier import Supplier
from app.schemas.common import MessageResponse
from app.schemas.supplier import (
    SupplierResponse,
    SupplierCreate,
    SupplierUpdate,
)

router = APIRouter()


@router.get(
    "/suppliers",
    response_model=list[SupplierResponse],
    summary="List suppliers",
    description="Daftar semua supplier (terbaru di atas).",
)
async def list_suppliers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).order_by(Supplier.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/suppliers/{id}",
    response_model=SupplierResponse,
    summary="Detail supplier",
    description="Detail supplier berdasarkan ID.",
)
async def get_supplier(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return s


@router.post(
    "/suppliers",
    response_model=SupplierResponse,
    status_code=201,
    summary="Buat supplier",
    description="Mendaftarkan supplier baru.",
)
async def create_supplier(request: Request, body: SupplierCreate, db: AsyncSession = Depends(get_db)):
    s = Supplier(**body.model_dump())
    db.add(s)
    await db.flush()
    await db.refresh(s)
    
    # Log activity
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="supplier",
        resource_id=s.id,
        resource_name=s.name,
        old_data=None,
        new_data=model_to_dict(s),
        details=f"Supplier {s.name} berhasil dibuat"
    )
    
    return s


@router.put(
    "/suppliers/{id}",
    response_model=SupplierResponse,
    summary="Update supplier",
    description="Update data supplier.",
)
async def update_supplier(request: Request, id: str, body: SupplierUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    
    old_data = model_to_dict(s)

    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(s, key, val)

    await db.flush()
    await db.refresh(s)

    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="supplier",
        resource_id=s.id,
        resource_name=s.name,
        old_data=old_data,
        new_data=model_to_dict(s),
        details=f"Data supplier {s.name} berhasil diperbarui"
    )
    
    return s


@router.delete(
    "/suppliers/{id}",
    response_model=MessageResponse,
    summary="Hapus supplier",
    description="Hapus supplier berdasarkan ID.",
)
async def delete_supplier(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    
    supplier_name = s.name
    old_data = model_to_dict(s)

    await db.delete(s)
    await db.flush()

    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="supplier",
        resource_id=id,
        resource_name=supplier_name,
        old_data=old_data,
        new_data=None,
        details=f"Supplier {supplier_name} berhasil dihapus"
    )
    
    return MessageResponse(message="Dihapus", code=200)
