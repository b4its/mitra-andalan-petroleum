# Mitra Andalan Petroleum — Build & Run System
# =============================================
# Semua target memakai Docker Compose (container_name sudah fixed).
# `make build` / `make up` sudah menangani migrasi + seed otomatis
# (entrypoint container), jadi pertama kali langsung bisa dipakai.
#
# ────────────────────────────────────────────────────────────────────────
# 🚀 APLIKASI DAPAT DIAKSES DI:
# ────────────────────────────────────────────────────────────────────────
#
# 📌 PRODUCTION (Live Deployment):
#    URL Utama: https://mandalan.mapetroleum.co.id
#    SSL: Let's Encrypt certificate aktif
#    Akses via domain ini untuk semua halaman dan API
#
# 🐛 LOCAL HOSTING (Development):
#    Frontend UI:     http://localhost:8092
#    Backend API:     http://localhost:8012
#    Database MySQL:  localhost:3318
#    Port Nginx:      localhost:92 (reverse proxy ke frontend)
#
# ────────────────────────────────────────────────────────────────────────
# 📋 PORT MAPPING (Host → Container):
# ────────────────────────────────────────────────────────────────────────
#   DB        3318:3318 (MySQL)
#   Backend   8012:8012 (FastAPI)
#   Frontend  8092:3012 (Nuxt SSR + HMR fallback 24678)
#   Nginx     92:80 (Reverse Proxy)
#   Vite HMR  24678:24678 (Internal, hardcoded di @nuxt/vite-builder)
#
# ────────────────────────────────────────────────────────────────────────
# 🌐 PAGES ACCESS (Production URL: https://mandalan.mapetroleum.co.id):
# ────────────────────────────────────────────────────────────────────────
#   Login:            https://mandalan.mapetroleum.co.id/login
#   Admin Dashboard:  https://mandalan.mapetroleum.co.id/admin
#   Accounting:       https://mandalan.mapetroleum.co.id/accounting
#   Marketing:        https://mandalan.mapetroleum.co.id/marketing
#   Operations:       https://mandalan.mapetroleum.co.id/operations
#   Finance:          https://mandalan.mapetroleum.co.id/finance
#   Supplier PO:      https://mandalan.mapetroleum.co.id/marketing/supplier/po
#   Customer OL:      https://mandalan.mapetroleum.co.id/marketing/ol
#   Invoice:          https://mandalan.mapetroleum.co.id/finance/invoice
#
# 🔐 DEMO CREDENTIALS:
# ────────────────────────────────────────────────────────────────────────
#   Role         Email                              Password
#   Admin        admin@mapetroleum.co.id            admin123
#   Marketing    marketing@mapetroleum.co.id        marketing123
#   Operations   ops@mapetroleum.co.id              ops123
#   Finance      finance@mapetroleum.co.id          finance123
#   Accounting   accounting@mapetroleum.co.id       accounting123
#
# ────────────────────────────────────────────────────────────────────────
# 💾 DATABASE CONNECTION INFO:
# ────────────────────────────────────────────────────────────────────────
#   Host:       localhost:3318 (via nginx) atau 127.0.0.1:3318
#   Database:   mandalan
#   User:       root
#   Password:   example123
#   SSL Mode:   DISABLED (development only)
#
# ────────────────────────────────────────────────────────────────────────
# Manual (tanpa Docker):
#   cd backend && source env/bin/activate
#   python -m app.db.seed [--force] [--check]
#   uvicorn app.main:app --host 0.0.0.0 --port 8012

.PHONY: help doctor up down build seed reseed seed-check logs ps clean restart db mysql-shell sql-cli

help: ## Tampilkan daftar perintah dan informasi akses aplikasi
	@echo "Mitra Andalan Petroleum — Build & Run System"
	@echo ""
	@echo "🌐 APLIKASI DAPAT DIAKSES:"
	@echo "   Production URL:  https://mandalan.mapetroleum.co.id"
	@echo "   Local Host:      http://localhost:8092"
	@echo ""
	@echo "💾 DATABASE:"
	@echo "   localhost:3318 | User: root | Pass: example123 | DB: mandalan"
	@echo ""
	@echo "📋 PERINTAH YANG TERSEDIA:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  %-15s %s\n", $$1, $$2}'

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

db: ## Akses MySQL database (docker exec atau mysql CLI lokal)
	@echo "Akses Database Mandalan"
	@echo "======================="
	@echo ""
	@echo "💾 Database Connection Info:"
	@echo "   Host:     localhost:3318"
	@echo "   Database: mandalan"
	@echo "   User:     root"
	@echo "   Password: example123"
	@echo ""
	@echo "🔧 Cara 1: Docker exec shell interaktif (direkomendasikan):"
	@echo "   make db-shell"
	@echo ""
	@echo "🔧 Cara 2: MySQL CLI lokal:"
	@echo "   mysql -h 127.0.0.1 -P 3318 -u root -pexample123 mandalan"
	@echo ""
	@echo "🔧 Cara 3: Jalankan query sekali saja tanpa shell:"
	@echo "   make sql-cli"
	@echo ""
	@echo "📌 Contoh query SQL untuk cek data:"
	@echo "   SELECT COUNT(*) FROM users WHERE role = 'admin';"
	@echo "   SELECT * FROM customers LIMIT 5;"
	@echo "   SELECT do_number, status FROM delivery_orders ORDER BY created_at DESC LIMIT 10;"

db-shell: ## Masuk ke MySQL shell via docker exec
	docker exec -it mandalan-db mysql -uroot -pexample123 mandalan

mysql-shell: ## Alias untuk db-shell
	$(MAKE) db-shell

sql-cli: ## Jalankan MySQL shell sekali saja (tanpa -it)
	docker exec mandalan-db mysql -uroot -pexample123 mandalan -e "SELECT version();"

clean: ## Hapus containers dan volumes
	docker compose --profile full down --volumes --remove-orphans

restart: ## Restart semua containers
	docker compose --profile full restart

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
