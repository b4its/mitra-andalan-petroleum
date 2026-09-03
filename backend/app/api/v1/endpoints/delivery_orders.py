import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from app.models.delivery_order import DeliveryOrder
from app.models.customer import Customer
from app.models.offering_letter import OfferingLetter
from app.models.purchase_order import PurchaseOrder
from app.models.po_transportir import PoTransportir
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


async def _get_po_transportir_number(db, po_transportir_id):
    if not po_transportir_id:
        return None
    pt = await db.get(PoTransportir, po_transportir_id)
    return pt.po_number if pt else None


async def _sync_offering_letters(
    db: AsyncSession, po_id: str | None, po_number: str | None, do_id: str
) -> None:
    po = None
    if po_id:
        po_result = await db.execute(
            select(PurchaseOrder).where(PurchaseOrder.id == po_id)
        )
        po = po_result.scalar_one_or_none()
    if po is None and po_number:
        po_result = await db.execute(
            select(PurchaseOrder).where(
                PurchaseOrder.type == "customer",
                PurchaseOrder.po_number == po_number,
            ).limit(1)
        )
        po = po_result.scalar_one_or_none()
    if not po:
        return
    try:
        ol_ids = json.loads(po.id_offering_letters or "[]")
    except (json.JSONDecodeError, TypeError):
        return
    if not isinstance(ol_ids, list):
        return
    do_result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == do_id))
    do_ = do_result.scalar_one_or_none()
    do_details = _details_from_str(do_.details) if do_ else None
    if not do_details:
        return
    for ol_id in ol_ids:
        if not isinstance(ol_id, str):
            continue
        ol_result = await db.execute(select(OfferingLetter).where(OfferingLetter.id == ol_id))
        ol = ol_result.scalar_one_or_none()
        if not ol:
            continue
        existing = _details_from_str(ol.details) or {}
        existing["deliveryOrder"] = do_details
        ol.details = json.dumps(existing, default=str)
        ol.status = "do_completed"
    await db.flush()


def _to_response(do, customer_name, po_transportir_number=None):
    return DeliveryOrderResponse(
        id=do.id, do_number=do.do_number,
        customer_id=do.customer_id, customer_name=customer_name,
        id_purchase_order=do.id_purchase_order,
        id_po_transportir=do.id_po_transportir,
        po_number=do.po_number, po_transportir_number=po_transportir_number,
        transport_name=do.transport_name,
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
    description="Daftar delivery order. Filter `status_rilis_dana=true` untuk Operations. Filter `purchase_order_id` untuk riwayat DO dari satu PO.",
)
async def list_delivery_orders(
    page: int = 1, page_size: int = 20,
    search: str | None = Query(default=None),
    status_rilis_dana: bool | None = Query(default=None),
    purchase_order_id: str | None = Query(
        default=None,
        description="Filter DO yang berparent ke purchase order ini",
    ),
    po_transportir_id: str | None = Query(
        default=None,
        description="Filter DO yang berparent ke PO Transportir ini",
    ),
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
    if purchase_order_id:
        base = base.where(DeliveryOrder.id_purchase_order == purchase_order_id)
    if po_transportir_id:
        base = base.where(DeliveryOrder.id_po_transportir == po_transportir_id)
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
    # Resolve po_transportir numbers untuk list
    potrans_ids = {do.id_po_transportir for do in dos if do.id_po_transportir}
    potrans_map = {}
    if potrans_ids:
        pt_rows = await db.execute(select(PoTransportir).where(PoTransportir.id.in_(potrans_ids)))
        potrans_map = {pt.id: pt.po_number for pt in pt_rows.scalars().all()}
    for do in dos:
        cn = await _get_customer_name(db, do.customer_id)
        items.append(_to_response(do, cn, potrans_map.get(do.id_po_transportir)))
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
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    cn = await _get_customer_name(db, do.customer_id)
    potrans_number = None
    if do.id_po_transportir:
        pt = await db.get(PoTransportir, do.id_po_transportir)
        if pt:
            potrans_number = pt.po_number
    return _to_response(do, cn, potrans_number)


@router.post(
    "/delivery-orders",
    response_model=DeliveryOrderResponse,
    status_code=201,
    summary="Buat delivery order",
    description="Membuat DO baru. Jika id_purchase_order diberikan, data PO (po_number, customer, fuel_total) otomatis diambil dari PO.",
)
async def create_delivery_order(request: Request, body: DeliveryOrderCreate, db: AsyncSession = Depends(get_db)):
    data = body.model_dump()
    data["details"] = _details_to_str(data.pop("details", None))

    # ── Resolusi PO Transportir (alur baru) ──────────────────────
    po_transportir_number = None
    if data.get("id_po_transportir"):
        pt_result = await db.execute(
            select(PoTransportir).where(PoTransportir.id == data["id_po_transportir"])
        )
        pt = pt_result.scalar_one_or_none()
        if not pt:
            raise HTTPException(status_code=400, detail="PO Transportir tidak ditemukan")
        po_transportir_number = pt.po_number
        # Resolve parent PO Customer dari PoTransportir
        if pt.id_purchase_order:
            po_res = await db.execute(
                select(PurchaseOrder).where(PurchaseOrder.id == pt.id_purchase_order)
            )
            parent_po = po_res.scalar_one_or_none()
            if parent_po:
                data["id_purchase_order"] = parent_po.id
                data["po_number"] = data.get("po_number") or parent_po.po_number
        # Copy customer_id dari PoTransportir
        if not data.get("customer_id") and pt.customer_id:
            data["customer_id"] = pt.customer_id
        # Copy transport_name dari receiver PO Transportir
        if not data.get("transport_name") and pt.receiver:
            data["transport_name"] = pt.receiver
        # Jika fuel_total tidak diisi, gunakan total PO Transportir
        if not data.get("fuel_total"):
            data["fuel_total"] = pt.total or 0

    # ── Resolusi PO parent (alur lama) ────────────────────────────
    po = None
    if data.get("id_purchase_order") and not data.get("id_po_transportir"):
        po_result = await db.execute(
            select(PurchaseOrder).where(PurchaseOrder.id == data["id_purchase_order"])
        )
        po = po_result.scalar_one_or_none()
        if not po:
            raise HTTPException(status_code=400, detail="Purchase order tidak ditemukan")
        data["id_purchase_order"] = po.id
        data["po_number"] = data.get("po_number") or po.po_number
        if not data.get("customer_id"):
            data["customer_id"] = po.customer_id
        if not data.get("fuel_total"):
            data["fuel_total"] = po.total or 0

    do = DeliveryOrder(**data)
    db.add(do)
    await db.flush()
    await db.refresh(do)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="delivery_order",
        resource_id=do.id,
        resource_name=do.do_number,
        old_data=None,
        new_data=model_to_dict(do),
        details=f"Delivery Order {do.do_number} berhasil dibuat"
    )
    cn = await _get_customer_name(db, do.customer_id)
    await _sync_offering_letters(db, do.id_purchase_order, do.po_number, do.id)
    await create_document_notification(
        db,
        title="Delivery Order Baru Dibuat",
        message=f"DO {do.do_number} untuk {cn} telah dibuat.",
        type="info",
        sender_id=do.created_by,
        to="/operations",
    )
    return _to_response(do, cn, po_transportir_number)


