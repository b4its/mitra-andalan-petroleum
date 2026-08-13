#!/bin/sh
# Entrypoint container backend Mandalan.
# Menunggu database siap, menjalankan migrasi & seeder, lalu memulai uvicorn.
# Dibuat agar "pertama kali dijalankan" tidak crash-loop karena database
# belum siap / migrasi belum jalan.

set -e

cd /app

echo "[entrypoint] Menunggu database MySQL siap..."
python - <<'PY'
import asyncio
import sys

async def wait_db():
    from app.core.database import engine
    from sqlalchemy import text
    for i in range(30):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("[entrypoint] Database siap.")
            return
        except Exception as e:
            print(f"[entrypoint] DB belum siap ({i + 1}/30): {type(e).__name__}")
            await asyncio.sleep(2)
    print("[entrypoint] ERROR: database tidak dapat dijangkau.")
    sys.exit(1)

asyncio.run(wait_db())
PY

echo "[entrypoint] Menjalankan migrasi skema..."
python -m app.db.migrate

echo "[entrypoint] Menjalankan seeder..."
python -m app.db.seed

echo "[entrypoint] Memulai server uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
