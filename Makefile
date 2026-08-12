# Mitra Andalan Petroleum — Makefile

# Semua target memakai Docker Compose. Manual (tanpa Docker):
#   cd backend && source env/bin/activate
#   python -m app.db.seed [--force] [--check]

.PHONY: help up down build seed reseed seed-check logs ps

help: ## Tampilkan daftar perintah
	@echo "Target yang tersedia:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  %-12s %s\n", $$1, $$2}'

up: ## Jalankan semua service (db, backend, frontend)
	docker compose --profile full up -d

down: ## Hentikan semua service
	docker compose --profile full down

build: ## Build ulang service + seed otomatis menyatu setelah up
	docker compose --profile full up -d --build && $(MAKE) seed

seed: ## Isi database dengan data contoh (aman: hanya jika database kosong)
	docker exec mandalan-backend python -m app.db.seed

reseed: ## Hapus SEMUA data lalu isi ulang dari nol (menggunakan --force)
	docker exec mandalan-backend python -m app.db.seed --force

seed-check: ## Periksa jumlah data & pola relasi hasil seed
	docker exec mandalan-backend python -m app.db.seed --check

logs: ## Ikuti log semua service
	docker compose logs -f

ps: ## Status service
	docker compose ps
