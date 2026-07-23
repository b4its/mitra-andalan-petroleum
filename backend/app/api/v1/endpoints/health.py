from fastapi import APIRouter

from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/health", response_model=MessageResponse)
async def health_check():
    return MessageResponse(message="OK", code=200)
