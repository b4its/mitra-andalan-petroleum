from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.activity_logger import log_activity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.customer import Customer
from app.schemas.common import MessageResponse
from app.schemas.customer import (
    CustomerResponse,
    CustomerCreate,
    CustomerUpdate,
)

router = APIRouter()


@router.get(
    "/customers",
    response_model=list[CustomerResponse],
    summary="List customers",
    description="Daftar semua customer (terbaru di atas).",
)
async def list_customers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/customers/{id}",
    response_model=CustomerResponse,
    summary="Detail customer",
    description="Detail customer berdasarkan ID.",
)
async def get_customer(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return c


@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=201,
    summary="Buat customer",
    description="Mendaftarkan customer baru.",
)
async def create_customer(request: Request, body: CustomerCreate, db: AsyncSession = Depends(get_db)):
    c = Customer(**body.model_dump())
    db.add(c)
    await db.flush()
    await db.refresh(c)
    
    # Log activity
    await log_activity(
        db=db,
        request=request,
        user_id=None,
        actor_name="System",
        actor_role="system",
        action="create",
        resource_type="customer",
        resource_id=c.id,
        resource_name=c.name,
        new_data=body.model_dump(),
        details=f"Customer {c.name} berhasil dibuat"
    )
    
    return c


@router.put(
    "/customers/{id}",
    response_model=CustomerResponse,
    summary="Update customer",
    description="Update data customer.",
)
async def update_customer(request: Request, id: str, body: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    
    old_data = {col.name: getattr(c, col.name) for col in c.__table__.columns}
    
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(c, key, val)
    
    await db.flush()
    await db.refresh(c)
    
    await log_activity(
        db=db,
        request=request,
        user_id=None,
        actor_name="System",
        actor_role="system",
        action="update",
        resource_type="customer",
        resource_id=c.id,
        resource_name=c.name,
        old_data=old_data,
        new_data=body.model_dump(),
        details=f"Data customer {c.name} berhasil diperbarui"
    )
    
    return c


@router.delete(
    "/customers/{id}",
    response_model=MessageResponse,
    summary="Hapus customer",
    description="Hapus customer berdasarkan ID.",
)
async def delete_customer(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.id == id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    
    customer_name = c.name
    old_data = {col.name: getattr(c, col.name) for col in c.__table__.columns}
    
    await db.delete(c)
    await db.flush()
    
    await log_activity(
        db=db,
        request=request,
        user_id=None,
        actor_name="System",
        actor_role="system",
        action="delete",
        resource_type="customer",
        resource_id=id,
        resource_name=customer_name,
        old_data=old_data,
        new_data=None,
        details=f"Customer {customer_name} berhasil dihapus"
    )
    
    return MessageResponse(message="Dihapus", code=200)
