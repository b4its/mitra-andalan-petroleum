# API Documentation — Mandalan API

Base URL: `http://localhost:8000/api/v1`

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Cek status server |

**Response:**
```json
{ "message": "OK", "code": 200 }
```

---

## Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login user |

### POST /auth/login

**Request body:**
```json
{
  "email": "admin@email.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "name": "Admin Mandalan",
  "email": "admin@mandalan.com",
  "role": "super_admin",
  "token": "token-<uuid>",
  "logged_in_at": "2025-01-01T00:00:00+00:00"
}
```

---

## Profiles (User Management)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles` | List semua user |
| GET | `/profiles/{id}` | Detail user |
| POST | `/profiles` | Buat user baru |
| PUT | `/profiles/{id}` | Update user |
| DELETE | `/profiles/{id}` | Hapus user |

### POST /profiles

**Request body:**
```json
{
  "name": "Staff Baru",
  "email": "staff@mandalan.com",
  "password": "staff123",
  "role": "staff"
}
```

### PUT /profiles/{id}

**Request body (semua field opsional):**
```json
{
  "name": "Nama Baru",
  "email": "baru@mandalan.com",
  "password": "pass123",
  "role": "super_admin"
}
```

---

## Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | List semua customer |
| GET | `/customers/{id}` | Detail customer |
| POST | `/customers` | Buat customer baru |
| PUT | `/customers/{id}` | Update customer |
| DELETE | `/customers/{id}` | Hapus customer |

### POST /customers

**Request body:**
```json
{
  "name": "PT Contoh",
  "phone": "08123456789",
  "email": "contoh@email.com",
  "address": "Jl. Contoh No. 1",
  "pic_name": "Budi",
  "pic_phone": "08123456780"
}
```

---

## Suppliers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/suppliers` | List semua supplier |
| GET | `/suppliers/{id}` | Detail supplier |
| POST | `/suppliers` | Buat supplier baru |
| PUT | `/suppliers/{id}` | Update supplier |
| DELETE | `/suppliers/{id}` | Hapus supplier |

---

## Offering Letters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/offering-letters` | List offering letters (paginated) |
| GET | `/offering-letters/{id}` | Detail offering letter |
| POST | `/offering-letters` | Buat offering letter baru |
| PUT | `/offering-letters/{id}` | Update offering letter |
| DELETE | `/offering-letters/{id}` | Hapus offering letter |

**Query params:** `?page=1&page_size=20`

---

## Purchase Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/purchase-orders` | List PO (paginated, filterable) |
| GET | `/purchase-orders/{id}` | Detail PO |
| POST | `/purchase-orders` | Buat PO baru |
| PUT | `/purchase-orders/{id}` | Update PO |
| DELETE | `/purchase-orders/{id}` | Hapus PO |

**Query params:** `?page=1&page_size=20&type=customer` (type: `customer` | `supplier`)

---

## Delivery Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/delivery-orders` | List DO (paginated) |
| GET | `/delivery-orders/{id}` | Detail DO |
| POST | `/delivery-orders` | Buat DO baru |
| PUT | `/delivery-orders/{id}` | Update DO |
| DELETE | `/delivery-orders/{id}` | Hapus DO |

---

## Invoices

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/invoices` | List invoice (paginated) |
| GET | `/invoices/{id}` | Detail invoice |
| POST | `/invoices` | Buat invoice baru |
| PUT | `/invoices/{id}` | Update invoice |
| DELETE | `/invoices/{id}` | Hapus invoice |

---

## Sales

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sales` | List sales terbaru (limit 5) |
| GET | `/sales/{id}` | Detail sale |
| POST | `/sales` | Buat sale baru |
| PUT | `/sales/{id}` | Update sale |
| DELETE | `/sales/{id}` | Hapus sale |

---

## Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications` | List semua notifikasi |
| GET | `/notifications/{id}` | Detail notifikasi |
| POST | `/notifications` | Buat notifikasi baru |
| PUT | `/notifications/{id}` | Update notifikasi |
| DELETE | `/notifications/{id}` | Hapus notifikasi |

---

## Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats/marketing` | Statistik marketing |
| GET | `/stats/operations` | Statistik operasional |
| GET | `/stats/finance` | Statistik keuangan |
| GET | `/stats/home` | Statistik halaman utama |

---

## Response Format

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### Error Response
```json
{
  "detail": "Not found"
}
```

### Delete Response
```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Tech Stack

- **Framework:** FastAPI (Python)
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** MySQL via aiomysql
- **Validasi:** Pydantic v2
- **Dokumentasi:** OpenAPI (Swagger UI otomatis)
