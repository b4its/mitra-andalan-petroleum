"""Migrasi skema database ringan (ALTER TABLE idempotent).

Dijalankan otomatis saat backend start (lifespan) DAN sebelum seeder
oleh entrypoint container (`python -m app.db.migrate && python -m app.db.seed`).
"""
import asyncio

from sqlalchemy import text

# PENTING: import semua model agar tabelnya terdaftar di Base.metadata
# sebelum `create_all` dijalankan. Tanpa ini, database baru tidak dibuat
# (create_all diam-diam tidak membuat tabel apa pun).
import app.models  # noqa: F401

from app.core.database import engine, Base


async def run_migrations():
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
        # Kolom baru: informasi pembayaran & telepon 2 pada supplier/customer
        try:
            await conn.execute(text(
                "ALTER TABLE `suppliers` ADD COLUMN `bank_name` VARCHAR(100) NULL "
                "COMMENT 'Nama bank supplier'"
            ))
        except Exception:
            pass
        try:
            await conn.execute(text(
                "ALTER TABLE `suppliers` ADD COLUMN `bank_account` VARCHAR(50) NULL "
                "COMMENT 'Nomor rekening supplier'"
            ))
        except Exception:
            pass
        try:
            await conn.execute(text(
                "ALTER TABLE `suppliers` ADD COLUMN `phone2` VARCHAR(30) NULL "
                "COMMENT 'Nomor telepon 2 supplier'"
            ))
        except Exception:
            pass
        try:
            await conn.execute(text(
                "ALTER TABLE `customers` ADD COLUMN `phone2` VARCHAR(30) NULL "
                "COMMENT 'Nomor telepon PIC / penanggung jawab customer'"
            ))
        except Exception:
            pass
        # Kolom tanda tangan (signature) untuk user aplikasi
        try:
            await conn.execute(text(
                "ALTER TABLE `users` ADD COLUMN `signature` VARCHAR(255) NULL "
                "COMMENT 'URL upload tanda tangan user'"
            ))
        except Exception:
            pass
        # Caption tanda tangan user (penanda siapa yang menandatangani)
        try:
            await conn.execute(text(
                "ALTER TABLE `users` ADD COLUMN `signature_caption` VARCHAR(255) NULL "
                "COMMENT 'Caption tanda tangan (penanda siapa yang menandatangani)'"
            ))
        except Exception:
            pass
        # Kolom rilis dana untuk purchase_orders (sedot dari model delivery_orders)
        try:
            await conn.execute(text(
                "ALTER TABLE `purchase_orders` ADD COLUMN `rilis_dana_at` DATETIME NULL "
                "COMMENT 'Waktu rilis dana (WITA)'"
            ))
        except Exception:
            pass
        try:
            await conn.execute(text(
                "ALTER TABLE `purchase_orders` ADD COLUMN `status_rilis_dana` TINYINT(1) NOT NULL DEFAULT 0 "
                "COMMENT 'True jika dana sudah dirilis'"
            ))
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


async def main():
    print("[migrate] Menjalankan migrasi skema...")
    await run_migrations()
    print("[migrate] Selesai.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        from app.db.session import engine
        # Tutup engine agar tidak ada `Exception ignored` saat interpreter keluar.
        import gc
        import aiomysql.connection  # noqa: F401  (pastikan kelas dimuat)
        gc.collect()
