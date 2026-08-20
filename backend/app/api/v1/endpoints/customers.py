from fastapi import APIRouter, Depends, HTTPException, Request
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
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
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="customer",
        resource_id=c.id,
        resource_name=c.name,
        old_data=None,
        new_data=model_to_dict(c),
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
        resource_type="customer",
        resource_id=c.id,
        resource_name=c.name,
        old_data=old_data,
        new_data=model_to_dict(c),
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
        resource_type="customer",
        resource_id=id,
        resource_name=customer_name,
        old_data=old_data,
        new_data=None,
        details=f"Customer {customer_name} berhasil dihapus"
    )
    
    return MessageResponse(message="Dihapus", code=200)
