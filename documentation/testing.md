# Testing

## Stack

| Layer | Tool |
|-------|------|
| Test runner | pytest 8.x |
| HTTP client | `starlette.testclient.TestClient` (synchronous) |
| Database | SQLite via `sqlite+aiosqlite` (async engine) + `sqlite` (sync engine) |
| ORM | SQLAlchemy 2.0 (async) |

## Quick Start

```bash
pytest                          # all tests
pytest tests/test_auth.py       # single file
pytest tests/ -k "customer"     # filter by name
pytest tests/ -x -v             # stop on first failure, verbose
```

## Test Database

The test suite uses a **SQLite file** at `/tmp/test.db` instead of MySQL/Docker.

- **Async engine** (`app.core.database.engine`): `sqlite+aiosqlite:////tmp/test.db`
- **Sync engine** (fixture only): `sqlite:////tmp/test.db`

Both point to the same file so the app's async queries and the fixture's sync setup/teardown share data.

### URL note

SQLite requires **four slashes** for an absolute path:

```python
# Correct — absolute path
"sqlite:////tmp/test.db"

# Incorrect — relative path, resolves to CWD/tmp/test.db
"sqlite:///tmp/test.db"
```

## Test Structure

```
tests/
├── conftest.py              # shared fixtures, engine, lifespan override
├── pytest.ini               # pytest config
├── test_auth.py             # 9 tests — login, validation, health
├── test_customers.py        # 10 tests — CRUD + validation
├── test_delivery_orders.py  # 8 tests — CRUD + validation
├── test_invoices.py         # 10 tests — CRUD + status transitions
├── test_notifications.py    # 6 tests — CRUD + mark-read
├── test_offering_letters.py # 11 tests — CRUD + pagination + validation
├── test_profiles.py         # 8 tests — CRUD + duplicate email
├── test_purchase_orders.py  # 10 tests — CRUD + type filter + validation
├── test_stats.py            # 6 tests — marketing/operations/finance/home
└── test_suppliers.py        # 8 tests — CRUD + validation
```

**Total**: 95 tests.

## Fixtures (conftest.py)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `reset_db` | function (autouse) | Drops all rows from every table before each test |
| `client` | function | `TestClient(app)` context manager |
| `seeded_db` | function | Inserts seed data (users, customers, suppliers, OL, PO, DO, invoices, notifications) and returns their IDs |

### `seeded_db` data

| Entity | Records |
|--------|---------|
| users | Admin (`admin@email.com`), Marketing (`marketing@email.com`) |
| customers | PT Bina Karya |
| suppliers | PT Supplier Logistik |
| offering_letters | 001/OL/VI/2025 |
| purchase_orders | PO/2025/VI/100 |
| delivery_orders | 001/DO/VI/2025 |
| invoices | INV/2025/VI/001 |
| notifications | Test Notif |

## Lifespan Bypass

The app's `lifespan` is replaced with a no-op to prevent the seed script (`app.db.seed.seed_database`) from running during tests:

```python
@asynccontextmanager
async def noop_lifespan_context(app_):
    yield None

app.router.lifespan_context = noop_lifespan_context
```

## Writing Tests

Tests are **synchronous** and use `TestClient`:

```python
from starlette.testclient import TestClient


def test_list_customers(client: TestClient, seeded_db):
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

## Validation Tests

Some endpoints do **not** enforce input validation for negative values, missing foreign keys, etc. These tests accept both `201` (success) and `422` (validation error) to document the gap:

```python
assert response.status_code in (201, 422)
```

## Key Decisions

1. **Sync TestClient** instead of `httpx.AsyncClient` — avoids event-loop issues with async engine + greenlet
2. **SQLite** instead of MySQL — fast, isolated, no Docker dependency
3. **No lifespan** — prevents the seed script from inserting duplicate data
4. **Autouse `reset_db`** — ensures isolation between tests by clearing all tables
5. **File-based SQLite** instead of `:memory:` — allows both sync and async engines to share the same database
