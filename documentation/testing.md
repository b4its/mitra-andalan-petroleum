# Mandalan Testing Guide

## Backend

### Dependencies
```bash
pip install -r dev-requirements.txt
```

### Running tests
```bash
# Run all tests from inside the backend container:
docker compose exec mandalan-backend python -m pytest tests/ -v

# With coverage:
docker compose exec mandalan-backend python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test file:
docker compose exec mandalan-backend python -m pytest tests/test_auth.py -v
```

**95 tests** covering auth, customers, delivery orders, invoices, notifications,
offering letters, profiles, purchase orders, stats, and suppliers.

---

## Frontend — Headless (Vitest)

Unit + API contract tests using `vitest` + `happy-dom`.

### Running tests (from host)
```bash
cd frontend
COREPACK_ENABLE_STRICT=0 npx vitest run
```

### Running tests (from inside container)
```bash
docker compose exec mandalan-frontend sh -c 'cd /app && npx vitest run --exclude "**/api.test.ts"'
```

> API contract tests (`api.test.ts`) connect to `localhost:8000` and need the
> backend running. Run them **from the host** where the port is exposed, or
> exclude them inside the container.

**53 tests** — utility functions (formatCurrency, formatDate, formatPercent,
randomInt, randomFrom), Zod schemas (addCustomer, profile, password,
marketingOLHeader), dummy account integrity, and 22 API contract tests (auth,
CRUD, pagination, CORS).

---

## Frontend — Browser (Playwright)

E2E tests menggunakan Playwright + Chromium (system browser).

### Prerequisites
- Frontend berjalan di `http://localhost:8080` (via Docker) atau `http://localhost:3000` (dev lokal)
- Backend berjalan di `http://localhost:8000`
- Chromium terinstall di host (Arch: `sudo pacman -S chromium`)

### Running tests (from host)
```bash
cd frontend
COREPACK_ENABLE_STRICT=0 pnpm exec playwright test
```

Konfigurasi dual:
- `playwright.config.ts` — baseURL `http://localhost:8080` (server Docker)
- `playwright.local.ts` — baseURL `http://localhost:3000` (Nuxt dev server)
- Jalankan dengan config lokal: `pnpm exec playwright test --config=playwright.local.ts`
- Jika Chromium tidak terdeteksi otomatis:
  `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium pnpm exec playwright test`

### Tips (penting agar test tidak flaky)
- **Semua `page.goto('/login')` harus pakai `{ waitUntil: 'networkidle' }`** —
  tanpa itu Vue belum selesai hydration dan submit login tidak terpanggil.
- Tests berjalan serial (`fullyParallel: false`); `--workers=1` direkomendasikan
  untuk menghindari resource contention.
- Login state dikelola per-test via localStorage — tidak ada shared cookies.
- **Robust login helper**: setelah `networkidle`, helper menunggu tombol submit
  enabled lalu melakukan **retry maksimal 3x** (isi ulang field + submit) bila
  URL belum berubah. Ini mengatasi race hydration Vue: field bisa tereset
  (state kosong → error "expected string, received undefined") jika submit
  pertama terjadi sebelum hydration selesai.
- Pengecekan body-visibility menunggu `waitUntil: "networkidle"` dan menargetkan
  elemen heading spesifik, bukan `<body>` (Nuxt menyembunyikan body saat hydration).
- Error login divalidasi dengan `getByText("Login Gagal", { exact: true })`
  (message API berbahasa Indonesia), bukan "Login failed".
- Console-error audit memfilter pesan benign: `favicon`, `Hydration completed
  but contains mismatches` (warning hydration Nuxt/Vue), Vue Devtools, dan
  experimental feature — jangan hapus filter ini tanpa alasan.

### Cakupan test (71 tests)
| File | Jumlah | Coverage |
|---|---|---|
| `login.spec.ts` | 9 | form login, redirect per role, error password/email, route guard, logout |
| `dashboard.spec.ts` | 18 | stat cards, sidebar, navigasi subpage, modal detail metrik, date range preset, page loads per role |
| `pages.spec.ts` | 15 | page rendering per modul, responsive mobile, console error audit per role |
| `accounting.spec.ts` | 7 | summary cards, chart of accounts, jurnal, buku besar, pemasukan/pengeluaran, console audit |
| `admin-accounting.spec.ts` | 5 | rekap page, jurnal & trial balance, search filter, export dropdown, download .xlsx |
| `export.spec.ts` | 9 | dropdown export 3 format di tiap halaman, download Excel/PDF/CSV |
| `admin-customers.spec.ts` | 3 | kolom NPWP, validasi format NPWP (warning), tambah customer dengan NPWP valid |
| `admin-database.spec.ts` | 5 | render kartu database, export SQL + download .sql, validasi tombol import/clear, import SQL |

**Total: 71 tests.** Jalankan full suite:
```bash
cd frontend
timeout 900 pnpm exec playwright test --reporter=line --workers=1
```

---

## Quick Reference

| Layer | Command | Count |
|---|---|---|
| Backend | `pytest tests/ -v` | 95 |
| Frontend (headless) | `npx vitest run` | 53 |
| Frontend (browser) | `pnpm exec playwright test` | 71 |
