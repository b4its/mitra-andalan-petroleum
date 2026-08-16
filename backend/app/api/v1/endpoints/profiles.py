from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import User
from app.schemas.profile import (
    ProfileResponse,
    ProfileDemoResponse,
    ProfileCreate,
    ProfileUpdate,
)
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get(
    "/profiles",
    response_model=list[ProfileResponse],
    summary="List users",
    description="Daftar semua user/profile (terbaru di atas). User memiliki `signature` (URL tanda tangan) dan `signature_caption` (penanda siapa).",
)
async def list_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/profiles/demo",
    response_model=list[ProfileDemoResponse],
    summary="List users (demo)",
    description=(
        "Sama seperti GET /profiles, tetapi menyertakan kolom password "
        "(password yang tersimpan) untuk keperluan DEMO/login bantuan. "
        "Jangan dipakai di production."
    ),
)
async def list_profiles_demo(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "password": u.demo_password or "",
        }
        for u in users
    ]


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
    data = body.model_dump()
    data["password"] = bcrypt.hash(data["password"])
    data["demo_password"] = body.password
    user = User(**data)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.put(
    "/profiles/{id}",
    response_model=ProfileResponse,
    summary="Update user",
    description="Update data user/profile, termasuk `signature` dan `signature_caption` (caption tanda tangan).",
)
async def update_profile(id: str, body: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    if "password" in data:
        data["password"] = bcrypt.hash(data["password"])
        data["demo_password"] = body.password
    for key, val in data.items():
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
