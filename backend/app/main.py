import mimetypes
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import v1_router
from app.api.v1.endpoints.uploads import FALLBACK_MIME
from app.core.config import settings
from app.core.database import engine, async_session_factory

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"

# Container tanpa file mime.types tidak mengenali beberapa ekstensi
# (mis. .xlsx, .docx). Daftarkan eksplisit agar StaticFiles mengirim
# content-type yang benar.
for _ext, _mime in FALLBACK_MIME.items():
    mimetypes.add_type(_mime, _ext)


@asynccontextmanager
async def lifespan(app: FastAPI):
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    from app.db.migrate import run_migrations
    await run_migrations()
    async with async_session_factory() as session:
        from app.db.seed import seed_database
        await seed_database(session)
    yield
    await engine.dispose()


openapi_tags = [
    {"name": "health", "description": "Cek status server"},
    {"name": "auth", "description": "Login user"},
    {"name": "customers", "description": "CRUD data customer (termasuk `phone2` untuk telepon PIC / penanggung jawab)."},
    {"name": "suppliers", "description": "CRUD data supplier (termasuk `phone2`, `bank_name`, `bank_account` untuk informasi pembayaran)."},
    {"name": "profiles", "description": "CRUD user/profile. User punya `signature` (URL upload tanda tangan) dan `signature_caption` (penanda siapa)."},
    {"name": "offering-letters", "description": "Surat penawaran harga (marketing). Mendukung PPH, metode pembayaran (cash/kredit), term pembayaran, tenggat PO, dan tanda tangan (QR/barcode). Relasi `uploads` (one-to-many) untuk file signature/dokumen."},
    {"name": "purchase-orders", "description": "Purchase order ke customer/supplier. PO supplier punya alur `rilis dana` oleh admin (`status_rilis_dana` + `rilis_dana_at`) sebelum surat bisa dilihat. Relasi `uploads` (one-to-many)."},
    {"name": "delivery-orders", "description": "Delivery order (operational) dengan status alur pengiriman (rilis dana, ready order, selesai dikirim, lunas ongkir). Relasi `uploads` (one-to-many) untuk foto bukti/dokumen return."},
    {"name": "invoices", "description": "Invoice/penagihan (finance). Tanpa sales order number, produk terhubung otomatis dari PO, `Dibuat Oleh` dari user login. Relasi `uploads` (one-to-many)."},
    {"name": "sales", "description": "Data penjualan"},
    {"name": "notifications", "description": "Notifikasi sistem. Field: `to` (redirect path), `is_read` (status baca), `role` (target role)."},
    {"name": "stats", "description": "Statistik untuk dashboard"},
    {"name": "uploads", "description": "Upload file (signature, dokumen, foto, dll). Multi-file, max 50MB/file. Kaitkan ke parent via `document_type` (`ol`/`po`/`do`/`invoice`/`profile`) + `document_id`. Cascade delete otomatis saat parent dihapus."},
    {"name": "accounting", "description": "Modul akuntansi: chart of accounts, jurnal umum, buku besar seluruh akun (`ledger-all`), pemasukan, pengeluaran, neraca saldo, kas harian, rekap monitoring (filter range tanggal), dan ringkasan keuangan."},
    {"name": "admin-database", "description": "Admin database: export dan import data SQL."},
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    summary="API Backend Mitra Andalan Petroleum",
    description="""
Sistem manajemen internal untuk perusahaan bahan bakar minyak.

## Modul
- **Marketing** — Offering Letters (PPH, metode pembayaran, tenggat PO), Purchase Orders, Stats
- **Operations** — Delivery Orders (nomor DO otomatis), Surat PO Transportir, Stats
- **Finance** — Invoices, Delivery Orders, Accounting (akun, jurnal, buku besar semua akun, pemasukan, pengeluaran, monitoring), Stats
- **Admin** — User/Profile Management, Data DO, Data PO Supplier (rilis dana), Database

## Auth
Login via `POST /api/v1/auth/login` — dapatkan token untuk autentikasi.
Belum ada middleware token, semua endpoint publik untuk development.

## Startup (container)
`python -m app.db.boot` → tunggu database → migrasi skema (`app.db.migrate`) → seeder (`app.db.seed`) → uvicorn.

## Data Format
- Dokumen (OL, PO, DO, Invoice) — field `details` JSON untuk data form frontend, dan `uploads` (relasi one-to-many ke file upload)
- PO Supplier — alur rilis dana oleh admin: `status_rilis_dana` (bool) + `rilis_dana_at` (datetime). Sebelum dirilis, surat belum bisa dilihat.
- User — `signature` (URL upload tanda tangan) + `signature_caption`; tanda tangan tampil sebagai QR/barcode di dokumen marketing.
- Notifikasi — field `to` (redirect path), `is_read` (status baca), `role` (target role)
- Upload — support multi-file, max 50MB per file, otomatis cascade delete saat parent dihapus
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
from app.api.v1.endpoints import status_translations
app.include_router(status_translations.router, prefix="/api/v1", tags=["Status Translations"])
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
