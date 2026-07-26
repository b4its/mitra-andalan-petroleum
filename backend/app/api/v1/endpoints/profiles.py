from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileCreate, ProfileUpdate
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get(
    "/profiles",
    response_model=list[ProfileResponse],
    summary="List users",
    description="Daftar semua user/profile (diurutkan berdasarkan nama).",
)
async def list_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.name))
    return result.scalars().all()


@router.get(
    "/profiles/{id}",
    response_model=ProfileResponse,
    summary="Detail user",
    description="Detail user/profile berdasarkan ID.",
)
async def get_profile(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@router.post(
    "/profiles",
    response_model=ProfileResponse,
    status_code=201,
    summary="Buat user",
    description="Mendaftarkan user baru (email harus unik).",
)
async def create_profile(body: ProfileCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(**body.model_dump())
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.put(
    "/profiles/{id}",
    response_model=ProfileResponse,
    summary="Update user",
    description="Update data user/profile.",
)
async def update_profile(id: str, body: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(user, key, val)
    await db.flush()
    await db.refresh(user)
    return user


@router.delete(
    "/profiles/{id}",
    response_model=MessageResponse,
    summary="Hapus user",
    description="Hapus user berdasarkan ID.",
)
async def delete_profile(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(user)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
