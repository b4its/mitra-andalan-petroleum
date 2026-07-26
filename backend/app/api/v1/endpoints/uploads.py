import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.schemas.common import MessageResponse

router = APIRouter()

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


@router.post(
    "/upload",
    summary="Upload file",
    description="Upload file (max 50MB). Gunakan `folder` untuk menentukan subfolder (signatures, documents, returned, dll). Return URL yang bisa diakses.",
)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("general"),
):
    ext = Path(file.filename or "").suffix.lower()
    if not ext:
        raise HTTPException(status_code=400, detail="File must have an extension")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    target_dir = MEDIA_DIR / folder
    _ensure_dir(target_dir)

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = target_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": unique_name,
        "url": f"/media/{folder}/{unique_name}",
        "size": len(content),
    }
