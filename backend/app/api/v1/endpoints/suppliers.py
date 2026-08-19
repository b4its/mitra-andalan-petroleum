from fastapi import APIRouter, Depends, HTTPException
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
async def create_supplier(body: SupplierCreate, db: AsyncSession = Depends(get_db)):
    s = Supplier(**body.model_dump())
    db.add(s)
    await db.flush()
    await db.refresh(s)
    return s


@router.put(
    "/suppliers/{id}",
    response_model=SupplierResponse,
    summary="Update supplier",
    description="Update data supplier.",
)
async def update_supplier(id: str, body: SupplierUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(s, key, val)
    await db.flush()
    await db.refresh(s)
    return s


@router.delete(
    "/suppliers/{id}",
    response_model=MessageResponse,
    summary="Hapus supplier",
    description="Hapus supplier berdasarkan ID.",
)
async def delete_supplier(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier).where(Supplier.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    await db.delete(s)
    await db.flush()
    return MessageResponse(message="Dihapus", code=200)
