# Setup — Mitra Andalan Petroleum

## Prasyarat

- Docker & Docker Compose (recommended)
- Python 3.12 (manual backend)
- Node.js 22 + pnpm (manual frontend)
- MySQL 8.0 (manual backend)
- Chromium (untuk E2E Playwright, contoh Arch: `sudo pacman -S chromium`)

## Instalasi & Menjalankan

### Dengan Docker (recommended)

```bash
cd mandalan
make doctor        # (opsional) cek make, docker, docker compose plugin
make build         # build + boot (migrasi & seed otomatis) — cukup sekali, langsung jalan
```

Setara dengan tanpa make:

```bash
docker compose --profile full up -d --build
```

`make build` / `make up` secara otomatis **menunggu backend sehat** sebelum
seed, sehingga aman dijalankan pertama kali (bahkan di database kosong).

> 💡 Pengembangan memakai **Dev Container** (VS Code): `.devcontainer/`
> menyediakan image Ubuntu + `make`, Docker-in-Docker, Python 3.12, Node 22 —
> semua tool yang dibutuhkan sudah termasuk.

Service akan berjalan di:

| Service | Port |
|---------|------|
| Backend (FastAPI) | 8000 |
| Frontend (Nuxt) | 8080 |
| MySQL | 3306 |
| Swagger UI | http://localhost:8000/docs |
| Uploaded Files | http://localhost:8000/media/... |

### Hanya backend + DB (untuk development frontend lokal)

```bash
docker compose --profile core up -d
```

### Manual (backend)

```bash
cd mandalan/backend
cp .env.example .env   # edit DATABASE_URL sesuai lokal
python3.12 -m venv env
source env/bin/activate
pip install -r requirements.txt
python -m app.db.migrate   # (opsional) migrasi skema
python -m app.db.seed      # (opsional) isi data contoh
uvicorn app.main:app --reload --port 8000
```

### Manual (frontend)

```bash
cd mandalan/frontend
pnpm install
pnpm dev
```

## Environment Variables

### Backend (`backend/.env`)

```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/mandalan
```

### Frontend (`frontend/.env`)

```env
NUXT_PUBLIC_SITE_URL=
```

## Seed Data

Database otomatis terisi data awal saat pertama kali backend dijalankan
(lihat `backend/app/db/seed.py`, `backend/app/db/migrate.py`, dan
`backend/app/db/boot.py`):

- 5 user (admin, marketing, finance, operations, accounting) — dengan caption & file tanda tangan
- 3 customer (termasuk telepon PIC), 2 supplier (termasuk bank & no. rekening)
- 15 offering letters (PPH, metode & term pembayaran, tenggat PO), 10 purchase orders (PO supplier berisi PPKB/PPH/PPN, sebagian sudah rilis dana)
- 15 delivery orders, 15 invoices
- 5 sales, 8 notifications, akun + jurnal akuntansi

Alur saat container start: **boot** (`python -m app.db.boot`) menunggu
database siap → **migrasi skema** (`python -m app.db.migrate`, kolom baru:
signature, bank_account, phone2, rilis_dana_at, dll.) → **seeder**
(`python -m app.db.seed`).

Panduan lengkap menjalankan seeder (fresh install, reseed database yang sudah
terisi, dan verifikasi) ada di [seeding.md](seeding.md).

## Akun Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@mapetroleum.co.id | admin123 |
| Marketing | marketing@mapetroleum.co.id | marketing123 |
| Finance | finance@mapetroleum.co.id | finance123 |
| Operations | ops@mapetroleum.co.id | ops123 |
| Accounting | accounting@mapetroleum.co.id | accounting123 |

## Testing

Panduan lengkap ada di `testing.md`. Ringkasan perintah:

```bash
# Backend (dari dalam container)
docker compose exec mandalan-backend python -m pytest tests/ -v

# Frontend unit (dari host, folder frontend)
cd frontend && npx vitest run

# E2E Playwright (frontend + backend harus berjalan, lalu)
cd frontend && pnpm exec playwright test
```
