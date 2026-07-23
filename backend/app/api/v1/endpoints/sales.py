from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.sale import Sale
from app.schemas.sale import SaleResponse, SaleCreate, SaleUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/sales", response_model=list[SaleResponse])
async def list_sales(limit: int = 5, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).order_by(Sale.created_at.desc()).limit(limit))
    return result.scalars().all()


@router.get("/sales/{id}", response_model=SaleResponse)
async def get_sale(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).where(Sale.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return s


@router.post("/sales", response_model=SaleResponse, status_code=201)
async def create_sale(body: SaleCreate, db: AsyncSession = Depends(get_db)):
    s = Sale(**body.model_dump())
    db.add(s)
    await db.flush()
    await db.refresh(s)
    return s


@router.put("/sales/{id}", response_model=SaleResponse)
async def update_sale(id: str, body: SaleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).where(Sale.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(s, key, val)
    await db.flush()
    await db.refresh(s)
    return s


@router.delete("/sales/{id}", response_model=MessageResponse)
async def delete_sale(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sale).where(Sale.id == id))
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(s)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
