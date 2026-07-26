import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.upload import Upload
from app.schemas.upload import UploadResponse, UploadUpdate
from app.schemas.common import MessageResponse

router = APIRouter()

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}
DOCUMENT_TYPES = {"ol", "po", "do", "invoice"}


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _delete_file(upload: Upload):
    file_path = MEDIA_DIR / upload.folder / upload.stored_filename
    if file_path.exists():
        file_path.unlink()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=201,
    summary="Upload file",
    description="Upload file (max 50MB). Kaitkan ke dokumen dengan `document_type` (ol/po/do/invoice) dan `document_id`.",
)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("general"),
    document_type: str | None = Form(None),
    document_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if document_type and document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"document_type must be one of {DOCUMENT_TYPES}")
    if (document_type and not document_id) or (document_id and not document_type):
        raise HTTPException(status_code=400, detail="Both document_type and document_id must be provided together")

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

    import mimetypes
    mime_type = mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = target_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    upload = Upload(
        original_filename=file.filename or unique_name,
        stored_filename=unique_name,
        folder=folder,
        mime_type=mime_type,
        size=len(content),
        url=f"/media/{folder}/{unique_name}",
        document_type=document_type,
        document_id=document_id,
    )
    db.add(upload)
    await db.flush()
    await db.refresh(upload)
    return upload


@router.get(
    "/uploads",
    response_model=list[UploadResponse],
    summary="List uploads",
    description="Daftar semua file upload. Filter dengan `document_type` dan/atau `document_id`.",
)
async def list_uploads(
    document_type: str | None = None,
    document_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Upload).order_by(Upload.created_at.desc())
    if document_type:
        stmt = stmt.where(Upload.document_type == document_type)
    if document_id:
        stmt = stmt.where(Upload.document_id == document_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/uploads/{id}",
    response_model=UploadResponse,
    summary="Detail upload",
    description="Detail file upload berdasarkan ID.",
)
async def get_upload(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).where(Upload.id == id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Not found")
    return upload


@router.put(
    "/uploads/{id}",
    response_model=UploadResponse,
    summary="Update upload",
    description="Update metadata upload (folder, document_type, document_id).",
)
async def update_upload(id: str, body: UploadUpdate, db: AsyncSession = Depends(get_db)):
    if body.document_type and body.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"document_type must be one of {DOCUMENT_TYPES}")

    result = await db.execute(select(Upload).where(Upload.id == id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Not found")

    old_path = None
    if body.folder is not None and body.folder != upload.folder:
        old_path = MEDIA_DIR / upload.folder / upload.stored_filename
        upload.url = f"/media/{body.folder}/{upload.stored_filename}"

    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(upload, key, val)

    await db.flush()
    await db.refresh(upload)

    if old_path and old_path.exists():
        new_dir = MEDIA_DIR / upload.folder
        _ensure_dir(new_dir)
        old_path.rename(MEDIA_DIR / upload.folder / upload.stored_filename)

    return upload


@router.delete(
    "/uploads/{id}",
    response_model=MessageResponse,
    summary="Hapus upload",
    description="Hapus file upload dari disk dan database.",
)
async def delete_upload(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).where(Upload.id == id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Not found")
    _delete_file(upload)
    await db.delete(upload)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)
