# API Documentation — Mandalan API

Base URL: `http://localhost:8000/api/v1`

Interactive docs: [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)

---

## Daftar Endpoint (54 routes)

| Method | Endpoint | Keterangan |
|--------|----------|------------|
| **HEALTH** | | |
| GET | `/health` | Cek status server |
| **AUTH** | | |
| POST | `/auth/login` | Login user |
| **CUSTOMERS** | | |
| GET | `/customers` | List semua customer |
| GET | `/customers/{id}` | Detail customer |
| POST | `/customers` | Tambah customer |
| PUT | `/customers/{id}` | Update customer |
| DELETE | `/customers/{id}` | Hapus customer |
| **SUPPLIERS** | | |
| GET | `/suppliers` | List semua supplier |
| GET | `/suppliers/{id}` | Detail supplier |
| POST | `/suppliers` | Tambah supplier |
| PUT | `/suppliers/{id}` | Update supplier |
| DELETE | `/suppliers/{id}` | Hapus supplier |
| **PROFILES (User Management)** | | |
| GET | `/profiles` | List semua user |
| GET | `/profiles/{id}` | Detail user |
| POST | `/profiles` | Tambah user |
| PUT | `/profiles/{id}` | Update user |
| DELETE | `/profiles/{id}` | Hapus user |
| **OFFERING LETTERS** | | |
| GET | `/offering-letters` | List (paginated: `?page=&page_size=`) |
| GET | `/offering-letters/{id}` | Detail |
| POST | `/offering-letters` | Buat baru |
| PUT | `/offering-letters/{id}` | Update |
| DELETE | `/offering-letters/{id}` | Hapus |
| **PURCHASE ORDERS** | | |
| GET | `/purchase-orders` | List (paginated, filter `?type=customer\|supplier`) |
| GET | `/purchase-orders/{id}` | Detail |
| POST | `/purchase-orders` | Buat baru |
| PUT | `/purchase-orders/{id}` | Update |
| DELETE | `/purchase-orders/{id}` | Hapus |
| **DELIVERY ORDERS** | | |
| GET | `/delivery-orders` | List (paginated) |
| GET | `/delivery-orders/{id}` | Detail |
| POST | `/delivery-orders` | Buat baru |
| PUT | `/delivery-orders/{id}` | Update |
| DELETE | `/delivery-orders/{id}` | Hapus |
| **INVOICES** | | |
| GET | `/invoices` | List (paginated) |
| GET | `/invoices/{id}` | Detail |
| POST | `/invoices` | Buat baru |
| PUT | `/invoices/{id}` | Update |
| DELETE | `/invoices/{id}` | Hapus |
| **SALES** | | |
| GET | `/sales` | List (query `?limit=`) |
| GET | `/sales/{id}` | Detail |
| POST | `/sales` | Buat baru |
| PUT | `/sales/{id}` | Update |
| DELETE | `/sales/{id}` | Hapus |
| **NOTIFICATIONS** | | |
| GET | `/notifications` | List semua |
| GET | `/notifications/{id}` | Detail |
| POST | `/notifications` | Buat baru |
| PUT | `/notifications/{id}` | Update |
| DELETE | `/notifications/{id}` | Hapus |
| **STATS** | | |
| GET | `/stats/marketing` | Statistik marketing |
| GET | `/stats/operations` | Statistik operasional |
| GET | `/stats/finance` | Statistik keuangan |
| GET | `/stats/home` | Statistik halaman utama |

---

## Contoh Request/Response

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@email.com","password":"admin123"}'
```

```json
{
  "name": "Admin",
  "email": "admin@email.com",
  "role": "admin",
  "token": "token-<uuid>",
  "logged_in_at": "2026-07-23T12:00:00"
}
```

### Buat Offering Letter (dengan full form data)

```bash
curl -X POST http://localhost:8000/api/v1/offering-letters \
  -H "Content-Type: application/json" \
  -d '{
    "offering_letter_number": "722/MAP/II-06/26",
    "customer_id": "<customer-uuid>",
    "location": "Samarinda",
    "date": "2026-07-23",
    "regarding": "Penawaran BBM",
    "receiver": "PT Customer",
    "fuel_total_price": 17950000,
    "transport_price": 1000000,
    "status": "created",
    "details": {
      "supplyPoint": "TBBM Palaran",
      "qualityAssurance": "Sesuai SK Dirjen Migas",
      "volumeUnit": "Liter",
      "paymentTerm": 7,
      "fuelPrices": {
        "basePrice": 17950,
        "sellingPrice": { "ppkb": 1795, "ppn": 1974.5 }
      }
    }
  }'
```

### List Offering Letters (paginated)

```bash
curl "http://localhost:8000/api/v1/offering-letters?page=1&page_size=10"
```

```json
{
  "items": [ ... ],
  "total": 15,
  "page": 1,
  "page_size": 10
}
```

### List Purchase Orders (filter by type)

```bash
curl "http://localhost:8000/api/v1/purchase-orders?type=supplier&page=1&page_size=20"
```

### List Sales

```bash
curl "http://localhost:8000/api/v1/sales?limit=5"
```

---

## Field `details` (JSON)

Dokumen **Offering Letter**, **Purchase Order**, **Delivery Order**, dan **Invoice** memiliki field `details` yang menyimpan seluruh data form dari frontend.

Frontend bebas mengirim struktur JSON apa pun di field ini — backend akan menyimpan dan mengembalikannya tanpa perubahan. Field summary (status, tanggal, total, dll) tetap terpisah untuk keperluan listing dan filtering.

---

## Common Response Format

### Paginated

```json
{ "items": [], "total": 0, "page": 1, "page_size": 20 }
```

### Error

```json
{ "detail": "Not found" }
```

### Delete

```json
{ "message": "Deleted", "code": 200 }
```

---

## Tech Stack Backend

- **FastAPI** — framework Python
- **SQLAlchemy 2.0** — ORM async
- **aiomysql** — driver MySQL async
- **Pydantic v2** — validasi data
- **OpenAPI** — dokumentasi otomatis
