# Seeder Database — Mitra Andalan Petroleum

## Apa itu seeder?

Seeder adalah script yang mengisi database dengan **data contoh (data demo)**:
user, customer, supplier, offering letter, purchase order, delivery order,
invoice, notifikasi, penjualan, dan data akuntansi (bagan akun + jurnal umum).

Lokasi: `backend/app/db/seed.py` — dijalankan lewat `python -m app.db.seed`.

## Kapan seeder berjalan?

1. **Otomatis saat backend start** — `docker-compose.yml` service `backend`
   menjalankan **migrasi skema** lalu seeder sebelum uvicorn:
   `python -m app.db.migrate && python -m app.db.seed && uvicorn ...`.
   Artinya setiap `docker compose --profile full up -d --build` =
   **migrasi + build + seed menyatu**. Fungsi `seed_database` di lifespan
   (`backend/app/main.py`) tetap ada sebagai cadangan.
2. **Manual** — lewat `make seed` / `make reseed` / `make seed-check`
   (lihat di bawah), atau `python -m app.db.seed [--force] [--check]` langsung
   di folder `backend`.

### Guard anti-hapus (penting)

Seeder **hanya mengisi database yang masih kosong** (tabel `users` kosong).
Jika sudah ada user, seeder dilewati dan mencetak pesan di log:

```
[seed] Dilewati: database sudah berisi data.
[seed] Gunakan `python -m app.db.seed --force` (atau `make reseed`) untuk mengisi ulang dari nol.
```

Guard ini sengaja dibuat agar data yang sudah ada (termasuk record lampiran/
upload) **tidak pernah dihapus** oleh seeder otomatis. Untuk mengisi ulang
dari nol, jalankan `make reseed` secara eksplisit.

## Perintah (Docker)

| Perintah | Fungsi |
| --- | --- |
| `make build` | Build ulang service + seed menyatu setelah `up` |
| `make seed` | Isi data contoh (aman: hanya jika database kosong) |
| `make reseed` | Hapus SEMUA data lalu isi ulang dari nol (setara `--force`) |
| `make seed-check` | Periksa jumlah data & pola relasi hasil seed |
| `make up` / `make down` / `make logs` / `make ps` | Kelola service |

Setara dengan tanpa make (Docker):

```bash
docker compose --profile full up -d --build   # build + seed menyatu
docker exec mandalan-backend python -m app.db.seed         # seed
docker exec mandalan-backend python -m app.db.seed --force # reseed
docker exec mandalan-backend python -m app.db.seed --check # check
```

## Perintah (manual, tanpa Docker)

```bash
cd mandalan/backend
cp .env.example .env      # sesuaikan DATABASE_URL
python3.12 -m venv env && source env/bin/activate
pip install -r requirements.txt

python -m app.db.seed             # seed (hanya database kosong)
python -m app.db.seed --force     # reseed dari nol (hapus semua data dulu)
python -m app.db.seed --check     # verifikasi hasil seed
uvicorn app.main:app --reload --port 8000
```

## Migrasi skema (sebelum seed)

Migrasi kolom ringan (ALTER TABLE idempotent) dipisah ke
`backend/app/db/migrate.py` agar berjalan **sebelum seeder** di entrypoint
container (seeder butuh kolom seperti `signature`, `bank_account`, `phone2`,
dll). Migrasi juga tetap dijalankan dari lifespan FastAPI saat uvicorn start.

```bash
# Manual (Docker)
docker exec mandalan-backend python -m app.db.migrate

# Manual (tanpa Docker)
cd mandalan/backend && source env/bin/activate && python -m app.db.migrate
```

## Data yang di-seed

| Data | Jumlah | Detail |
| --- | --- | --- |
| User | 5 | admin, operations, marketing, finance, accounting (lihat `setup.md` untuk akun default) — punya `signature_caption` (penanda siapa) |
| Customer | 3 | PT. Bina Karya Sentosa, CV. Maju Jaya Abadi, PT. Sumber Rejeki Mandiri — punya `phone2` (telepon PIC) |
| Supplier | 2 | PT. Supplier Logistik Mandiri, CV. Bahan Bakar Utama — punya `phone2`, `bank_name`, `bank_account` |
| Offering Letter | 15 | status campuran `created`, `under_revision`, `po_received`; `paymentTerm` string (contoh "7 Hari"), `purchaseOrderDeadline` string (contoh "1 - 14"), field `pph` di sellingPrice |
| Purchase Order | 10 | 5 PO customer + 5 PO supplier; produk PO supplier berisi `ppkb`/`pph`/`ppn` |
| Delivery Order | 15 | terhubung ke PO customer, lengkap dengan `details` (catatan pengiriman, T2, dll.) |
| Invoice | 15 | status `unpaid`, `paid`, `overdue` |
| Notifikasi | 8 | info/warning/success/error ke berbagai role |
| Sales | 5 | status `paid`, `failed`, `refunded` |
| Accounting | 1 set | 21 akun (aset/kewajiban/ekuitas/pendapatan/beban) + 10 jurnal umum posted (termasuk pemasukan & pengeluaran) |

