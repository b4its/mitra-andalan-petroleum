# Setup — Mitra Andalan Petroleum

## Prasyarat

- Docker & Docker Compose
- Git

## Instalasi

```bash
git clone <repo-url> mandalan
cd mandalan
```

## Menjalankan Aplikasi

### Dengan Docker (produksi)

Menjalankan backend + frontend bersama MySQL:

```bash
docker compose --profile up -d
```

Hanya backend (untuk development frontend lokal):

```bash
docker compose --profile backend up -d
```

Hanya MySQL (untuk development backend lokal):

```bash
docker compose --profile backend up -d
```

### Tanpa Docker (development backend)

1. Pastikan MySQL sudah berjalan dan database `mandalan` sudah dibuat.
2. Atur environment variable di `backend/.env`:

```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/mandalan
```

3. Jalankan backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Tanpa Docker (development frontend)

```bash
cd frontend
pnpm install
pnpm dev
```

## Seed Data

Database akan otomatis diisi dengan data awal saat pertama kali backend dijalankan, termasuk:
- Akun admin default
- Contoh customers, suppliers, offering letters, purchase orders, delivery orders, invoices, sales, notifications

## Akun Login Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@email.com | admin123 |
| Operations | ops@email.com | ops123 |
| Marketing | marketing@email.com | marketing123 |
| Finance | finance@email.com | finance123 |

## Port

| Service | Port |
|---------|------|
| Backend (FastAPI) | 8000 |
| Frontend (Nuxt) | 3000 |
| MySQL | 3306 |
| Swagger UI | http://localhost:8000/docs |
