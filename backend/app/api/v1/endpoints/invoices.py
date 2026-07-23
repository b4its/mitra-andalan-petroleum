from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.invoice import (
    InvoiceResponse,
    InvoiceCreate,
    InvoiceUpdate,
)

router = APIRouter()


async def _get_customer_name(db, customer_id):
    if not customer_id:
        return ""
    c = await db.execute(select(Customer).where(Customer.id == customer_id))
    c_obj = c.scalar_one_or_none()
    return c_obj.name if c_obj else ""


def _to_response(inv, customer_name):
    return InvoiceResponse(
        id=inv.id, invoice_number=inv.invoice_number,
        customer_id=inv.customer_id, customer_name=customer_name,
        terms_day=inv.terms_day, grand_total=inv.grand_total,
        invoice_status=inv.invoice_status, deadline_status=inv.deadline_status,
        created_at=inv.created_at, updated_at=inv.updated_at,
    )


@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse])
async def list_invoices(
    page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)
):
    total_result = await db.execute(select(func.count()).select_from(select(Invoice).subquery()))
    total = total_result.scalar() or 0

    stmt = select(Invoice).order_by(Invoice.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    invoices = result.scalars().all()

    items = []
    for inv in invoices:
        cn = await _get_customer_name(db, inv.customer_id)
        items.append(_to_response(inv, cn))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/invoices/{id}", response_model=InvoiceResponse)
async def get_invoice(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    cn = await _get_customer_name(db, inv.customer_id)
    return _to_response(inv, cn)


@router.post("/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(body: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    inv = Invoice(**body.model_dump())
    db.add(inv)
    await db.flush()
    await db.refresh(inv)
    cn = await _get_customer_name(db, inv.customer_id)
    return _to_response(inv, cn)


@router.put("/invoices/{id}", response_model=InvoiceResponse)
async def update_invoice(id: str, body: InvoiceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(inv, key, val)
    await db.flush()
    await db.refresh(inv)
    cn = await _get_customer_name(db, inv.customer_id)
    return _to_response(inv, cn)


@router.delete("/invoices/{id}", response_model=MessageResponse)
async def delete_invoice(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(inv)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
