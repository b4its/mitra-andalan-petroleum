import json
import uuid
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.delivery_order import DeliveryOrder
from app.models.customer import Customer
from app.models.upload import Upload
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.delivery_order import (
    DeliveryOrderResponse,
    DeliveryOrderCreate,
    DeliveryOrderUpdate,
)
from app.utils.notifications import create_document_notification

router = APIRouter()

WITA = ZoneInfo("Asia/Makassar")


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


def _to_response(do, customer_name):
    return DeliveryOrderResponse(
        id=do.id, do_number=do.do_number,
        customer_id=do.customer_id, customer_name=customer_name,
        po_number=do.po_number, transport_name=do.transport_name,
        fuel_total=do.fuel_total, status=do.status,
        details=_details_from_str(do.details),
        created_by=do.created_by,
        rilis_dana_at=do.rilis_dana_at,
        status_rilis_dana=do.status_rilis_dana or False,
        ready_order_at=do.ready_order_at,
        status_ready_order=do.status_ready_order or False,
        selesai_dikirim_at=do.selesai_dikirim_at,
        status_selesai_dikirim=do.status_selesai_dikirim or False,
        lunas_ongkir_at=do.lunas_ongkir_at,
        status_lunas_ongkir=do.status_lunas_ongkir or False,
        created_at=do.created_at, updated_at=do.updated_at,
    )


