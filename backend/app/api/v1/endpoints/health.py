from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=MessageResponse,
    summary="Health check",
    description="Cek apakah server berjalan.",
)
async def health_check():
    return MessageResponse(message="OK", code=200)