@router.put(
    "/delivery-orders/{id}",
    response_model=DeliveryOrderResponse,
    summary="Update delivery order",
)
async def update_delivery_order(request: Request, id: str, body: DeliveryOrderUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(do)
    for key, val in body.model_dump(exclude_unset=True).items():
        if key == "details":
            val = _details_to_str(val)
        setattr(do, key, val)
    if do.id_purchase_order:
        po_result = await db.execute(
            select(PurchaseOrder).where(PurchaseOrder.id == do.id_purchase_order)
        )
        po = po_result.scalar_one_or_none()
        if po and not do.po_number:
            do.po_number = po.po_number
    await db.flush()
    await db.refresh(do)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="delivery_order",
        resource_id=do.id,
        resource_name=do.do_number,
        old_data=old_data,
        new_data=model_to_dict(do),
        details=f"Data Delivery Order {do.do_number} berhasil diperbarui"
    )
    cn = await _get_customer_name(db, do.customer_id)
    await _sync_offering_letters(db, do.id_purchase_order, do.po_number, do.id)
    po_transportir_number = await _get_po_transportir_number(db, do.id_po_transportir)
    return _to_response(do, cn, po_transportir_number)


@router.post(
    "/delivery-orders/{id}/rilis-dana",
    response_model=DeliveryOrderResponse,
    summary="Rilis Dana",
    description="Finance: tandai rilis dana. DO akan muncul di Operations.",
)
async def rilis_dana(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    if do.status_rilis_dana:
        raise HTTPException(status_code=400, detail="Dana sudah dirilis sebelumnya")
    old_data = model_to_dict(do)
    now_wita = datetime.now(WITA)
    do.rilis_dana_at = now_wita
    do.status_rilis_dana = True
    await db.flush()
    await db.refresh(do)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="delivery_order",
        resource_id=do.id,
        resource_name=do.do_number,
        old_data=old_data,
        new_data=model_to_dict(do),
        details=f"Dana Delivery Order {do.do_number} telah dirilis"
    )
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
async def ready_order(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    if do.status_ready_order:
        raise HTTPException(status_code=400, detail="Pengantaran sudah disiapkan sebelumnya")
    old_data = model_to_dict(do)
    now_wita = datetime.now(WITA)
    do.ready_order_at = now_wita
    do.status_ready_order = True
    await db.flush()
    await db.refresh(do)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="delivery_order",
        resource_id=do.id,
        resource_name=do.do_number,
        old_data=old_data,
        new_data=model_to_dict(do),
        details=f"Pengantaran DO {do.do_number} telah disiapkan"
    )
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
    description="Operations: konfirmasi pengiriman selesai. Item yang diantar ditandai 'delivered' pada PO Transportir; jika semua item diantar, PO Transportir berstatus completed. PO Supplier terkait dicatat end-to-end sampai ke customer.",
)
async def selesai_dikirim(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    if not do.status_ready_order:
        raise HTTPException(status_code=400, detail="Pengantaran belum disiapkan")
    if do.status_selesai_dikirim:
        raise HTTPException(status_code=400, detail="Pengiriman sudah ditandai selesai")
    old_data = model_to_dict(do)
    now_wita = datetime.now(WITA)
    do.selesai_dikirim_at = now_wita
    do.status_selesai_dikirim = True

    # ── Tandai item yang diantar pada PO Transportir terkait ────
    pt_updated = False
    do_details = _details_from_str(do.details) or {}
    delivered_items = do_details.get("selectedProducts") or []
    if do.id_po_transportir:
        pt = await db.get(PoTransportir, do.id_po_transportir)
        if pt:
            pt_details = _details_from_str(pt.details) or {}
            pt_products = pt_details.get("products") or []
            if isinstance(pt_products, list) and pt_products:
                # Tandai produk yang cocok (by name) sebagai delivered
                delivered_names = {
                    (it.get("name") or "").strip()
                    for it in delivered_items if isinstance(it, dict)
                }
                for prod in pt_products:
                    if not isinstance(prod, dict):
                        continue
                    name = (prod.get("name") or "").strip()
                    if name and (not delivered_names or name in delivered_names):
                        prod["delivered"] = True
                        prod["delivered_at"] = now_wita.strftime("%d/%m/%Y %H:%M")
                pt_details["products"] = pt_products
                pt.details = _details_to_str(pt_details)
                # Jika semua item sudah diantar → status completed
                all_delivered = all(
                    isinstance(p, dict) and p.get("delivered")
                    for p in pt_products if isinstance(p, dict)
                )
                if all_delivered and pt.status != "completed":
                    pt.status = "completed"
                await db.flush()
                pt_updated = True

    # ── Catat PO Supplier end-to-end (pesanan diantar sampai customer) ──
    if pt_updated and do.id_po_transportir:
        pt = await db.get(PoTransportir, do.id_po_transportir)
        if pt and pt.id_purchase_order:
            # PO Customer dari PO Transportir → ambil offering letters terkait
            po_customer = await db.get(PurchaseOrder, pt.id_purchase_order)
            if po_customer and po_customer.id_offering_letters:
                try:
                    ol_ids = set(json.loads(po_customer.id_offering_letters))
                except (TypeError, json.JSONDecodeError):
                    ol_ids = set()
                if ol_ids:
                    # Cari PO Supplier yang berbagi offering letter
                    po_suppliers = (
                        await db.execute(
                            select(PurchaseOrder).where(
                                PurchaseOrder.type == "supplier",
                                PurchaseOrder.id_offering_letters.is_not(None),
                            )
                        )
                    ).scalars().all()
                    for spo in po_suppliers:
                        try:
                            spo_ol = set(json.loads(spo.id_offering_letters))
                        except (TypeError, json.JSONDecodeError):
                            continue
                        if spo_ol & ol_ids:
                            spo_details = _details_from_str(spo.details) or {}
                            spo_details["delivered"] = True
                            spo_details["delivered_at"] = now_wita.strftime("%d/%m/%Y %H:%M")
                            spo_details["sampai_customer"] = True
                            spo_details["sampai_customer_at"] = now_wita.strftime("%d/%m/%Y %H:%M")
                            spo.details = _details_to_str(spo_details)
                            await db.flush()

    await db.flush()
    await db.refresh(do)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="delivery_order",
        resource_id=do.id,
        resource_name=do.do_number,
        old_data=old_data,
        new_data=model_to_dict(do),
        details=f"Pengiriman DO {do.do_number} telah selesai dikirim"
    )
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
    description="Admin/Finance: tandai pelunasan ongkir. Tersedia setelah Operations menandai pengiriman selesai (status_selesai_dikirim).",
)
async def lunas_ongkir(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    if not do.status_selesai_dikirim:
        raise HTTPException(status_code=400, detail="Pengiriman belum ditandai selesai oleh Operations")
    if do.status_lunas_ongkir:
        raise HTTPException(status_code=400, detail="Ongkir sudah dilunasi sebelumnya")
    old_data = model_to_dict(do)
    now_wita = datetime.now(WITA)
    do.lunas_ongkir_at = now_wita
    do.status_lunas_ongkir = True
    await db.flush()
    await db.refresh(do)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="delivery_order",
        resource_id=do.id,
        resource_name=do.do_number,
        old_data=old_data,
        new_data=model_to_dict(do),
        details=f"Ongkir DO {do.do_number} telah dilunasi"
    )
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
async def delete_delivery_order(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryOrder).where(DeliveryOrder.id == id))
    do = result.scalar_one_or_none()
    if not do:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    do_name = do.do_number
    old_data = model_to_dict(do)
    upl_result = await db.execute(
        select(Upload).where(Upload.document_type == "do", Upload.document_id == id)
    )
    uploads = upl_result.scalars().all()
    await _delete_upload_files(uploads)
    for u in uploads:
        await db.delete(u)
    await db.delete(do)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="delivery_order",
        resource_id=id,
        resource_name=do_name,
        old_data=old_data,
        new_data=None,
        details=f"Delivery Order {do_name} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
