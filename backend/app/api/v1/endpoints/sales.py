from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from app.models.sale import Sale
from app.schemas.sale import SaleResponse, SaleCreate, SaleUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get(
    "/sales",
    response_model=list[SaleResponse],
    summary="List sales",
    description="Daftar sales terbaru (limit default 5).",
)
async def list_sales(limit: int = 5, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).order_by(Sale.created_at.desc()).limit(limit))
    return result.scalars().all()


@router.get(
    "/sales/{id}",
    response_model=SaleResponse,
    summary="Detail sale",
    description="Detail data penjualan.",
)
async def get_sale(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).where(Sale.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return s


@router.post(
    "/sales",
    response_model=SaleResponse,
    status_code=201,
    summary="Buat sale",
    description="Mencatat data penjualan baru.",
)
async def create_sale(request: Request, body: SaleCreate, db: AsyncSession = Depends(get_db)):
    s = Sale(**body.model_dump())
    db.add(s)
    await db.flush()
    await db.refresh(s)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="sale",
        resource_id=s.id,
        resource_name=s.id,
        old_data=None,
        new_data=model_to_dict(s),
        details=f"Data penjualan {s.id} berhasil dicatat"
    )
    return s


@router.put(
    "/sales/{id}",
    response_model=SaleResponse,
    summary="Update sale",
    description="Update data penjualan.",
)
async def update_sale(request: Request, id: str, body: SaleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).where(Sale.id == id))
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
        resource_type="sale",
        resource_id=s.id,
        resource_name=s.id,
        old_data=old_data,
        new_data=model_to_dict(s),
        details=f"Data penjualan {s.id} berhasil diperbarui"
    )
    return s


@router.delete(
    "/sales/{id}",
    response_model=MessageResponse,
    summary="Hapus sale",
    description="Hapus data penjualan.",
)
async def delete_sale(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).where(Sale.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
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
        resource_type="sale",
        resource_id=id,
        resource_name=s.id,
        old_data=old_data,
        new_data=None,
        details=f"Data penjualan {s.id} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
