from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
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
        role=n.role,
        to=n.to,
        is_read=n.is_read,
        created_at=n.created_at,
    )


@router.get(
    "/notifications",
    response_model=list[NotificationResponse],
    summary="List notifications",
    description="Daftar notifikasi sistem (terbaru di atas). Filter berdasarkan role jika disediakan.",
)
async def list_notifications(
    role: str | None = Query(default=None, description="Filter notifikasi berdasarkan role target"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Notification).order_by(Notification.created_at.desc())
    if role:
        # Tampilkan notifikasi yang ditujukan untuk role tertentu ATAU untuk semua role (role = null)
        stmt = stmt.where(or_(Notification.role == role, Notification.role.is_(None)))
    result = await db.execute(stmt)
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
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    name = await _get_user_name(db, n.sender_id)
    return _to_response(n, name)


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=201,
    summary="Buat notification",
    description="Membuat notifikasi baru.",
)
async def create_notification(request: Request, body: NotificationCreate, db: AsyncSession = Depends(get_db)):
    n = Notification(**body.model_dump())
    db.add(n)
    await db.flush()
    await db.refresh(n)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="notification",
        resource_id=n.id,
        resource_name=n.title,
        old_data=None,
        new_data=model_to_dict(n),
        details=f"Notifikasi {n.title} berhasil dibuat"
    )
    name = await _get_user_name(db, n.sender_id)
    return _to_response(n, name)


@router.put(
    "/notifications/{id}",
    response_model=NotificationResponse,
    summary="Update notification",
    description="Update notifikasi (read status, dll).",
)
async def update_notification(request: Request, id: str, body: NotificationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(n)
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(n, key, val)
    await db.flush()
    await db.refresh(n)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="notification",
        resource_id=n.id,
        resource_name=n.title,
        old_data=old_data,
        new_data=model_to_dict(n),
        details=f"Notifikasi {n.title} berhasil diperbarui"
    )
    name = await _get_user_name(db, n.sender_id)
    return _to_response(n, name)


@router.delete(
    "/notifications/{id}",
    response_model=MessageResponse,
    summary="Hapus notification",
    description="Hapus notifikasi.",
)
async def delete_notification(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    n_title = n.title
    old_data = model_to_dict(n)
    await db.delete(n)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="notification",
        resource_id=id,
        resource_name=n_title,
        old_data=old_data,
        new_data=None,
        details=f"Notifikasi {n_title} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)
