"""Boot container backend: tunggu DB -> migrasi -> seeder -> uvicorn.

Sengaja memakai Python (bukan shell script) agar tidak terpengaruh
CRLF/LF ketika repo di-clone di Windows — penyebab error klasik
`set: Illegal option -` / `: not found` pada entrypoint .sh.

Jalankan: python -m app.db.boot
"""

import asyncio
import os
import sys

from sqlalchemy import text


async def _wait_db(timeout_seconds: int = 60) -> None:
    """Tunggu sampai database MySQL bisa diakses (retry tiap 2 detik)."""
    from app.core.database import engine

    print("[boot] Menunggu database MySQL siap...")
    attempts = timeout_seconds // 2
    for i in range(attempts):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("[boot] Database siap.")
            return
        except Exception as e:  # noqa: BLE001 - log semua jenis error koneksi
            print(f"[boot] DB belum siap ({i + 1}/{attempts}): {type(e).__name__}")
            await asyncio.sleep(2)
    print("[boot] ERROR: database tidak dapat dijangkau.")
    sys.exit(1)


async def main() -> None:
    from app.core.database import async_session_factory, engine

    await _wait_db()

    print("[boot] Menjalankan migrasi skema...")
    from app.db.migrate import run_migrations

    await run_migrations()
    print("[boot] Migrasi selesai.")

    print("[boot] Menjalankan seeder...")
    from app.db.seed import seed_database

    session = async_session_factory()
    try:
        await seed_database(session)
    finally:
        await session.close()
        await engine.dispose()
    print("[boot] Seeder selesai.")

    print("[boot] Memulai server uvicorn...")
    os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8012"])


if __name__ == "__main__":
    asyncio.run(main())
