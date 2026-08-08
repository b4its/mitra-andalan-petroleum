# ============================================================================
#  Mitra Andalan Petroleum — Makefile
#  Jalankan semua perintah project tanpa harus hafal command Docker/Compose.
#  Cukup:  make <target>
#
#  Lihat semua perintah:  make help   (atau cukup  make)
# ============================================================================

SHELL := /bin/bash

# ── Konfigurasi Compose ─────────────────────────────────────────────────────
COMPOSE         := docker compose
COMPOSE_DEV     := docker compose -f docker-compose.yml -f docker-compose.local.yml
PROFILE_FULL    := --profile full
PROFILE_CORE    := --profile core

# Port & container name (sesuaikan bila berubah di compose)
BACKEND_PORT    ?= 8000
FRONTEND_PORT   ?= 8080
DB_PORT         ?= 3306

BACKEND_SVC     := mandalan-backend
FRONTEND_SVC    := mandalan-frontend
DB_SVC          := mandalan-db

# ── Warna untuk output ──────────────────────────────────────────────────────
C_RESET := \033[0m
C_BOLD  := \033[1m
C_CYAN  := \033[36m
C_GREEN := \033[32m
C_RED   := \033[31m
C_YEL   := \033[33m

# ============================================================================
#  HELP (target default)
# ============================================================================
.PHONY: help
help: ## Tampilkan semua perintah yang tersedia
	@echo -e ""
	@echo -e "$(C_BOLD)$(C_CYAN)Mitra Andalan Petroleum — Makefile$(C_RESET)"
	@echo -e "$(C_CYAN)==========================================$(C_RESET)"
	@echo -e ""
	@grep -E '^[a-zA-Z_./-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(C_GREEN)%-24s$(C_RESET) %s\n", $$1, $$2}'
	@echo -e ""
	@echo -e "Contoh: $(C_BOLD)make full-up$(C_RESET)  — jalankan semua service"

# ============================================================================
#  FULL STACK — db + backend + frontend (mode development / hot-reload)
# ============================================================================
.PHONY: full-up
full-up: ## Build + jalankan semua service (db, backend, frontend) — mode dev
	$(COMPOSE_DEV) $(PROFILE_FULL) up -d --build
	@$(MAKE) --no-print-directory status

.PHONY: full-up-local
full-up-local: ## Jalankan semua service tanpa build (mode dev, volume mount aktif)
	$(COMPOSE_DEV) $(PROFILE_FULL) up -d
	@$(MAKE) --no-print-directory status

.PHONY: full-up-prod
full-up-prod: ## Build + jalankan semua service tanpa volume mount (mode production)
	$(COMPOSE) $(PROFILE_FULL) up -d --build
	@$(MAKE) --no-print-directory status

.PHONY: full-build
full-build: ## Build image semua service (tanpa start)
	$(COMPOSE_DEV) $(PROFILE_FULL) build

.PHONY: full-build-frontend
full-build-frontend: ## Build + restart hanya frontend
	$(COMPOSE_DEV) $(PROFILE_FULL) up -d --build frontend

.PHONY: full-build-backend
full-build-backend: ## Build + restart hanya backend
	$(COMPOSE_DEV) $(PROFILE_FULL) up -d --build backend

.PHONY: full-down
full-down: ## Stop semua service
	$(COMPOSE) down

.PHONY: full-restart
full-restart: ## Restart semua service
	$(COMPOSE) restart

.PHONY: full-logs
full-logs: ## Ikuti log semua service (Ctrl+C untuk keluar)
	$(COMPOSE) logs -f --tail=100

.PHONY: full-ps
full-ps: status

.PHONY: status
status: ## Status semua service
	@echo -e "$(C_BOLD)Status service:$(C_RESET)"
	@$(COMPOSE) ps

# ============================================================================
#  CORE — db + backend saja (untuk development frontend lokal)
# ============================================================================
.PHONY: core-up
core-up: ## Build + jalankan hanya db dan backend
	$(COMPOSE_DEV) $(PROFILE_CORE) up -d --build

.PHONY: core-up-local
core-up-local: ## Jalankan hanya db dan backend (tanpa build)
	$(COMPOSE_DEV) $(PROFILE_CORE) up -d

.PHONY: core-build
core-build: ## Build image db dan backend
	$(COMPOSE_DEV) $(PROFILE_CORE) build

.PHONY: core-down
core-down: ## Stop db dan backend
	$(COMPOSE) stop db backend

.PHONY: core-logs
core-logs: ## Ikuti log db dan backend
	$(COMPOSE) logs -f --tail=100 db backend

.PHONY: core-restart
core-restart: ## Restart db dan backend
	$(COMPOSE) restart db backend

# ============================================================================
#  LOGS per service
# ============================================================================
.PHONY: logs-backend
logs-backend: ## Log backend (ikuti, Ctrl+C untuk keluar)
	$(COMPOSE) logs -f --tail=100 backend

.PHONY: logs-frontend
logs-frontend: ## Log frontend (ikuti, Ctrl+C untuk keluar)
	$(COMPOSE) logs -f --tail=100 frontend

.PHONY: logs-db
logs-db: ## Log database MySQL
	$(COMPOSE) logs -f --tail=100 db

# ============================================================================
#  SHELL / akses ke dalam container
# ============================================================================
.PHONY: shell-backend
shell-backend: ## Masuk ke shell backend
	$(COMPOSE) exec $(BACKEND_SVC) bash

.PHONY: shell-frontend
shell-frontend: ## Masuk ke shell frontend
	$(COMPOSE) exec $(FRONTEND_SVC) sh

.PHONY: shell-db
shell-db: ## Masuk ke shell MySQL (mysql client)
	$(COMPOSE) exec $(DB_SVC) mysql -umandalan -pmandalan mandalan

# ============================================================================
#  TESTING
# ============================================================================
.PHONY: test
test: test-backend test-frontend ## Jalankan semua test (backend + frontend vitest)

.PHONY: test-backend
test-backend: ## Jalankan test backend (pytest) di dalam container
	$(COMPOSE) exec $(BACKEND_SVC) python -m pytest tests/ -v

.PHONY: test-backend-coverage
test-backend-coverage: ## Test backend dengan coverage
	$(COMPOSE) exec $(BACKEND_SVC) python -m pytest tests/ -v --cov=app --cov-report=term-missing

.PHONY: test-frontend
test-frontend: ## Jalankan test frontend (vitest) — perlu backend berjalan
	cd frontend && COREPACK_ENABLE_STRICT=0 npx vitest run

.PHONY: test-e2e
test-e2e: ## Jalankan E2E Playwright — butuh full stack berjalan di port 8080
	cd frontend && PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium COREPACK_ENABLE_STRICT=0 npx playwright test

.PHONY: test-e2e-local
test-e2e-local: ## E2E Playwright ke server lokal (port 3000)
	cd frontend && NUXT_API_PROXY_TARGET=http://127.0.0.1:8004/api/v1 pnpm exec playwright test --config=playwright.local.ts

.PHONY: lint
lint: ## Lint frontend (eslint)
	cd frontend && pnpm lint

.PHONY: typecheck
typecheck: ## Typecheck frontend (vue-tsc / nuxt)
	cd frontend && pnpm typecheck

# ============================================================================
#  DEVELOPMENT — DIJALANKAN VIA DOCKER (wajib)
#  Untuk development lokal, gunakan docker compose dengan local override
#  yang sudah menyediakan hot-reload (volume mount).
# ============================================================================
.PHONY: dev-backend
dev-backend: ## [Docker] Jalankan backend + DB dengan hot-reload (mode local)
	$(COMPOSE_DEV) $(PROFILE_CORE) up -d --build
	@echo -e "$(C_GREEN)Backend siap di http://localhost:$(BACKEND_PORT)$(C_RESET)"
	@echo -e "$(C_GREEN)Swagger: http://localhost:$(BACKEND_PORT)/docs$(C_RESET)"
	$(COMPOSE_DEV) logs -f backend

.PHONY: dev-frontend
dev-frontend: ## [Docker] Jalankan semua service (full stack) dengan hot-reload
	$(COMPOSE_DEV) $(PROFILE_FULL) up -d --build
	@echo -e "$(C_GREEN)Frontend siap di http://localhost:$(FRONTEND_PORT)$(C_RESET)"
	@echo -e "$(C_GREEN)Backend API di http://localhost:$(BACKEND_PORT)$(C_RESET)"
	$(COMPOSE_DEV) logs -f frontend

.PHONY: dev-logs-backend
dev-logs-backend: ## Ikuti log backend (hot-reload mode)
	$(COMPOSE_DEV) logs -f --tail=50 backend

.PHONY: dev-logs-frontend
dev-logs-frontend: ## Ikuti log frontend (hot-reload mode)
	$(COMPOSE_DEV) logs -f --tail=50 frontend

.PHONY: install
install: ## Install dependency backend & frontend
	cd backend && python3 -m venv env && source env/bin/activate && pip install -r requirements.txt
	cd frontend && pnpm install

# ============================================================================
#  MAINTENANCE / DATABASE
# ============================================================================
.PHONY: db-reset
db-reset: ## Hapus volume DB + start ulang + reseed otomatis (HAPUS SEMUA DATA!)
	$(COMPOSE) down -v
	@echo -e "$(C_YEL)Volume database dihapus. Menjalankan ulang...$(C_RESET)"
	$(MAKE) --no-print-directory full-up

.PHONY: clean
clean: ## Stop semua service + hapus volume (HAPUS SEMUA DATA!)
	$(COMPOSE) down -v --remove-orphans
	@echo -e "$(C_RED)Semua container & volume dihapus.$(C_RESET)"

.PHONY: prune
prune: ## Bersihkan image docker yang tidak terpakai
	docker system prune -f

# ============================================================================
#  INFORMASI / DIAGNOSA
# ============================================================================
.PHONY: info
info: ## Tampilkan URL akses service
	@echo -e "$(C_BOLD)URL Service:$(C_RESET)"
	@echo -e "  Backend API   → http://localhost:$(BACKEND_PORT)"
	@echo -e "  Swagger UI    → http://localhost:$(BACKEND_PORT)/docs"
	@echo -e "  ReDoc         → http://localhost:$(BACKEND_PORT)/redoc"
	@echo -e "  Frontend      → http://localhost:$(FRONTEND_PORT)"
	@echo -e "  Database      → localhost:$(DB_PORT) (user: mandalan / pass: mandalan)"
	@echo -e ""
	@echo -e "$(C_BOLD)Akun Default:$(C_RESET)"
	@echo -e "  Admin      → admin@email.com      / admin123"
	@echo -e "  Marketing  → marketing@email.com  / marketing123"
	@echo -e "  Finance    → finance@email.com    / finance123"
	@echo -e "  Operations → ops@email.com        / ops123"
	@echo -e "  Accounting → accounting@email.com / accounting123"

.PHONY: doctor
doctor: ## Cek prasyarat (docker, node, pnpm, python)
	@echo -e "$(C_BOLD)Memeriksa prasyarat...$(C_RESET)"
	@command -v docker  >/dev/null 2>&1 && echo -e "  $(C_GREEN)✔ docker$(C_RESET)"          || echo -e "  $(C_RED)✘ docker tidak ditemukan$(C_RESET)"
	@command -v docker-compose >/dev/null 2>&1 && echo -e "  $(C_GREEN)✔ docker-compose$(C_RESET)" || echo -e "  $(C_YEL)• docker-compose (plugin compose sudah termasuk)$(C_RESET)"
	@command -v node    >/dev/null 2>&1 && echo -e "  $(C_GREEN)✔ node $$(node -v)$(C_RESET)"      || echo -e "  $(C_RED)✘ node tidak ditemukan$(C_RESET)"
	@command -v pnpm    >/dev/null 2>&1 && echo -e "  $(C_GREEN)✔ pnpm $$(pnpm -v)$(C_RESET)"      || echo -e "  $(C_RED)✘ pnpm tidak ditemukan$(C_RESET)"
	@command -v python3 >/dev/null 2>&1 && echo -e "  $(C_GREEN)✔ python3 $$(python3 --version | cut -d' ' -f2)$(C_RESET)" || echo -e "  $(C_RED)✘ python3 tidak ditemukan$(C_RESET)"
