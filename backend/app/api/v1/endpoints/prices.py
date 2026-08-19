from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
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
async def create_price(body: PriceCreate, db: AsyncSession = Depends(get_db)):
    price = Price(**body.model_dump())
    db.add(price)
    await db.flush()
    await db.refresh(price)
    return price


@router.put(
    "/prices/{id}",
    response_model=PriceResponse,
    summary="Update harga",
    description="Update data harga berdasarkan ID.",
)
async def update_price(id: str, body: PriceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Price).where(Price.id == id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    for key, val in data.items():
        setattr(price, key, val)
    await db.flush()
    await db.refresh(price)
    return price


@router.delete(
    "/prices/{id}",
    response_model=MessageResponse,
    summary="Hapus harga",
    description="Hapus harga berdasarkan ID.",
)
async def delete_price(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Price).where(Price.id == id))
    price = result.scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    await db.delete(price)
    await db.flush()
    return MessageResponse(message="Dihapus", code=200)
