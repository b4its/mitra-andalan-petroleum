# Mitra Andalan Petroleum

Sistem manajemen internal untuk perusahaan bahan bakar minyak.

## Tech Stack

- **Backend:** Python FastAPI + SQLAlchemy async + MySQL
- **Frontend:** Nuxt.js (Vue 3) + Nuxt UI
- **Containerization:** Docker + Docker Compose
- **API Dokumentasi:** Swagger UI (otomatis dari FastAPI)

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
    ├── setup.md
    └── api_setup.md
```

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

## Akun Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@email.com | admin123 |
| Marketing | marketing@email.com | marketing123 |
| Finance | finance@email.com | finance123 |
| Operations | ops@email.com | ops123 |
