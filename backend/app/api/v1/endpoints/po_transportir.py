import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.po_transportir import PoTransportir
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.po_transportir import (
    PoTransportirResponse,
    PoTransportirCreate,
    PoTransportirUpdate,
)
from app.utils.notifications import create_document_notification

router = APIRouter()


def _details_to_str(details: dict[str, Any] | None) -> str | None:
    return json.dumps(details) if details else None


def _details_from_str(details: str | None) -> dict[str, Any] | None:
    return json.loads(details) if details else None


def _to_response(po: PoTransportir) -> PoTransportirResponse:
    return PoTransportirResponse(
        id=po.id,
        po_number=po.po_number,
        date=po.date,
        pic_person=po.pic_person,
        receiver=po.receiver,
        total=po.total,
        status=po.status,
        details=_details_from_str(po.details),
        created_by=po.created_by,
        created_at=po.created_at,
        updated_at=po.updated_at,
    )


@router.get(
    "/po-transportir",
    response_model=PaginatedResponse[PoTransportirResponse],
    summary="List PO transportir",
    description="Menampilkan daftar Purchase Order Transportir dengan pagination.",
)
async def list_po_transportir(
    page: int = 1, page_size: int = 20, search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    filters = []
    if search:
        filters.append(or_(
            PoTransportir.po_number.ilike(f"%{search}%"),
            PoTransportir.receiver.ilike(f"%{search}%"),
            PoTransportir.pic_person.ilike(f"%{search}%"),
        ))
    if status:
        filters.append(PoTransportir.status == status)

    base = select(PoTransportir)
    if filters:
        base = base.where(*filters)
    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = base.order_by(PoTransportir.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return PaginatedResponse(
        items=[_to_response(po) for po in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/po-transportir/{id}",
    response_model=PoTransportirResponse,
    summary="Detail PO transportir",
)
async def get_po_transportir(id: str, db: AsyncSession = Depends(get_db)):
    po = await db.get(PoTransportir, id)
    if not po:
        raise HTTPException(status_code=404, detail="PO Transportir tidak ditemukan")
    return _to_response(po)


@router.post(
    "/po-transportir",
    response_model=PoTransportirResponse,
    summary="Buat PO transportir",
    status_code=201,
)
async def create_po_transportir(body: PoTransportirCreate, db: AsyncSession = Depends(get_db)):
    po = PoTransportir(
        po_number=body.po_number,
        date=body.date,
        pic_person=body.pic_person,
        receiver=body.receiver,
        total=body.total,
        status=body.status or "created",
        details=_details_to_str(body.details),
        created_by=body.created_by,
    )
    db.add(po)
    await db.flush()

    await create_document_notification(
        db,
        title="PO Transportir Baru",
        message=f"PO Transportir {po.po_number} ke {po.receiver or '-'} berhasil dibuat.",
        type="info",
        sender_id=body.created_by,
        role="operations",
        to="/operations/rekap-po-transportir",
    )

    await db.commit()
    await db.refresh(po)
    return _to_response(po)


@router.put(
    "/po-transportir/{id}",
    response_model=PoTransportirResponse,
    summary="Perbarui PO transportir",
)
async def update_po_transportir(
    id: str, body: PoTransportirUpdate, db: AsyncSession = Depends(get_db)
):
    po = await db.get(PoTransportir, id)
    if not po:
        raise HTTPException(status_code=404, detail="PO Transportir tidak ditemukan")

    if body.po_number is not None:
        po.po_number = body.po_number
    if body.date is not None:
        po.date = body.date
    if body.pic_person is not None:
        po.pic_person = body.pic_person
    if body.receiver is not None:
        po.receiver = body.receiver
    if body.total is not None:
        po.total = body.total
    if body.status is not None:
        po.status = body.status
    if body.details is not None:
        po.details = _details_to_str(body.details)

    await db.commit()
    await db.refresh(po)
    return _to_response(po)


@router.delete(
    "/po-transportir/{id}",
    response_model=MessageResponse,
    summary="Hapus PO transportir",
)
async def delete_po_transportir(id: str, db: AsyncSession = Depends(get_db)):
    po = await db.get(PoTransportir, id)
    if not po:
        raise HTTPException(status_code=404, detail="PO Transportir tidak ditemukan")
    await db.delete(po)
    await db.commit()
    return MessageResponse(message="PO Transportir dihapus")