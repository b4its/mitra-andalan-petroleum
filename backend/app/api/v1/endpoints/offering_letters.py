import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.offering_letter import OfferingLetter
from app.models.customer import Customer
from app.models.purchase_order import PurchaseOrder
from app.models.delivery_order import DeliveryOrder
from app.models.upload import Upload
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.offering_letter import (
    OfferingLetterResponse,
    OfferingLetterCreate,
    OfferingLetterUpdate,
    OfferingLetterPurchaseOrderItem,
    OfferingLetterPurchaseOrdersResponse,
)
from app.utils.notifications import create_document_notification, valid_sender_id

router = APIRouter()


def _details_to_str(details: dict[str, Any] | None) -> str | None:
    return json.dumps(details) if details else None


def _details_from_str(details: str | None) -> dict[str, Any] | None:
    return json.loads(details) if details else None


def _to_response(ol: OfferingLetter, customer_name: str) -> OfferingLetterResponse:
    return OfferingLetterResponse(
        id=ol.id, offering_letter_number=ol.offering_letter_number,
        customer_id=ol.customer_id, customer_name=customer_name,
        location=ol.location, date=ol.date, regarding=ol.regarding,
        receiver=ol.receiver, fuel_total_price=ol.fuel_total_price,
        transport_price=ol.transport_price, status=ol.status,
        details=_details_from_str(ol.details),
        created_by=ol.created_by,
        created_at=ol.created_at, updated_at=ol.updated_at,
    )


@router.get(
    "/offering-letters",
    response_model=PaginatedResponse[OfferingLetterResponse],
    summary="List offering letters",
    description="Menampilkan daftar surat penawaran dengan pagination. Menyertakan nama customer.",
)
async def list_offering_letters(
    page: int = 1, page_size: int = 20, search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    base = (
        select(OfferingLetter)
        .outerjoin(Customer, OfferingLetter.customer_id == Customer.id)
    )
    if search:
        base = base.where(or_(
            OfferingLetter.offering_letter_number.ilike(f"%{search}%"),
            OfferingLetter.receiver.ilike(f"%{search}%"),
            OfferingLetter.status.ilike(f"%{search}%"),
            Customer.name.ilike(f"%{search}%"),
        ))
    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = (
        select(OfferingLetter, Customer.name.label("customer_name"))
        .outerjoin(Customer, OfferingLetter.customer_id == Customer.id)
    )
    if search:
        stmt = stmt.where(or_(
            OfferingLetter.offering_letter_number.ilike(f"%{search}%"),
            OfferingLetter.receiver.ilike(f"%{search}%"),
            OfferingLetter.status.ilike(f"%{search}%"),
            Customer.name.ilike(f"%{search}%"),
        ))
    stmt = stmt.order_by(OfferingLetter.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    rows = result.all()

    items = [_to_response(ol, cn) for ol, cn in rows]
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/offering-letters/{id}/purchase-orders",
    response_model=OfferingLetterPurchaseOrdersResponse,
    summary="Purchase order & delivery order terkait offering letter",
    description="Menampilkan purchase order yang terhubung ke surat penawaran (via `id_offering_letters`) beserta delivery order terkait tiap purchase order (via `id_purchase_order`).",
)
async def get_offering_letter_purchase_orders(
    id: str, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(OfferingLetter).where(OfferingLetter.id == id))
    ol = result.scalar_one_or_none()
    if not ol:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")

    pos = (await db.execute(select(PurchaseOrder))).scalars().all()
    customers_by_id = {}
    suppliers_by_id = {}
    if pos:
        customers_by_id = {
            c.id: c
            for c in (await db.execute(select(Customer))).scalars().all()
        }
    from app.models.supplier import Supplier
    if pos:
        suppliers_by_id = {
            s.id: s
            for s in (await db.execute(select(Supplier))).scalars().all()
        }

    items: list[OfferingLetterPurchaseOrderItem] = []
    for po in pos:
        if not po.id_offering_letters:
            continue
        try:
            linked_ids = json.loads(po.id_offering_letters)
        except (TypeError, json.JSONDecodeError):
            continue
        if not linked_ids or id not in [str(x) for x in linked_ids]:
            continue

        customer = customers_by_id.get(po.customer_id) if po.customer_id else None
        supplier = suppliers_by_id.get(po.supplier_id) if po.supplier_id else None

        dos = (await db.execute(
            select(DeliveryOrder).where(DeliveryOrder.id_purchase_order == po.id)
        )).scalars().all()
        do_items = []
        for do in dos:
            do_customer = customers_by_id.get(do.customer_id) if do.customer_id else None
            do_items.append({
                "id": do.id,
                "do_number": do.do_number,
                "customer_id": do.customer_id,
                "customer_name": do_customer.name if do_customer else "",
                "id_purchase_order": do.id_purchase_order,
                "po_number": do.po_number,
                "transport_name": do.transport_name,
                "fuel_total": do.fuel_total,
                "status": do.status,
                "details": json.loads(do.details) if do.details else None,
            })

        items.append(OfferingLetterPurchaseOrderItem(
            id=po.id,
            po_number=po.po_number,
            type=po.type,
            customer_id=po.customer_id,
            supplier_id=po.supplier_id,
            customer_name=customer.name if customer else "",
            supplier_name=supplier.name if supplier else "",
            date=po.date,
            total=po.total,
            status=po.status,
            created_by=po.created_by,
            created_at=po.created_at,
            updated_at=po.updated_at,
            id_offering_letters=po.id_offering_letters,
            delivery_orders=do_items,
        ))

    return OfferingLetterPurchaseOrdersResponse(items=items)


@router.get(
    "/offering-letters/{id}",
    response_model=OfferingLetterResponse,
    summary="Detail offering letter",
    description="Mendapatkan detail surat penawaran termasuk field `details` JSON.",
)
async def get_offering_letter(id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(OfferingLetter, Customer.name.label("customer_name"))
        .outerjoin(Customer, OfferingLetter.customer_id == Customer.id)
        .where(OfferingLetter.id == id)
    )
    result = await db.execute(stmt)
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    ol, customer_name = row
    return _to_response(ol, customer_name)


@router.post(
    "/offering-letters",
    response_model=OfferingLetterResponse,
    status_code=201,
    summary="Buat offering letter",
    description="Membuat surat penawaran baru. Field `details` bisa diisi dengan form data dari frontend (supplyPoint, fuelPrices, personInCharge, dll).",
)
async def create_offering_letter(request: Request, body: OfferingLetterCreate, db: AsyncSession = Depends(get_db)):
    customer_name = ""
    if body.customer_id:
        customer = await db.execute(select(Customer).where(Customer.id == body.customer_id))
        c = customer.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=400, detail="Customer tidak ditemukan")
        customer_name = c.name
    data = body.model_dump()
    data["details"] = _details_to_str(data.pop("details", None))
    # created_by dari browser bisa basi (mis. setelah DB di-reseed & user id berubah);
    # validasi dulu agar penyimpanan tidak gagal karena constraint FK.
    data["created_by"] = await valid_sender_id(db, data.get("created_by"))
    ol = OfferingLetter(**data)
    db.add(ol)
    await db.flush()
    await db.refresh(ol)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="offering_letter",
        resource_id=ol.id,
        resource_name=ol.offering_letter_number,
        old_data=None,
        new_data=model_to_dict(ol),
        details=f"Surat penawaran {ol.offering_letter_number} berhasil dibuat"
    )
    await create_document_notification(
        db,
        title="Surat Penawaran Baru Dibuat",
        message=f"Surat penawaran {ol.offering_letter_number} untuk {customer_name} telah dibuat.",
        type="info",
        sender_id=ol.created_by,
        to="/marketing/customer",
    )
    return _to_response(ol, customer_name)


