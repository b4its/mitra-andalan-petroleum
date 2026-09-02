import uuid
from pathlib import Path
import re
import subprocess
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from app.models.upload import Upload
from app.schemas.upload import UploadResponse, UploadUpdate
from app.schemas.common import MessageResponse

router = APIRouter()

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "media"
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".pdf", ".doc", ".docx", ".xls", ".xlsx"}
DOCUMENT_TYPES = {"ol", "po", "do", "invoice", "profile"}

# Fallback karena mimetypes.guess_type di container tanpa file mime.types
# mengembalikan None untuk beberapa ekstensi (mis. .xlsx, .docx).
FALLBACK_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _safe_folder(folder: str) -> str:
    folder = (folder or "general").strip().strip("/")
    if not folder or not re.fullmatch(r"[A-Za-z0-9_-]+", folder):
        raise HTTPException(status_code=400, detail="Nama folder hanya boleh berisi huruf, angka, garis bawah, dan garis pisah")
    return folder


def _delete_file(upload: Upload):
    file_path = MEDIA_DIR / upload.folder / upload.stored_filename
    if file_path.exists():
        file_path.unlink()


async def _process_single_file(file: UploadFile, folder: str, document_type: str | None, document_id: str | None, db: AsyncSession) -> Upload:
    folder = _safe_folder(folder)
    ext = Path(file.filename or "").suffix.lower()
    if not ext:
        raise HTTPException(status_code=400, detail="File harus memiliki ekstensi")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File tidak boleh kosong")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File terlalu besar (maks 50MB)")

    target_dir = MEDIA_DIR / folder
    _ensure_dir(target_dir)

    import mimetypes
    mime_type = mimetypes.guess_type(file.filename or "")[0] or FALLBACK_MIME.get(ext, "application/octet-stream")
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


@router.post(
    "/upload",
    response_model=list[UploadResponse],
    status_code=201,
    summary="Upload file(s)",
    description="Upload satu atau banyak file (max 50MB per file). Kaitkan ke dokumen dengan `document_type` (ol/po/do/invoice/profile) dan `document_id`. `profile` dipakai untuk tanda tangan user aplikasi.",
)
async def upload_files(
    request: Request,
    files: list[UploadFile] = File(..., description="Satu atau banyak file"),
    folder: str = Form("general"),
    document_type: str | None = Form(None),
    document_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    folder = _safe_folder(folder)
    if document_type and document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"document_type must be one of {DOCUMENT_TYPES}")
    if (document_type and not document_id) or (document_id and not document_type):
        raise HTTPException(status_code=400, detail="Harus menyertakan document_type dan document_id sekaligus")

    results = []
    try:
        for file in files:
            upload = await _process_single_file(file, folder, document_type, document_id, db)
            results.append(upload)
        actor = actor_from_request(request)
        await log_activity(
            db=db,
            request=request,
            user_id=actor["user_id"],
            actor_name=actor["actor_name"],
            actor_role=actor["actor_role"],
            action="create",
            resource_type="upload",
            resource_id=results[0].id if results else None,
            resource_name=", ".join(u.original_filename for u in results),
            old_data=None,
            new_data=[model_to_dict(u) for u in results] if results else {},
            details=f"{len(results)} file berhasil di-upload ke {folder}"
        )
    except Exception:
        for upload in results:
            _delete_file(upload)
        raise
    return results


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
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return upload


@router.put(
    "/uploads/{id}",
    response_model=UploadResponse,
    summary="Update upload",
    description="Update metadata upload (folder, document_type, document_id).",
)
async def update_upload(request: Request, id: str, body: UploadUpdate, db: AsyncSession = Depends(get_db)):
    if body.document_type and body.document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"document_type must be one of {DOCUMENT_TYPES}")
    if body.folder is not None:
        body.folder = _safe_folder(body.folder)

    result = await db.execute(select(Upload).where(Upload.id == id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")

    old_data = model_to_dict(upload)

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

    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="upload",
        resource_id=upload.id,
        resource_name=upload.original_filename,
        old_data=old_data,
        new_data=model_to_dict(upload),
        details=f"Upload {upload.original_filename} berhasil diperbarui"
    )

    return upload


@router.delete(
    "/uploads/{id}",
    response_model=MessageResponse,
    summary="Hapus upload",
    description="Hapus file upload dari disk dan database.",
)
async def delete_upload(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).where(Upload.id == id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    u_name = upload.original_filename
    old_data = model_to_dict(upload)
    _delete_file(upload)
    await db.delete(upload)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="upload",
        resource_id=id,
        resource_name=u_name,
        old_data=old_data,
        new_data=None,
        details=f"Upload {u_name} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)


@router.get(
    "/uploads/{id}/pdf",
    summary="Convert DOCX to PDF",
    description="Konversi file .docx ke PDF menggunakan LibreOffice untuk preview di browser.",
)
async def convert_docx_to_pdf(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Upload).where(Upload.id == id))
    upload = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")

    ext = Path(upload.original_filename).suffix.lower()
    if ext not in (".doc", ".docx"):
        raise HTTPException(status_code=400, detail="Hanya file .doc dan .docx yang dapat dikonversi")

    src_path = MEDIA_DIR / upload.folder / upload.stored_filename
    if not src_path.exists():
        raise HTTPException(status_code=404, detail="File sumber tidak ditemukan di disk")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_src = Path(tmpdir) / upload.stored_filename
        tmp_src.write_bytes(src_path.read_bytes())

        try:
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    tmpdir,
                    str(tmp_src),
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Gagal konversi ke PDF: {e.stderr.decode(errors='replace') or e.stdout.decode(errors='replace') or str(e)}"
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Konversi ke PDF gagal (timeout atau libreoffice tidak tersedia): {e}"
            )

        pdf_name = f"{Path(upload.stored_filename).stem}.pdf"
        pdf_path = Path(tmpdir) / pdf_name

        if not pdf_path.exists():
            raise HTTPException(status_code=500, detail="File PDF hasil konversi tidak ditemukan")

        pdf_bytes = pdf_path.read_bytes()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{Path(upload.original_filename).stem}.pdf"'},
    )
