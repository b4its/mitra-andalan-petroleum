from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.api.deps import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(body: LoginRequest, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or user.password != body.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return LoginResponse(
        name=user.name,
        email=user.email,
        role=user.role,
        token=f"token-{user.id}",
        logged_in_at=datetime.now(timezone.utc).isoformat(),
    )
