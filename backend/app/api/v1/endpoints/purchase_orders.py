from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.purchase_order import PurchaseOrder
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.purchase_order import (
    PurchaseOrderResponse,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
)

router = APIRouter()


async def _resolve_names(db, po):
    customer_name = ""
    supplier_name = ""
    if po.customer_id:
        c = await db.execute(select(Customer).where(Customer.id == po.customer_id))
        c_obj = c.scalar_one_or_none()
        if c_obj:
            customer_name = c_obj.name
    if po.supplier_id:
        s = await db.execute(select(Supplier).where(Supplier.id == po.supplier_id))
        s_obj = s.scalar_one_or_none()
        if s_obj:
            supplier_name = s_obj.name
    return customer_name, supplier_name


def _to_response(po, customer_name, supplier_name):
    return PurchaseOrderResponse(
        id=po.id, po_number=po.po_number, type=po.type,
        customer_id=po.customer_id, supplier_id=po.supplier_id,
        customer_name=customer_name, supplier_name=supplier_name,
        date=po.date, total=po.total, status=po.status,
        created_at=po.created_at, updated_at=po.updated_at,
    )


@router.get("/purchase-orders", response_model=PaginatedResponse[PurchaseOrderResponse])
async def list_purchase_orders(
    page: int = 1, page_size: int = 20, type: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    base = select(PurchaseOrder)
    if type:
        base = base.where(PurchaseOrder.type == type)
    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = base.order_by(PurchaseOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    pos = result.scalars().all()

    items = []
    for po in pos:
        cn, sn = await _resolve_names(db, po)
        items.append(_to_response(po, cn, sn))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/purchase-orders/{id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Not found")
    cn, sn = await _resolve_names(db, po)
    return _to_response(po, cn, sn)


@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=201)
async def create_purchase_order(body: PurchaseOrderCreate, db: AsyncSession = Depends(get_db)):
    po = PurchaseOrder(**body.model_dump())
    db.add(po)
    await db.flush()
    await db.refresh(po)
    cn, sn = await _resolve_names(db, po)
    return _to_response(po, cn, sn)


@router.put("/purchase-orders/{id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(id: str, body: PurchaseOrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(po, key, val)
    await db.flush()
    await db.refresh(po)
    cn, sn = await _resolve_names(db, po)
    return _to_response(po, cn, sn)


@router.delete("/purchase-orders/{id}", response_model=MessageResponse)
async def delete_purchase_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(po)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
