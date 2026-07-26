# Mitra Andalan Petroleum

Sistem manajemen internal untuk perusahaan bahan bakar minyak.

## Tech Stack

- **Backend:** Python FastAPI + SQLAlchemy async + MySQL
- **Frontend:** Nuxt.js (Vue 3) + Nuxt UI
- **Containerization:** Docker + Docker Compose
- **API Dokumentasi:** Swagger UI (otomatis dari FastAPI)

## API Endpoints (27 routes)

| Modul | Endpoints | Keterangan |
|-------|-----------|------------|
| Health | `GET /health` | Cek status server |
| Auth | `POST /auth/login` | Login user |
| Customers | CRUD `/customers` | Data customer |
| Suppliers | CRUD `/suppliers` | Data supplier |
| Profiles | CRUD `/profiles` | Manajemen user |
| Offering Letters | CRUD `/offering-letters` | Surat penawaran (marketing) |
| Purchase Orders | CRUD `/purchase-orders` | PO customer/supplier |
| Delivery Orders | CRUD `/delivery-orders` | Delivery order (operational) |
| Invoices | CRUD `/invoices` | Invoice/penagihan (finance) |
| Sales | CRUD `/sales` | Data penjualan |
| Notifications | CRUD `/notifications` | Notifikasi sistem |
| Stats | GET `/stats/*` | Statistik dashboard |
| Uploads | CRUD `/upload`, `/uploads` | File upload (signature, dokumen) |

## Struktur Proyek

```
mandalan/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers
│   │   ├── core/               # Config, database
│   │   ├── db/                 # Seed data
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
├── docker-compose.yml
└── documentation/
    ├── setup.md                # Panduan instalasi
    └── api_setup.md            # Dokumentasi API lengkap + skenario upload
```

## Key Features

- **File Upload** — Multi-file upload (max 50MB), kaitkan ke dokumen via `document_type` + `document_id`, cascade delete otomatis
- **Notifikasi** — Field `to` untuk redirect path, `is_read` untuk status baca
- **Details JSON** — Setiap dokumen punya field `details` fleksibel untuk data form frontend
- **Relasi Upload** — OL, PO, DO, Invoice punya `uploads` one-to-many (nullable)

## Memulai Cepat

```bash
docker compose --profile full up -d
```

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Frontend | http://localhost:8080 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Uploaded Files | http://localhost:8000/media/... |

## Akun Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@email.com | admin123 |
| Marketing | marketing@email.com | marketing123 |
| Finance | finance@email.com | finance123 |
| Operations | ops@email.com | ops123 |
