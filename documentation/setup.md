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
docker compose --profile full up -d
```

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
(lihat `backend/app/db/seed.py`):

- 5 user (admin, marketing, finance, operations, accounting)
- 3 customer, 2 supplier
- 15 offering letters, 10 purchase orders
- 15 delivery orders, 15 invoices
- 5 sales, 8 notifications, akun + jurnal akuntansi

Panduan lengkap menjalankan seeder (fresh install, reseed database yang sudah
terisi, dan verifikasi) ada di [seeding.md](seeding.md).

## Akun Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@email.com | admin123 |
| Marketing | marketing@email.com | marketing123 |
| Finance | finance@email.com | finance123 |
| Operations | ops@email.com | ops123 |
| Accounting | accounting@email.com | accounting123 |

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
