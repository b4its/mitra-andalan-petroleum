from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.delivery_order import DeliveryOrder
from app.models.customer import Customer
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.delivery_order import (
    DeliveryOrderResponse,
    DeliveryOrderCreate,
    DeliveryOrderUpdate,
)

router = APIRouter()


async def _get_customer_name(db, customer_id):
    if not customer_id:
        return ""
    c = await db.execute(select(Customer).where(Customer.id == customer_id))
    c_obj = c.scalar_one_or_none()
    return c_obj.name if c_obj else ""


def _to_response(do, customer_name):
    return DeliveryOrderResponse(
        id=do.id, do_number=do.do_number,
        customer_id=do.customer_id, customer_name=customer_name,
        po_number=do.po_number, transport_name=do.transport_name,
        fuel_total=do.fuel_total, status=do.status,
        created_at=do.created_at, updated_at=do.updated_at,
    )


@router.get("/delivery-orders", response_model=PaginatedResponse[DeliveryOrderResponse])
async def list_delivery_orders(
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)
):
    total_result = await db.execute(select(func.count()).select_from(select(DeliveryOrder).subquery()))
    total = total_result.scalar() or 0

    stmt = select(DeliveryOrder).order_by(DeliveryOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    dos = result.scalars().all()

    items = []
    for do in dos:
        cn = await _get_customer_name(db, do.customer_id)
        items.append(_to_response(do, cn))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/delivery-orders/{id}", response_model=DeliveryOrderResponse)
async def get_delivery_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    cn = await _get_customer_name(db, do.customer_id)
    return _to_response(do, cn)


@router.post("/delivery-orders", response_model=DeliveryOrderResponse, status_code=201)
async def create_delivery_order(body: DeliveryOrderCreate, db: AsyncSession = Depends(get_db)):
    do = DeliveryOrder(**body.model_dump())
    db.add(do)
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    return _to_response(do, cn)


@router.put("/delivery-orders/{id}", response_model=DeliveryOrderResponse)
async def update_delivery_order(id: str, body: DeliveryOrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(do, key, val)
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    return _to_response(do, cn)


@router.delete("/delivery-orders/{id}", response_model=MessageResponse)
async def delete_delivery_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(do)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
