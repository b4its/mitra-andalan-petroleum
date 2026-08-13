# Mitra Andalan Petroleum

Sistem manajemen internal untuk perusahaan bahan bakar minyak.

## Tech Stack

- **Backend:** Python FastAPI + SQLAlchemy async + MySQL
- **Frontend:** Nuxt.js (Vue 3) + Nuxt UI
- **Containerization:** Docker + Docker Compose (boot otomatis: tunggu DB → migrasi → seed → uvicorn)
- **API Dokumentasi:** Swagger UI (otomatis dari FastAPI)

## Fitur Utama

- **Surat Penawaran (Marketing)** — PPH, metode pembayaran (Cash/Kredit), term & tenggat PO, tanda tangan QR/barcode
- **Purchase Order** — PO customer & supplier; PO supplier punya alur **rilis dana** oleh admin sebelum surat bisa dilihat; produk PO supplier berisi PPKB/PPH/PPN
- **Delivery Order (Operations)** — nomor DO otomatis (tahun/romawi/tanggal), catatan pengiriman, alur status (rilis dana, siap kirim, selesai, lunas ongkir), Surat PO Transportir
- **Invoice (Finance)** — tanpa sales order number, produk terhubung otomatis dari PO, "Dibuat Oleh" dari user login, tanpa barcode
- **Accounting** — buku besar seluruh akun, pemasukan/pengeluaran, neraca, kas harian, rekap monitoring (filter range tanggal)
- **Tanda Tangan User** — upload di profil/admin, caption (penanda siapa), tampil sebagai QR di dokumen marketing
- **Admin** — Data DO, Data PO Supplier (rilis dana), Manajemen pengguna (tanda tangan), Database export/import

## Memulai Cepat (Docker)

```bash
cd mandalan
make doctor        # (opsional) cek make, docker, docker compose plugin
make build         # build + boot (migrasi & seed otomatis) — sekali, langsung jalan
```

Setara tanpa make:

```bash
docker compose --profile full up -d --build
```

`make build` / `make up` menunggu backend sehat sebelum seed, aman untuk
first-run di database kosong. Pengembangan dengan Dev Container (VS Code):
`.devcontainer/` menyediakan image Ubuntu + make + Docker-in-Docker + Python + Node.

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Frontend | http://localhost:8080 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Uploaded Files | http://localhost:8000/media/... |

## Struktur Proyek

```
mandalan/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   ├── core/               # Config, database
│   │   ├── db/                 # boot.py, migrate.py, seed.py, session.py
│   │   ├── models/             # SQLAlchemy models
│   │   └── schemas/            # Pydantic request/response schemas
│   ├── media/                  # Uploaded files (signatures, documents, returned)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── pages/                  # Nuxt pages per role
│   ├── components/             # UI components
│   ├── types/                  # TypeScript interfaces & Zod schemas
│   ├── Dockerfile
│   └── nuxt.config.ts
├── .devcontainer/              # Dev Container (OS + make + tools)
├── .gitattributes              # Normalisasi LF (cegah CRLF di .sh/.py/dll)
├── Makefile                    # doctor/build/up/seed/reseed/seed-check/logs/ps
├── docker-compose.yml
└── documentation/
    ├── setup.md                # Panduan instalasi
    ├── api_setup.md            # Dokumentasi API lengkap + skenario upload
    ├── seeding.md              # Panduan seeder & migrasi
    └── testing.md              # Panduan testing (pytest, vitest, Playwright)
```

## API Endpoints

59 routes, dikelompokkan: health, auth, customers, suppliers, profiles,
offering-letters (termasuk `/offering-letters/{id}/purchase-orders`),
purchase-orders (termasuk `/{id}/rilis-dana`), delivery-orders, invoices,
sales, notifications, stats, uploads, accounting (termasuk `/ledger-all`,
`/monitoring` dengan range tanggal), admin-database.
Detail lengkap di `documentation/api_setup.md` dan Swagger UI `/docs`.

## Testing

| Layer | Tool | Command | Count |
|---|---|---|---|
| Backend | pytest | `docker exec mandalan-backend python -m pytest tests/ -v` | 164 |
| Frontend (headless) | Vitest | `cd frontend && npx vitest run` | 47 |
| Frontend (browser/E2E) | Playwright | `cd frontend && pnpm exec playwright test` | 76 |

E2E Playwright menguji aplikasi via Chromium pada `localhost:8080` (Docker)
atau `localhost:3000` (dev): login per role, dashboard admin, halaman
marketing/operations/finance/accounting, ekspor Excel/PDF/CSV, dan audit
console error. Lihat `documentation/testing.md` untuk detail dan tips
anti-flaky (login wajib `waitUntil: "networkidle"`).

## Akun Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@email.com | admin123 |
| Marketing | marketing@email.com | marketing123 |
| Finance | finance@email.com | finance123 |
| Operations | ops@email.com | ops123 |
| Accounting | accounting@email.com | accounting123 |
