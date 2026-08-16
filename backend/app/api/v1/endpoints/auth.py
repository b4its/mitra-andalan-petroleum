from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import bcrypt
from sqlalchemy import select

from app.api.deps import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()


@router.post(
    "/auth/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Autentikasi user dengan email & password.\n\nAkun default:\n- `admin@mapetroleum.co.id` / `admin123` (admin)\n- `ops@mapetroleum.co.id` / `ops123` (operations)\n- `marketing@mapetroleum.co.id` / `marketing123` (marketing)\n- `finance@mapetroleum.co.id` / `finance123` (finance)",
)
async def login(body: LoginRequest, db=Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not bcrypt.verify(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return LoginResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        token=f"token-{user.id}",
        logged_in_at=datetime.now(timezone.utc).isoformat(),
    )
