# Mitra Andalan Petroleum — Makefile
#
# Semua target memakai Docker Compose (container_name sudah fixed).
# `make build` / `make up` sudah menangani migrasi + seeder otomatis
# (entrypoint container), jadi pertama kali langsung bisa dipakai.
#
# Manual (tanpa Docker):
#   cd backend && source env/bin/activate
#   python -m app.db.seed [--force] [--check]

.PHONY: help doctor up down build seed reseed seed-check logs ps

help: ## Tampilkan daftar perintah
	@echo "Target yang tersedia:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  %-12s %s\n", $$1, $$2}'

doctor: ## Periksa prasyarat (make, docker, docker compose plugin)
	@echo "Memeriksa prasyarat..."
	@command -v make >/dev/null 2>&1 || { echo "ERROR: 'make' tidak terpasang. Install dulu (Linux: sudo apt install make / macOS: xcode-select --install)."; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "ERROR: 'docker' tidak terpasang."; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo "ERROR: plugin 'docker compose' (v2) tidak tersedia."; exit 1; }
	@echo "Semua prasyarat OK."

up: ## Jalankan semua service (db, backend, frontend) — seed otomatis
	docker compose --profile full up -d
	@$(MAKE) _wait-backend

down: ## Hentikan semua service
	docker compose --profile full down

build: ## Build ulang service + migrasi & seed otomatis (tunggu backend sehat)
	docker compose --profile full up -d --build
	@$(MAKE) _wait-backend
	@$(MAKE) seed

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

_wait-backend: ## (internal) Tunggu sampai backend sehat
	@echo "Menunggu backend sehat..."
	@i=0; until [ $$i -ge 90 ]; do \
	  status=$$(docker inspect -f '{{.State.Health.Status}}' mandalan-backend 2>/dev/null || echo starting); \
	  if [ "$$status" = "healthy" ]; then echo "Backend sehat."; exit 0; fi; \
	  sleep 2; i=$$((i+1)); \
	done; \
	echo "ERROR: backend tidak sehat dalam 180 detik. Log backend:"; \
	docker logs mandalan-backend --tail 50; \
	exit 1
