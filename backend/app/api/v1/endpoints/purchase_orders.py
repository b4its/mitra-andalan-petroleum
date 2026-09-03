import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from app.models.purchase_order import PurchaseOrder
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.upload import Upload
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.purchase_order import (
    PurchaseOrderResponse,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
)
from app.utils.notifications import create_document_notification, valid_sender_id

router = APIRouter()

WITA = ZoneInfo("Asia/Makassar")


def _details_to_str(details: dict[str, Any] | None) -> str | None:
    return json.dumps(details) if details else None


def _details_from_str(details: str | None) -> dict[str, Any] | None:
    return json.loads(details) if details else None


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
        details=_details_from_str(po.details),
        created_by=po.created_by,
        id_offering_letters=po.id_offering_letters,
        rilis_dana_at=po.rilis_dana_at,
        status_rilis_dana=po.status_rilis_dana,
        created_at=po.created_at, updated_at=po.updated_at,
    )


@router.get(
    "/purchase-orders",
    response_model=PaginatedResponse[PurchaseOrderResponse],
    summary="List purchase orders",
)
async def list_purchase_orders(
    page: int = 1, page_size: int = 20, type: str | None = None,
    search: str | None = Query(default=None),
    offering_letter_id: str | None = Query(
        default=None,
        description="Filter PO yang terkait dengan offering letter (dicocokkan pada id_offering_letters)",
    ),
    db: AsyncSession = Depends(get_db)
):
    base = select(PurchaseOrder)
    if type:
        base = base.where(PurchaseOrder.type == type)
    if search:
        base = base.where(or_(
            PurchaseOrder.po_number.ilike(f"%{search}%"),
            PurchaseOrder.status.ilike(f"%{search}%"),
        ))
    if offering_letter_id:
        base = base.where(PurchaseOrder.id_offering_letters.like(f'%"{offering_letter_id}"%'))
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


@router.get(
    "/purchase-orders/{id}",
    response_model=PurchaseOrderResponse,
    summary="Detail purchase order",
)
async def get_purchase_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    cn, sn = await _resolve_names(db, po)
    return _to_response(po, cn, sn)


@router.post(
    "/purchase-orders",
    response_model=PurchaseOrderResponse,
    status_code=201,
    summary="Buat purchase order",
    description="Membuat PO baru. PO tidak membuat DO otomatis; DO dibuat dari PO di modul Operations (id_purchase_order).",
)
async def create_purchase_order(request: Request, body: PurchaseOrderCreate, db: AsyncSession = Depends(get_db)):
    if body.customer_id:
        c = await db.execute(select(Customer).where(Customer.id == body.customer_id))
        if not c.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Customer tidak ditemukan")
    if body.supplier_id:
        s = await db.execute(select(Supplier).where(Supplier.id == body.supplier_id))
        if not s.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Supplier tidak ditemukan")
    data = body.model_dump()
    data["details"] = _details_to_str(data.pop("details", None))
    # created_by dari browser bisa basi (mis. setelah DB di-reseed & user id berubah);
    # validasi dulu agar penyimpanan tidak gagal karena constraint FK.
    data["created_by"] = await valid_sender_id(db, data.get("created_by"))
    po = PurchaseOrder(**data)
    db.add(po)
    await db.flush()
    await db.refresh(po)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="purchase_order",
        resource_id=po.id,
        resource_name=po.po_number,
        old_data=None,
        new_data=model_to_dict(po),
        details=f"Purchase Order {po.po_number} ({po.type}) berhasil dibuat"
    )
    cn, sn = await _resolve_names(db, po)
    party = cn if po.type == "customer" else sn

    await create_document_notification(
        db,
        title=f"Purchase Order {po.type.capitalize()} Baru",
        message=f"PO {po.po_number} untuk {party} telah dibuat.",
        type="info",
        sender_id=po.created_by,
        to="/marketing/customer" if po.type == "customer" else "/marketing/supplier",
    )
    await db.refresh(po)
    return _to_response(po, cn, sn)


@router.put(
    "/purchase-orders/{id}",
    response_model=PurchaseOrderResponse,
    summary="Update purchase order",
)
async def update_purchase_order(request: Request, id: str, body: PurchaseOrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(po)
    for key, val in body.model_dump(exclude_unset=True).items():
        if key == "details":
            val = _details_to_str(val)
        setattr(po, key, val)
    await db.flush()
    await db.refresh(po)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="purchase_order",
        resource_id=po.id,
        resource_name=po.po_number,
        old_data=old_data,
        new_data=model_to_dict(po),
        details=f"Data Purchase Order {po.po_number} berhasil diperbarui"
    )
    cn, sn = await _resolve_names(db, po)
    return _to_response(po, cn, sn)


@router.post(
    "/purchase-orders/{id}/rilis-dana",
    response_model=PurchaseOrderResponse,
    status_code=200,
    summary="Rilis dana PO supplier",
    description="Menandai PO supplier bahwa dana sudah dirilis oleh admin. Setelah dirilis, surat PO supplier dapat dilihat.",
)
async def rilis_dana_purchase_order(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    if po.type != "supplier":
        raise HTTPException(status_code=400, detail="Rilis dana hanya untuk PO supplier")
    old_data = model_to_dict(po)
    now = datetime.now(WITA)
    po.rilis_dana_at = now
    po.status_rilis_dana = True
    await db.flush()
    await db.refresh(po)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="purchase_order",
        resource_id=po.id,
        resource_name=po.po_number,
        old_data=old_data,
        new_data=model_to_dict(po),
        details=f"Dana PO {po.po_number} telah dirilis"
    )
    cn, sn = await _resolve_names(db, po)
    return _to_response(po, cn, sn)


async def _delete_upload_files(uploads: list[Upload]):
    from pathlib import Path
    MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
    for u in uploads:
        fp = MEDIA_DIR / u.folder / u.stored_filename
        if fp.exists():
            fp.unlink()


@router.delete(
    "/purchase-orders/{id}",
    response_model=MessageResponse,
    summary="Hapus purchase order",
)
async def delete_purchase_order(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == id))
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    po_name = po.po_number
    old_data = model_to_dict(po)
    upl_result = await db.execute(
        select(Upload).where(Upload.document_type == "po", Upload.document_id == id)
    )
    uploads = upl_result.scalars().all()
    await _delete_upload_files(uploads)
    for u in uploads:
        await db.delete(u)
    await db.delete(po)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="purchase_order",
        resource_id=id,
        resource_name=po_name,
        old_data=old_data,
        new_data=None,
        details=f"Purchase Order {po_name} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
