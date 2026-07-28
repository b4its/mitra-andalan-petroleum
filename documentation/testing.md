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

E2E tests using Playwright + system Chromium.

### Prerequisites
- Frontend server running at `http://localhost:8080`
- Chromium installed on host (Arch: `sudo pacman -S chromium`)

### Running tests (from host)
```bash
cd frontend
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium COREPACK_ENABLE_STRICT=0 npx playwright test
```

### Tips
- Tests run serially (`fullyParallel: false`). Single-worker execution avoids
  resource contention and stale session state.
- Login state is managed per-test via localStorage — no shared cookies.
- Body-visibility checks wait for `waitUntil: "networkidle"` and target
  specific heading elements rather than `<body>` (which Nuxt may keep hidden
  during hydration/transitions).
- Error notifications are validated with `getByText("Login failed", { exact: true })`
  to avoid strict-mode ambiguity with the toast container element.

**40 tests** — login flows (admin/marketing/operations/finance), form error
display, route guards (redirect to login on unauthenticated access), logout,
dashboard rendering per role (stat cards, sidebar navigation, subpages), page
rendering (customer, supplier, offering letters, purchase orders, delivery
orders, invoices, detail pages), responsive layout (mobile viewport, sidebar
behavior), and browser console error auditing.

---

## Quick Reference

| Layer | Command | Count |
|---|---|---|
| Backend | `pytest tests/ -v` | 95 |
| Frontend (headless) | `npx vitest run` | 53 |
| Frontend (browser) | `npx playwright test` | 40 |
