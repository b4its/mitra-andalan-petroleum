"""
Helper untuk membuat notifikasi otomatis saat CRUD dokumen.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_document_notification(
    db: AsyncSession,
    *,
    title: str,
    message: str,
    type: str = "info",
    sender_id: str | None = None,
    to: str | None = None,
) -> None:
    """Buat notifikasi baru. Dipanggil setelah dokumen berhasil disimpan."""
    n = Notification(
        title=title,
        message=message,
        type=type,
        sender_id=sender_id,
        to=to,
        is_read=False,
    )
    db.add(n)
    # Tidak perlu flush/commit — akan di-commit bersamaan dengan parent transaction
