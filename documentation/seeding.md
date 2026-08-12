# Seeder Database — Mitra Andalan Petroleum

## Apa itu seeder?

Seeder adalah script yang mengisi database dengan **data contoh (data demo)**:
user, customer, supplier, offering letter, purchase order, delivery order,
invoice, notifikasi, penjualan, dan data akuntansi (bagan akun + jurnal umum).

Lokasi: `backend/app/db/seed.py`

## Kapan seeder berjalan?

Seeder berjalan **otomatis setiap kali backend (FastAPI) dimulai** melalui
lifespan di `backend/app/main.py` (`seed_database`).

Namun ada **guard penting** (`backend/app/db/seed.py:29-36`):

> Seeder **hanya mengisi database yang masih kosong** (tabel `users` kosong).
> Jika sudah ada user di database, seeder dilewati — data yang ada **tidak
> pernah dihapus** oleh seeder.

Jadi restart backend berulang kali aman: tidak menghapus data yang sudah ada
(termasuk record lampiran/upload).

## Data yang di-seed

| Data | Jumlah | Detail |
| --- | --- | --- |
| User | 5 | admin, operations, marketing, finance, accounting (lihat `setup.md` untuk akun default) |
| Customer | 3 | PT. Bina Karya Sentosa, CV. Maju Jaya Abadi, PT. Sumber Rejeki Mandiri |
| Supplier | 2 | PT. Supplier Logistik Mandiri, CV. Bahan Bakar Utama |
| Offering Letter | 15 | status campuran `created`, `under_revision`, `po_received` |
| Purchase Order | 10 | 5 PO customer + 5 PO supplier, sebagian terhubung ke OL |
| Delivery Order | 15 | terhubung ke PO customer, lengkap dengan `details` (catatan pengiriman, T2, dll.) |
| Invoice | 15 | status `unpaid`, `paid`, `overdue` |
| Notifikasi | 8 | info/warning/success/error ke berbagai role |
| Sales | 5 | status `paid`, `failed`, `refunded` |
| Accounting | 1 set | 21 akun (aset/kewajiban/ekuitas/pendapatan/beban) + 6 jurnal umum posted |

## Menjalankan seeder (database kosong / pertama kali)

### Dengan Docker (recommended)

```bash
cd mandalan
docker compose --profile full up -d --build backend
```

Seeder otomatis terisi saat backend pertama kali dimulai (tabel dibuat oleh
`create_all` dulu, lalu di-seed). Cek log:

```bash
docker compose logs backend | grep -i seed
```

### Manual (backend tanpa Docker)

```bash
cd mandalan/backend
cp .env.example .env      # sesuaikan DATABASE_URL
python3.12 -m venv env && source env/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Seeder berjalan otomatis di awal saat uvicorn pertama kali menyala.

## Menjalankan ulang (reseed database yang sudah terisi)

Karena seeder hanya jalan di database kosong, untuk **menjalankan ulang**
database harus dikosongkan dulu — lalu restart backend.

> ⚠️ **Peringatan**: menghapus data mengakibatkan record upload (lampiran,
> signature, foto) ikut hilang dari sistem (file di disk tidak terhapus.
> Lakukan hanya di lingkungan dev/demo.

### Opsi A — hapus database lalu buat ulang (paling sederhana, Docker)

```bash
cd mandalan
docker compose exec mandalan-db mysql -uroot -proot \
  -e "DROP DATABASE mandalan; CREATE DATABASE mandalan"
docker compose up -d --build backend   # tabel dibuat ulang + seed otomatis
```

### Opsi B — hapus isi tabel secara FK-safe (tanpa drop database)

Urutan hapus mengikuti `_CLEAR_ORDER` di `backend/app/db/seed.py:22-26`
(child dulu, parent belakangan):

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
docker compose restart backend   # seed otomatis terisi
```

> Catatan: tabel `uploads` sengaja **tidak** dikosongkan di opsi B agar
> lampiran tidak hilang. Seeder menghapus record upload hanya saat mengisi
> database yang benar-benar kosong (lihat guard di atas).

### Manual (tanpa Docker)

```sql
-- via klien MySQL apa pun, sesuai DATABASE_URL lokal
SET FOREIGN_KEY_CHECKS=0;
DELETE FROM journal_lines; DELETE FROM journal_entries;
DELETE FROM notifications; DELETE FROM invoices;
DELETE FROM delivery_orders; DELETE FROM purchase_orders;
DELETE FROM offering_letters; DELETE FROM sales;
DELETE FROM accounts; DELETE FROM suppliers;
DELETE FROM customers; DELETE FROM users;
SET FOREIGN_KEY_CHECKS=1;
```

Lalu restart uvicorn agar seeder berjalan.

## Verifikasi hasil seed

### Cek jumlah data per tabel

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

## Referensi

- `backend/app/db/seed.py` — script seeder (satu-satunya sumber kebenaran).
- `backend/app/main.py` — pemanggilan otomatis `seed_database` saat startup.
- `documentation/setup.md` — cara menjalankan sistem secara keseluruhan.
- `documentation/demo-login.md` — detail akun demo & endpoint `/profiles/demo`.