@router.get(
    "/delivery-orders",
    response_model=PaginatedResponse[DeliveryOrderResponse],
    summary="List delivery orders",
    description="Daftar delivery order. Filter `status_rilis_dana=true` untuk Operations.",
)
async def list_delivery_orders(
    page: int = 1, page_size: int = 20,
    search: str | None = Query(default=None),
    status_rilis_dana: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    base = select(DeliveryOrder)
    if search:
        base = base.where(or_(
            DeliveryOrder.do_number.ilike(f"%{search}%"),
            DeliveryOrder.transport_name.ilike(f"%{search}%"),
            DeliveryOrder.status.ilike(f"%{search}%"),
            DeliveryOrder.po_number.ilike(f"%{search}%"),
        ))
    if status_rilis_dana is not None:
        if status_rilis_dana:
            base = base.where(
                DeliveryOrder.status_rilis_dana == True,
                DeliveryOrder.rilis_dana_at.is_not(None)
            )
        else:
            base = base.where(
                (DeliveryOrder.status_rilis_dana == False) |
                DeliveryOrder.rilis_dana_at.is_(None)
            )
    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = base.order_by(DeliveryOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    dos = result.scalars().all()

    items = []
    for do in dos:
        cn = await _get_customer_name(db, do.customer_id)
        items.append(_to_response(do, cn))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/delivery-orders/{id}",
    response_model=DeliveryOrderResponse,
    summary="Detail delivery order",
)
async def get_delivery_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    cn = await _get_customer_name(db, do.customer_id)
    return _to_response(do, cn)


@router.post(
    "/delivery-orders",
    response_model=DeliveryOrderResponse,
    status_code=201,
    summary="Buat delivery order",
)
async def create_delivery_order(body: DeliveryOrderCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump()
    data["details"] = _details_to_str(data.pop("details", None))
    do = DeliveryOrder(**data)
    db.add(do)
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    await create_document_notification(
        db,
        title="Delivery Order Baru Dibuat",
        message=f"DO {do.do_number} untuk {cn} telah dibuat.",
        type="info",
        sender_id=do.created_by,
        to="/operations",
    )
    return _to_response(do, cn)


@router.put(
    "/delivery-orders/{id}",
    response_model=DeliveryOrderResponse,
    summary="Update delivery order",
)
async def update_delivery_order(id: str, body: DeliveryOrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        if key == "details":
            val = _details_to_str(val)
        setattr(do, key, val)
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    return _to_response(do, cn)


@router.post(
    "/delivery-orders/{id}/rilis-dana",
    response_model=DeliveryOrderResponse,
    summary="Rilis Dana",
    description="Finance: tandai rilis dana. DO akan muncul di Operations.",
)
async def rilis_dana(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    if do.status_rilis_dana:
        raise HTTPException(status_code=400, detail="Dana sudah dirilis sebelumnya")
    now_wita = datetime.now(WITA)
    do.rilis_dana_at = now_wita
    do.status_rilis_dana = True
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    await create_document_notification(
        db,
        title="Rilis Dana Delivery Order",
        message=f"Dana untuk DO {do.do_number} telah dirilis pada {now_wita.strftime('%d/%m/%Y %H:%M')} WITA.",
        type="success",
        to="/operations",
    )
    return _to_response(do, cn)


@router.post(
    "/delivery-orders/{id}/ready-order",
    response_model=DeliveryOrderResponse,
    summary="Siapkan Pengantaran",
    description="Operations: tandai pengantaran sudah disiapkan.",
)
async def ready_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    if not do.status_rilis_dana:
        raise HTTPException(status_code=400, detail="Dana belum dirilis oleh Finance")
    if do.status_ready_order:
        raise HTTPException(status_code=400, detail="Pengantaran sudah disiapkan sebelumnya")
    now_wita = datetime.now(WITA)
    do.ready_order_at = now_wita
    do.status_ready_order = True
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    await create_document_notification(
        db,
        title="Pengantaran Disiapkan",
        message=f"DO {do.do_number} siap untuk dikirim pada {now_wita.strftime('%d/%m/%Y %H:%M')} WITA.",
        type="info",
        to="/operations",
    )
    return _to_response(do, cn)


@router.post(
    "/delivery-orders/{id}/selesai-dikirim",
    response_model=DeliveryOrderResponse,
    summary="Selesai Dikirim",
    description="Operations: konfirmasi pengiriman selesai. Finance dapat melunasi ongkir setelah ini.",
)
async def selesai_dikirim(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    if not do.status_ready_order:
        raise HTTPException(status_code=400, detail="Pengantaran belum disiapkan")
    if do.status_selesai_dikirim:
        raise HTTPException(status_code=400, detail="Pengiriman sudah ditandai selesai")
    now_wita = datetime.now(WITA)
    do.selesai_dikirim_at = now_wita
    do.status_selesai_dikirim = True
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    await create_document_notification(
        db,
        title="Pengiriman Selesai",
        message=f"DO {do.do_number} telah selesai dikirim pada {now_wita.strftime('%d/%m/%Y %H:%M')} WITA. Finance dapat melunasi ongkir.",
        type="success",
        to="/finance/do",
    )
    return _to_response(do, cn)


@router.post(
    "/delivery-orders/{id}/lunas-ongkir",
    response_model=DeliveryOrderResponse,
    summary="Lunas Ongkir",
    description="Finance: tandai pelunasan ongkir. Tersedia setelah Operations menandai siap dikirim.",
)
async def lunas_ongkir(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    if not do.status_ready_order:
        raise HTTPException(status_code=400, detail="Pengantaran belum disiapkan oleh Operations")
    if do.status_lunas_ongkir:
        raise HTTPException(status_code=400, detail="Ongkir sudah dilunasi sebelumnya")
    now_wita = datetime.now(WITA)
    do.lunas_ongkir_at = now_wita
    do.status_lunas_ongkir = True
    await db.flush()
    await db.refresh(do)
    cn = await _get_customer_name(db, do.customer_id)
    await create_document_notification(
        db,
        title="Pelunasan Ongkir",
        message=f"Ongkir DO {do.do_number} telah dilunasi pada {now_wita.strftime('%d/%m/%Y %H:%M')} WITA.",
        type="success",
        to="/finance/do",
    )
    return _to_response(do, cn)


async def _delete_upload_files(uploads: list[Upload]):
    from pathlib import Path
    MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
    for u in uploads:
        fp = MEDIA_DIR / u.folder / u.stored_filename
        if fp.exists():
            fp.unlink()


@router.delete(
    "/delivery-orders/{id}",
    response_model=MessageResponse,
    summary="Hapus delivery order",
)
async def delete_delivery_order(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Not found")
    upl_result = await db.execute(
        select(Upload).where(Upload.document_type == "do", Upload.document_id == id)
    )
    uploads = upl_result.scalars().all()
    await _delete_upload_files(uploads)
    for u in uploads:
        await db.delete(u)
    await db.delete(do)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
