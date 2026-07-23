from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerResponse,
    CustomerCreate,
    CustomerUpdate,
    MessageResponse,
)

router = APIRouter()


@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.name))
    return result.scalars().all()


@router.get("/customers/{id}", response_model=CustomerResponse)
async def get_customer(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c


@router.post("/customers", response_model=CustomerResponse, status_code=201)
async def create_customer(body: CustomerCreate, db: AsyncSession = Depends(get_db)):
    c = Customer(**body.model_dump())
    db.add(c)
    await db.flush()
    await db.refresh(c)
    return c


@router.put("/customers/{id}", response_model=CustomerResponse)
async def update_customer(id: str, body: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(c, key, val)
    await db.flush()
    await db.refresh(c)
    return c


@router.delete("/customers/{id}", response_model=MessageResponse)
async def delete_customer(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(c)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
