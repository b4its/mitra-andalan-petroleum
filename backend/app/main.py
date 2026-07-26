import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1 import v1_router
from app.core.config import settings
from app.core.database import engine, Base, async_session_factory

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"


@asynccontextmanager
async def lifespan(app: FastAPI):
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        for col in ["`to` VARCHAR(500) NULL", "`is_read` TINYINT(1) NOT NULL DEFAULT 0"]:
            try:
                await conn.execute(text(f"ALTER TABLE notifications ADD COLUMN {col}"))
            except Exception:
                pass
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        from app.db.seed import seed_database
        await seed_database(session)
    yield
    await engine.dispose()


openapi_tags = [
    {"name": "health", "description": "Cek status server"},
    {"name": "auth", "description": "Login user"},
    {"name": "customers", "description": "CRUD data customer"},
    {"name": "suppliers", "description": "CRUD data supplier"},
    {"name": "profiles", "description": "CRUD user/profile management"},
    {"name": "offering-letters", "description": "Surat penawaran harga (marketing)"},
    {"name": "purchase-orders", "description": "Purchase order ke customer/supplier"},
    {"name": "delivery-orders", "description": "Delivery order (operational)"},
    {"name": "invoices", "description": "Invoice/penagihan (finance)"},
    {"name": "sales", "description": "Data penjualan"},
    {"name": "notifications", "description": "Notifikasi sistem"},
    {"name": "stats", "description": "Statistik untuk dashboard"},
    {"name": "uploads", "description": "Upload file (signature, dokumen, dll)"},
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    summary="API Backend Mitra Andalan Petroleum",
    description="""
Sistem manajemen internal untuk perusahaan bahan bakar minyak.

## Modul
- **Marketing** — Offering Letters, Purchase Orders, Stats
- **Operations** — Delivery Orders, Sales, Stats
- **Finance** — Invoices, Delivery Orders, Sales, Stats
- **Admin** — User/Profile Management

## Auth
Login via `POST /api/v1/auth/login` — dapatkan token untuk autentikasi.
Belum ada middleware token, semua endpoint publik untuk development.

## Data Format
Dokumen (OL, PO, DO, Invoice) mendukung field `details` JSON
untuk menyimpan data form yang kompleks dari frontend.
""",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
    contact={
        "name": "Mitra Andalan Petroleum",
        "email": "marketing.mapetroleum@gmail.com",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
