import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.upload import Upload
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.invoice import (
    InvoiceResponse,
    InvoiceCreate,
    InvoiceUpdate,
)

router = APIRouter()


def _details_to_str(details: dict[str, Any] | None) -> str | None:
    return json.dumps(details) if details else None


def _details_from_str(details: str | None) -> dict[str, Any] | None:
    return json.loads(details) if details else None


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
        details=_details_from_str(inv.details),
        created_at=inv.created_at, updated_at=inv.updated_at,
    )


@router.get(
    "/invoices",
    response_model=PaginatedResponse[InvoiceResponse],
    summary="List invoices",
    description="Daftar invoice dengan pagination. Menyertakan nama customer.",
)
async def list_invoices(
    page: int = 1, page_size: int = 20,
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    base = select(Invoice)
    if search:
        base = base.where(or_(
            Invoice.invoice_number.ilike(f"%{search}%"),
            Invoice.invoice_status.ilike(f"%{search}%"),
            Invoice.deadline_status.ilike(f"%{search}%"),
        ))
    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = base.order_by(Invoice.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    invoices = result.scalars().all()

    items = []
    for inv in invoices:
        cn = await _get_customer_name(db, inv.customer_id)
        items.append(_to_response(inv, cn))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/invoices/{id}",
    response_model=InvoiceResponse,
    summary="Detail invoice",
    description="Detail invoice termasuk field `details` JSON.",
)
async def get_invoice(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    cn = await _get_customer_name(db, inv.customer_id)
    return _to_response(inv, cn)


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=201,
    summary="Buat invoice",
    description="Membuat invoice baru. Field `details` untuk data form frontend (products, paymentStatus, dll).",
)
async def create_invoice(body: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump()
    data["details"] = _details_to_str(data.pop("details", None))
    inv = Invoice(**data)
    db.add(inv)
    await db.flush()
    await db.refresh(inv)
    cn = await _get_customer_name(db, inv.customer_id)
    return _to_response(inv, cn)


@router.put(
    "/invoices/{id}",
    response_model=InvoiceResponse,
    summary="Update invoice",
    description="Update invoice (status, details, dll).",
)
async def update_invoice(id: str, body: InvoiceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        if key == "details":
            val = _details_to_str(val)
        setattr(inv, key, val)
    await db.flush()
    await db.refresh(inv)
    cn = await _get_customer_name(db, inv.customer_id)
    return _to_response(inv, cn)


async def _delete_upload_files(uploads: list[Upload]):
    from pathlib import Path
    MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
    for u in uploads:
        fp = MEDIA_DIR / u.folder / u.stored_filename
        if fp.exists():
            fp.unlink()


@router.delete(
    "/invoices/{id}",
    response_model=MessageResponse,
    summary="Hapus invoice",
    description="Hapus invoice berdasarkan ID. Upload terkait juga ikut terhapus.",
)
async def delete_invoice(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")
    upl_result = await db.execute(
        select(Upload).where(Upload.document_type == "invoice", Upload.document_id == id)
    )
    uploads = upl_result.scalars().all()
    await _delete_upload_files(uploads)
    for u in uploads:
        await db.delete(u)
    await db.delete(inv)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
