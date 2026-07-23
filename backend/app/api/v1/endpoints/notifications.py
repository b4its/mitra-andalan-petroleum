from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationUpdate,
)
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Notification).order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.get("/notifications/{id}", response_model=NotificationResponse)
async def get_notification(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    return n


@router.post("/notifications", response_model=NotificationResponse, status_code=201)
async def create_notification(body: NotificationCreate, db: AsyncSession = Depends(get_db)):
    n = Notification(**body.model_dump())
    db.add(n)
    await db.flush()
    await db.refresh(n)
    return n


@router.put("/notifications/{id}", response_model=NotificationResponse)
async def update_notification(id: str, body: NotificationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(n, key, val)
    await db.flush()
    await db.refresh(n)
    return n


@router.delete("/notifications/{id}", response_model=MessageResponse)
async def delete_notification(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).where(Notification.id == id))
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(n)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