@router.put(
    "/offering-letters/{id}",
    response_model=OfferingLetterResponse,
    summary="Update offering letter",
    description="Update field tertentu pada surat penawaran (status, details, dll).",
)
async def update_offering_letter(request: Request, id: str, body: OfferingLetterUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OfferingLetter).where(OfferingLetter.id == id))
    ol = result.scalar_one_or_none()
    if not ol:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(ol)
    data = body.model_dump(exclude_unset=True)
    if "customer_id" in data and data["customer_id"]:
        cust = await db.execute(select(Customer).where(Customer.id == data["customer_id"]))
        if not cust.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Customer tidak ditemukan")
    for key, val in data.items():
        if key == "details":
            val = _details_to_str(val)
        setattr(ol, key, val)
    await db.flush()
    await db.refresh(ol)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="offering_letter",
        resource_id=ol.id,
        resource_name=ol.offering_letter_number,
        old_data=old_data,
        new_data=model_to_dict(ol),
        details=f"Data surat penawaran {ol.offering_letter_number} berhasil diperbarui"
    )
    customer = await db.execute(select(Customer).where(Customer.id == ol.customer_id))
    c = customer.scalar_one_or_none()
    return _to_response(ol, c.name if c else "")

async def _delete_upload_files(uploads: list[Upload]):
    from pathlib import Path
    MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
    for u in uploads:
        fp = MEDIA_DIR / u.folder / u.stored_filename
        if fp.exists():
            fp.unlink()


@router.delete(
    "/offering-letters/{id}",
    response_model=MessageResponse,
    summary="Hapus offering letter",
    description="Menghapus surat penawaran berdasarkan ID. Upload terkait juga ikut terhapus.",
)
async def delete_offering_letter(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OfferingLetter).where(OfferingLetter.id == id))
    ol = result.scalar_one_or_none()
    if not ol:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    ol_name = ol.offering_letter_number
    old_data = model_to_dict(ol)
    upl_result = await db.execute(
        select(Upload).where(Upload.document_type == "ol", Upload.document_id == id)
    )
    uploads = upl_result.scalars().all()
    await _delete_upload_files(uploads)
    for u in uploads:
        await db.delete(u)
    await db.delete(ol)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="offering_letter",
        resource_id=id,
        resource_name=ol_name,
        old_data=old_data,
        new_data=None,
        details=f"Surat penawaran {ol_name} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
