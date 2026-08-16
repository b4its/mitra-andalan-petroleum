"""
Helper untuk membuat notifikasi otomatis saat CRUD dokumen.

Notifikasi dibuat di dalam savepoint (nested transaction) sehingga jika terjadi
kesalahan — misalnya `sender_id` tidak ditemukan di tabel users (stale user id
setelah database di-reseed) — kegagalan notifikasi TIDAK menggagalkan penyimpanan
dokumen utama (mencegah HTTP 500).
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User


async def valid_sender_id(db: AsyncSession, sender_id: str | None) -> str | None:
    """Pastikan sender_id benar-benar ada di tabel users, jika tidak kembalikan None."""
    if not sender_id:
        return None
    result = await db.execute(select(User.id).where(User.id == sender_id))
    return sender_id if result.scalar_one_or_none() else None


async def create_document_notification(
    db: AsyncSession,
    *,
    title: str,
    message: str,
    type: str = "info",
    sender_id: str | None = None,
    to: str | None = None,
    role: str | None = None,
) -> None:
    """Buat notifikasi baru. Dipanggil setelah dokumen berhasil disimpan.

    Aman digunakan: tidak akan melempar error ke pemanggil. Jika validasi atau
    insert notifikasi gagal, hanya notifikasi yang dibatalkan (rollback ke
    savepoint), dokumen utama tetap tersimpan.
    """
    try:
        async with db.begin_nested():
            # Hindari ForeignKeyViolation di tabel notifications saat user id
            # sudah tidak ada di tabel users (stale id dari localStorage).
            safe_sender_id = await valid_sender_id(db, sender_id)
            n = Notification(
                title=title,
                message=message,
                type=type,
                sender_id=safe_sender_id,
                role=role,
                to=to,
                is_read=False,
            )
            db.add(n)
            # Flush di dalam savepoint agar error FK muncul di sini dan hanya
            # merollback notifikasi, bukan seluruh transaksi dokumen.
            await db.flush()
    except Exception:
        # Jangan sampai notifikasi menggagalkan operasi dokumen utama.
        pass
