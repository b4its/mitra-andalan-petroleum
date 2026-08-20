from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from app.models.price import Price
from app.schemas.price import PriceCreate, PriceResponse, PriceUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get(
    "/prices",
    response_model=list[PriceResponse],
    summary="List prices",
    description="Daftar harga (fuel/shipping) terbaru di atas. Filter opsional berdasarkan kategori.",
)
async def list_prices(
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Price).order_by(Price.created_at.desc())
    if category:
        stmt = stmt.where(Price.category == category)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/prices/{id}",
    response_model=PriceResponse,
    summary="Detail harga",
    description="Detail harga berdasarkan ID.",
)
async def get_price(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Price).where(Price.id == id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return price


@router.post(
    "/prices",
    response_model=PriceResponse,
    status_code=201,
    summary="Buat harga",
    description="Mencatat harga baru (harga solar atau biaya pengiriman).",
)
async def create_price(request: Request, body: PriceCreate, db: AsyncSession = Depends(get_db)):
    price = Price(**body.model_dump())
    db.add(price)
    await db.flush()
    await db.refresh(price)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="price",
        resource_id=price.id,
        resource_name=price.category,
        old_data=None,
        new_data=model_to_dict(price),
        details=f"Harga {price.category} berhasil dicatat"
    )
    return price


@router.put(
    "/prices/{id}",
    response_model=PriceResponse,
    summary="Update harga",
    description="Update data harga berdasarkan ID.",
)
async def update_price(request: Request, id: str, body: PriceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Price).where(Price.id == id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(price)
    data = body.model_dump(exclude_unset=True)
    for key, val in data.items():
        setattr(price, key, val)
    await db.flush()
    await db.refresh(price)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="price",
        resource_id=price.id,
        resource_name=price.category,
        old_data=old_data,
        new_data=model_to_dict(price),
        details=f"Harga {price.category} berhasil diperbarui"
    )
    return price


@router.delete(
    "/prices/{id}",
    response_model=MessageResponse,
    summary="Hapus harga",
    description="Hapus harga berdasarkan ID.",
)
async def delete_price(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Price).where(Price.id == id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    price_category = price.category
    old_data = model_to_dict(price)
    await db.delete(price)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="price",
        resource_id=id,
        resource_name=price_category,
        old_data=old_data,
        new_data=None,
        details=f"Harga {price_category} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
