# Mitra Andalan Petroleum

Sistem manajemen internal untuk perusahaan bahan bakar minyak.

## Tech Stack

- **Backend:** Python FastAPI + SQLAlchemy (async) + MySQL
- **Frontend:** Nuxt.js (Vue 3) + Nuxt UI
- **Containerization:** Docker + Docker Compose
- **Dokumentasi API:** Swagger UI (otomatis dari FastAPI)

## Struktur Proyek

```
mandalan/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes (v1)
│   │   ├── core/      # Konfigurasi, database
│   │   ├── db/        # Seed data
│   │   ├── models/    # SQLAlchemy models
│   │   └── schemas/   # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/          # Nuxt.js frontend
│   ├── pages/         # Halaman aplikasi
│   ├── components/    # UI components
│   ├── Dockerfile
│   └── nuxt.config.ts
├── docker-compose.yml
└── documentation/
    ├── setup.md       # Panduan instalasi & setup
    └── api_setup.md   # Dokumentasi API
```

## Memulai Cepat

```bash
docker compose --profile full up -d
```

Backend: http://localhost:8000
Frontend: http://localhost:3000
Swagger UI: http://localhost:8000/docs

Lihat [documentation/setup.md](documentation/setup.md) untuk panduan lengkap.
