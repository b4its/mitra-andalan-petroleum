from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.deps import get_db
from app.models.activity import Activity
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.activity import ActivityResponse, ActivityFilter

router = APIRouter()


@router.get(
    "/activities",
    response_model=PaginatedResponse[ActivityResponse],
    summary="List activities",
    description="Daftar semua aktivitas sistem dengan filter."
)
async def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    actor_name: str | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    user_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get paginated activities with optional filters"""
    
    # Build query
    query = select(Activity).order_by(Activity.created_at.desc())
    
    # Apply filters
    if action:
        query = query.where(Activity.action == action)
    
    if resource_type:
        query = query.where(Activity.resource_type == resource_type)
    
    if actor_name:
        query = query.where(Activity.actor_name.ilike(f"%{actor_name}%"))
    
    if user_id:
        query = query.where(Activity.user_id == user_id)
    
    if from_date:
        query = query.where(Activity.created_at >= from_date)
    
    if to_date:
        query = query.where(Activity.created_at <= to_date)
    
    # Get total count
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()
    
    # Get paginated results
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    activities = result.scalars().all()
    
    return {
        "items": activities,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get(
    "/activities/{id}",
    response_model=ActivityResponse,
    summary="Detail activity",
    description="Detail aktivitas berdasarkan ID."
)
async def get_activity(id: str, db: AsyncSession = Depends(get_db)):
    """Get single activity by ID"""
    result = await db.execute(select(Activity).where(Activity.id == id))
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity tidak ditemukan")
    
    return activity
