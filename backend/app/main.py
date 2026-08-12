import mimetypes
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1 import v1_router
from app.api.v1.endpoints.uploads import FALLBACK_MIME
from app.core.config import settings
from app.core.database import engine, Base, async_session_factory

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"

# Container tanpa file mime.types tidak mengenali beberapa ekstensi
# (mis. .xlsx, .docx). Daftarkan eksplisit agar StaticFiles mengirim
# content-type yang benar.
for _ext, _mime in FALLBACK_MIME.items():
    mimetypes.add_type(_mime, _ext)


@asynccontextmanager
async def lifespan(app: FastAPI):
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        # Kolom lama yang ditambahkan sebelumnya
        for col in ["`to` VARCHAR(500) NULL", "`is_read` TINYINT(1) NOT NULL DEFAULT 0"]:
            try:
                await conn.execute(text(f"ALTER TABLE notifications ADD COLUMN {col}"))
            except Exception:
                pass
        # Kolom created_by untuk tracking user input dokumen
        for table in ["offering_letters", "purchase_orders", "delivery_orders"]:
            try:
                await conn.execute(text(
                    f"ALTER TABLE `{table}` ADD COLUMN `created_by` VARCHAR(36) NULL "
                    f"COMMENT 'ID user yang membuat dokumen'"
                ))
            except Exception:
                pass
        # Kolom npwp untuk customer
        try:
            await conn.execute(text(
                "ALTER TABLE `customers` ADD COLUMN `npwp` VARCHAR(20) NULL "
                "COMMENT 'Nomor Pokok Wajib Pajak customer'"
            ))
        except Exception:
            pass
        # Kolom npwp untuk supplier
        try:
            await conn.execute(text(
                "ALTER TABLE `suppliers` ADD COLUMN `npwp` VARCHAR(20) NULL "
                "COMMENT 'Nomor Pokok Wajib Pajak supplier'"
            ))
        except Exception:
            pass
        # Kolom provinsi/kota untuk supplier dan customer
        for table in ["suppliers", "customers"]:
            for col in [
                "`province` VARCHAR(100) NULL COMMENT 'Provinsi'",
                "`city` VARCHAR(100) NULL COMMENT 'Kota/Kabupaten'",
            ]:
                try:
                    await conn.execute(text(f"ALTER TABLE `{table}` ADD COLUMN {col}"))
                except Exception:
                    pass
        # Buat relasi customer_id nullable agar dokumen tetap bisa dibuat
        # meskipun customer belum terdaftar (mencegah error insert).
        for table in ["offering_letters", "delivery_orders", "invoices"]:
            try:
                await conn.execute(text(
                    f"ALTER TABLE `{table}` MODIFY COLUMN `customer_id` VARCHAR(36) NULL"
                ))
            except Exception:
                pass
        # Kolom role untuk notification (target role)
        try:
            await conn.execute(text(
                "ALTER TABLE `notifications` ADD COLUMN `role` VARCHAR(20) NULL "
                "COMMENT 'Target role notifikasi (accounting, admin, dll)'"
            ))
        except Exception:
            pass
        # Kolom baru delivery_orders: rilis dana + lunas ongkir
        do_new_cols = [
            "`rilis_dana_at` DATETIME NULL COMMENT 'Waktu rilis dana (WITA)'",
            "`status_rilis_dana` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'True jika dana sudah dirilis'",
            "`ready_order_at` DATETIME NULL COMMENT 'Waktu pengantaran disiapkan (WITA)'",
            "`status_ready_order` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'True jika pengantaran sudah disiapkan'",
            "`selesai_dikirim_at` DATETIME NULL COMMENT 'Waktu selesai dikirim (WITA)'",
            "`status_selesai_dikirim` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'True jika pengiriman sudah selesai'",
            "`lunas_ongkir_at` DATETIME NULL COMMENT 'Waktu pelunasan ongkir (WITA)'",
            "`status_lunas_ongkir` TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'True jika ongkir sudah dilunasi'",
            "`id_purchase_order` VARCHAR(36) NULL COMMENT 'ID purchase order (parent). Satu PO dapat memiliki banyak DO'",
        ]
        for col in do_new_cols:
            try:
                await conn.execute(text(f"ALTER TABLE `delivery_orders` ADD COLUMN {col}"))
            except Exception:
                pass
        # Kolom baru purchase_orders: relasi ke OL
        po_new_cols = [
            "`id_offering_letters` TEXT NULL COMMENT 'JSON array: ID offering letter terkait'",
        ]
        for col in po_new_cols:
            try:
                await conn.execute(text(f"ALTER TABLE `purchase_orders` ADD COLUMN {col}"))
            except Exception:
                pass
        # Backfill: hubungkan DO lama (DO-DRAFT atau tanpa id_purchase_order)
        # ke PO parent berdasarkan po_number. Satu PO dapat memiliki banyak DO.
        try:
            await conn.execute(text(
                """
                UPDATE delivery_orders do
                JOIN purchase_orders po
                  ON po.po_number = do.po_number
                SET do.id_purchase_order = po.id
                WHERE do.id_purchase_order IS NULL
                  AND do.po_number IS NOT NULL
                """
            ))
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
    {"name": "offering-letters", "description": "Surat penawaran harga (marketing). Memiliki relasi `uploads` (one-to-many) untuk file signature, dokumen pendukung."},
    {"name": "purchase-orders", "description": "Purchase order ke customer/supplier. Memiliki relasi `uploads` (one-to-many) untuk dokumen PO, lampiran."},
    {"name": "delivery-orders", "description": "Delivery order (operational). Memiliki relasi `uploads` (one-to-many) untuk foto bukti, dokumen return."},
    {"name": "invoices", "description": "Invoice/penagihan (finance). Memiliki relasi `uploads` (one-to-many) untuk lampiran invoice."},
    {"name": "sales", "description": "Data penjualan"},
    {"name": "notifications", "description": "Notifikasi sistem. Field: `to` (redirect path), `is_read` (status baca)."},
    {"name": "stats", "description": "Statistik untuk dashboard"},
    {"name": "uploads", "description": "Upload file (signature, dokumen, foto, dll). Multi-file, max 50MB/file. Kaitkan ke parent via `document_type` + `document_id`. Cascade delete otomatis saat parent dihapus."},
    {"name": "accounting", "description": "Modul akuntansi (finance): chart of accounts, jurnal umum, buku besar, pemasukan, pengeluaran, neraca saldo, dan ringkasan keuangan."},
    {"name": "admin-database", "description": "Admin database: export dan import data SQL."},
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
- **Finance** — Invoices, Delivery Orders, Accounting (akun, jurnal, buku besar, pemasukan, pengeluaran), Stats
- **Admin** — User/Profile Management

## Auth
Login via `POST /api/v1/auth/login` — dapatkan token untuk autentikasi.
Belum ada middleware token, semua endpoint publik untuk development.

## Data Format
- Dokumen (OL, PO, DO, Invoice) — field `details` JSON untuk data form frontend, dan `uploads` (relasi one-to-many ke file upload)
- Notifikasi — field `to` (redirect path) dan `is_read` (status baca)
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
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