## Verifikasi hasil seed

### Otomatis (`make seed-check`)

```bash
make seed-check
```

Mengecek jumlah data per tabel dan pola relasi dokumen:

```
[seed] Jumlah data:
  [OK] users: 5 (diharapkan 5)
  [OK] customers: 3 (diharapkan 3)
  ...
[seed] Pola relasi dokumen:
  [OK] delivery_orders -> purchase_orders (15 DO terhubung ke PO)
  ...
[seed] SEMUA POLA VALID
```

Keluar dengan exit code 0 jika semua valid, 1 jika ada yang tidak valid.

### Manual via SQL

```bash
docker compose exec mandalan-db mysql -uroot -proot mandalan \
  -e "SELECT 'users' t, COUNT(*) n FROM users
      UNION ALL SELECT 'customers', COUNT(*) FROM customers
      UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
      UNION ALL SELECT 'offering_letters', COUNT(*) FROM offering_letters
      UNION ALL SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
      UNION ALL SELECT 'delivery_orders', COUNT(*) FROM delivery_orders
      UNION ALL SELECT 'invoices', COUNT(*) FROM invoices"
```

Hasil yang diharapkan: `5 / 3 / 2 / 15 / 10 / 15 / 15`.

### Cek via UI

1. Buka `http://localhost:8080`, login dengan salah satu akun default
   (mis. `admin@email.com` / `admin123`).
2. Halaman login menampilkan daftar akun demo lengkap dengan passwordnya
   (endpoint `/api/v1/profiles/demo`, lihat `demo-login.md`).
3. Cek halaman Marketing (Offering Letter/Purchase Order), Operations
   (Delivery Order + detail + cetak), Finance (Invoice), dan Accounting —
   semua terisi data contoh.

## Menjalankan ulang (reseed) — alternatif manual

`make reseed` (atau `python -m app.db.seed --force`) adalah cara yang
disarankan: menghapus semua data sesuai urutan FK-safe lalu mengisi ulang.

> ⚠️ **Peringatan**: reseed menghapus semua record upload (lampiran, signature,
> foto) dari sistem (file di disk tidak terhapus). Lakukan hanya di lingkungan
> dev/demo.

Bila ingin menghapus secara manual tanpa make (misalnya hanya tabel tertentu):

```bash
docker compose exec mandalan-db mysql -uroot -proot mandalan \
  -e "SET FOREIGN_KEY_CHECKS=0;
      DELETE FROM journal_lines; DELETE FROM journal_entries;
      DELETE FROM notifications; DELETE FROM invoices;
      DELETE FROM delivery_orders; DELETE FROM purchase_orders;
      DELETE FROM offering_letters; DELETE FROM sales;
      DELETE FROM accounts; DELETE FROM suppliers;
      DELETE FROM customers; DELETE FROM users;
      SET FOREIGN_KEY_CHECKS=1;"
docker compose restart backend   # seed otomatis terisi saat backend start
```

> Catatan: tabel `uploads` sengaja tidak dikosongkan di contoh di atas agar
> lampiran tidak hilang. Urutan hapus mengikuti `_CLEAR_ORDER` di
> `backend/app/db/seed.py` (child dulu, parent belakangan).

## Referensi

- `backend/app/db/seed.py` — script seeder (satu-satunya sumber kebenaran).
- `backend/app/db/migrate.py` — migrasi skema ringan (ALTER TABLE idempotent), dijalankan sebelum seed.
- `backend/app/main.py` — pemanggilan cadangan `seed_database` saat startup.
- `docker-compose.yml` — service `backend` menjalankan migrate + seed sebelum uvicorn.
- `Makefile` — target `build`/`seed`/`reseed`/`seed-check`.
- `documentation/setup.md` — cara menjalankan sistem secara keseluruhan.
- `documentation/demo-login.md` — detail akun demo & endpoint `/profiles/demo`.