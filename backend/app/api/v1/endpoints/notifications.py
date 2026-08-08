from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationUpdate,
)
from app.schemas.common import MessageResponse

router = APIRouter()


async def _get_user_name(db: AsyncSession, user_id: str | None) -> str | None:
    if not user_id:
        return None
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    return u.name if u else None


def _to_response(n: Notification, user_name: str | None = None) -> NotificationResponse:
    return NotificationResponse(
        id=n.id,
        title=n.title,
        message=n.message,
        type=n.type,
        sender_id=n.sender_id,
        user_name=user_name,
        to=n.to,
        is_read=n.is_read,
        created_at=n.created_at,
    )


@router.get(
    "/notifications",
    response_model=list[NotificationResponse],
    summary="List notifications",
    description="Daftar notifikasi sistem (terbaru di atas). Menyertakan nama pengguna jika sender_id tersedia.",
)
async def list_notifications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Notification).order_by(Notification.created_at.desc())
    )
    notifications = result.scalars().all()
    items = []
    for n in notifications:
        name = await _get_user_name(db, n.sender_id)
        items.append(_to_response(n, name))
    return items


@router.get(
    "/notifications/{id}",
    response_model=NotificationResponse,
    summary="Detail notification",
    description="Detail notifikasi berdasarkan ID.",
)
async def get_notification(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    name = await _get_user_name(db, n.sender_id)
    return _to_response(n, name)


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=201,
    summary="Buat notification",
    description="Membuat notifikasi baru.",
)
async def create_notification(body: NotificationCreate, db: AsyncSession = Depends(get_db)):
    n = Notification(**body.model_dump())
    db.add(n)
    await db.flush()
    await db.refresh(n)
    name = await _get_user_name(db, n.sender_id)
    return _to_response(n, name)


@router.put(
    "/notifications/{id}",
    response_model=NotificationResponse,
    summary="Update notification",
    description="Update notifikasi (read status, dll).",
)
async def update_notification(id: str, body: NotificationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(n, key, val)
    await db.flush()
    await db.refresh(n)
    name = await _get_user_name(db, n.sender_id)
    return _to_response(n, name)


@router.delete(
    "/notifications/{id}",
    response_model=MessageResponse,
    summary="Hapus notification",
    description="Hapus notifikasi.",
)
async def delete_notification(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(n)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
