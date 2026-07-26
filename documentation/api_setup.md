# API Documentation — Mandalan API

Base URL: `http://localhost:8000/api/v1`

Interactive docs: [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)

---

## Daftar Isi

- [Akun Default](#akun-default)
- [Health Check](#health-check)
- [Auth](#auth)
- [Customers](#customers)
- [Suppliers](#suppliers)
- [Profiles (User Management)](#profiles-user-management)
- [Offering Letters](#offering-letters)
- [Purchase Orders](#purchase-orders)
- [Delivery Orders](#delivery-orders)
- [Invoices](#invoices)
- [Sales](#sales)
- [Notifications](#notifications)
- [Uploads](#uploads)
- [Stats](#stats)
- [Field `details` JSON](#field-details-json)
- [Common Response Format](#common-response-format)

---

## Akun Default

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@email.com | admin123 |
| Marketing | marketing@email.com | marketing123 |
| Finance | finance@email.com | finance123 |
| Operations | ops@email.com | ops123 |

---

## Health Check

Cek apakah server berjalan.

### GET /health

```bash
curl -X GET http://localhost:8000/api/v1/health
```

```json
{
  "message": "OK",
  "code": 200
}
```

---

## Auth

### POST /auth/login

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
  "token": "token-f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "logged_in_at": "2026-07-26T10:30:00.000000"
}
```

---

## Customers

### GET /customers — List semua customer

```bash
curl -X GET http://localhost:8000/api/v1/customers
```

```json
[
  {
    "id": "uuid-customer-1",
    "name": "PT Bintang Jaya",
    "address": "Jl. A. Yani No. 10",
    "phone": "08123456789",
    "email": "bintang@example.com"
  }
]
```

### GET /customers/{id} — Detail customer

```bash
curl -X GET http://localhost:8000/api/v1/customers/uuid-customer-1
```

```json
{
  "id": "uuid-customer-1",
  "name": "PT Bintang Jaya",
  "address": "Jl. A. Yani No. 10",
  "phone": "08123456789",
  "email": "bintang@example.com"
}
```

### POST /customers — Tambah customer

```bash
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PT Maju Mundur",
    "address": "Jl. Sudirman No. 5",
    "phone": "08765432100",
    "email": "maju@example.com"
  }'
```

```json
{
  "id": "uuid-customer-baru",
  "name": "PT Maju Mundur",
  "address": "Jl. Sudirman No. 5",
  "phone": "08765432100",
  "email": "maju@example.com"
}
```

### PUT /customers/{id} — Update customer

```bash
curl -X PUT http://localhost:8000/api/v1/customers/uuid-customer-baru \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "08111111111"
  }'
```

```json
{
  "id": "uuid-customer-baru",
  "name": "PT Maju Mundur",
  "address": "Jl. Sudirman No. 5",
  "phone": "08111111111",
  "email": "maju@example.com"
}
```

### DELETE /customers/{id} — Hapus customer

```bash
curl -X DELETE http://localhost:8000/api/v1/customers/uuid-customer-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Suppliers

### GET /suppliers — List semua supplier

```bash
curl -X GET http://localhost:8000/api/v1/suppliers
```

```json
[
  {
    "id": "uuid-supplier-1",
    "name": "PT Solar Indo",
    "address": "Jl. Pelabuhan No. 1",
    "phone": "08111122233",
    "email": "solar@example.com"
  }
]
```

### GET /suppliers/{id} — Detail supplier

```bash
curl -X GET http://localhost:8000/api/v1/suppliers/uuid-supplier-1
```

```json
{
  "id": "uuid-supplier-1",
  "name": "PT Solar Indo",
  "address": "Jl. Pelabuhan No. 1",
  "phone": "08111122233",
  "email": "solar@example.com"
}
```

### POST /suppliers — Tambah supplier

```bash
curl -X POST http://localhost:8000/api/v1/suppliers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PT Bahan Bakar Nusantara",
    "address": "Jl. Industri Raya No. 8",
    "phone": "08222233344",
    "email": "bbn@example.com"
  }'
```

```json
{
  "id": "uuid-supplier-baru",
  "name": "PT Bahan Bakar Nusantara",
  "address": "Jl. Industri Raya No. 8",
  "phone": "08222233344",
  "email": "bbn@example.com"
}
```

### PUT /suppliers/{id} — Update supplier

```bash
curl -X PUT http://localhost:8000/api/v1/suppliers/uuid-supplier-baru \
  -H "Content-Type: application/json" \
  -d '{
    "email": "update@example.com"
  }'
```

```json
{
  "id": "uuid-supplier-baru",
  "name": "PT Bahan Bakar Nusantara",
  "address": "Jl. Industri Raya No. 8",
  "phone": "08222233344",
  "email": "update@example.com"
}
```

### DELETE /suppliers/{id} — Hapus supplier

```bash
curl -X DELETE http://localhost:8000/api/v1/suppliers/uuid-supplier-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Profiles (User Management)

### GET /profiles — List semua user

```bash
curl -X GET http://localhost:8000/api/v1/profiles
```

```json
[
  {
    "id": "uuid-user-1",
    "name": "Admin",
    "email": "admin@email.com",
    "role": "admin"
  }
]
```

### GET /profiles/{id} — Detail user

```bash
curl -X GET http://localhost:8000/api/v1/profiles/uuid-user-1
```

```json
{
  "id": "uuid-user-1",
  "name": "Admin",
  "email": "admin@email.com",
  "role": "admin"
}
```

### POST /profiles — Tambah user

```bash
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Staff Baru",
    "email": "staff@email.com",
    "password": "staff123",
    "role": "staff"
  }'
```

```json
{
  "id": "uuid-user-baru",
  "name": "Staff Baru",
  "email": "staff@email.com",
  "role": "staff"
}
```

### PUT /profiles/{id} — Update user

```bash
curl -X PUT http://localhost:8000/api/v1/profiles/uuid-user-baru \
  -H "Content-Type: application/json" \
  -d '{
    "role": "marketing",
    "password": "newpass123"
  }'
```

```json
{
  "id": "uuid-user-baru",
  "name": "Staff Baru",
  "email": "staff@email.com",
  "role": "marketing"
}
```

### DELETE /profiles/{id} — Hapus user

```bash
curl -X DELETE http://localhost:8000/api/v1/profiles/uuid-user-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Offering Letters

### GET /offering-letters — List (paginated)

Query params: `?page=1&page_size=20`

```bash
curl "http://localhost:8000/api/v1/offering-letters?page=1&page_size=10"
```

```json
{
  "items": [
    {
      "id": "uuid-ol-1",
      "offering_letter_number": "722/MAP/II-06/26",
      "customer_id": "uuid-customer-1",
      "customer_name": "PT Bintang Jaya",
      "location": "Samarinda",
      "date": "2026-07-23",
      "regarding": "Penawaran BBM",
      "receiver": "PT Bintang Jaya",
      "fuel_total_price": 17950000,
      "transport_price": 1000000,
      "status": "created",
      "details": {
        "supplyPoint": "TBBM Palaran",
        "qualityAssurance": "Sesuai SK Dirjen Migas",
        "volumeUnit": "Liter",
        "paymentTerm": 7
      },
      "created_at": "2026-07-23T10:00:00",
      "updated_at": "2026-07-23T10:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10
}
```

### GET /offering-letters/{id} — Detail

```bash
curl -X GET http://localhost:8000/api/v1/offering-letters/uuid-ol-1
```

```json
{
  "id": "uuid-ol-1",
  "offering_letter_number": "722/MAP/II-06/26",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "location": "Samarinda",
  "date": "2026-07-23",
  "regarding": "Penawaran BBM",
  "receiver": "PT Bintang Jaya",
  "fuel_total_price": 17950000,
  "transport_price": 1000000,
  "status": "created",
  "details": {
    "supplyPoint": "TBBM Palaran",
    "qualityAssurance": "Sesuai SK Dirjen Migas",
    "custodyTransfer": "Setelah kendaraan selesai bongkar",
    "unloadingProcedure": "Menggunakan selang flexi",
    "volumeUnit": "Liter",
    "volumeTolerance": 0.5,
    "paymentTerm": 7,
    "latePenalty": 0.05,
    "servicePattern": "SSP (Sell, Service, Product)",
    "personInCharge": {
      "name": "Andi",
      "phoneNumber": "081234567890"
    },
    "paymentAddress": {
      "bankName": "Bank Mandiri",
      "accountNumber": "1234567890",
      "accountName": "PT Mitra Andalan Petroleum"
    },
    "fuelPrices": {
      "logisticInformation": "PPKB + OAT",
      "productName": "Solar",
      "basePrice": 17950,
      "totalPrice": 17950000,
      "sellingPrice": {
        "ppkb": 1795,
        "oat": null,
        "ppn": 1974.5
      },
      "percentageNum": {
        "ppkb": 10,
        "oat": 0,
        "ppn": 11
      }
    }
  },
  "created_at": "2026-07-23T10:00:00",
  "updated_at": "2026-07-23T10:00:00"
}
```

### POST /offering-letters — Buat baru

```bash
curl -X POST http://localhost:8000/api/v1/offering-letters \
  -H "Content-Type: application/json" \
  -d '{
    "offering_letter_number": "723/MAP/II-06/26",
    "customer_id": "uuid-customer-1",
    "location": "Samarinda",
    "date": "2026-07-23",
    "regarding": "Penawaran BBM Solar",
    "receiver": "PT Bintang Jaya",
    "fuel_total_price": 17950000,
    "transport_price": 1000000,
    "status": "created",
    "details": {
      "supplyPoint": "TBBM Palaran",
      "fuelPrices": {
        "basePrice": 17950,
        "sellingPrice": { "ppkb": 1795, "ppn": 1974.5 }
      }
    }
  }'
```

```json
{
  "id": "uuid-ol-baru",
  "offering_letter_number": "723/MAP/II-06/26",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "location": "Samarinda",
  "date": "2026-07-23",
  "regarding": "Penawaran BBM Solar",
  "receiver": "PT Bintang Jaya",
  "fuel_total_price": 17950000,
  "transport_price": 1000000,
  "status": "created",
  "details": {
    "supplyPoint": "TBBM Palaran",
    "fuelPrices": {
      "basePrice": 17950,
      "sellingPrice": { "ppkb": 1795, "ppn": 1974.5 }
    }
  },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T10:30:00"
}
```

### PUT /offering-letters/{id} — Update

```bash
curl -X PUT http://localhost:8000/api/v1/offering-letters/uuid-ol-baru \
  -H "Content-Type: application/json" \
  -d '{
    "status": "po_received",
    "details": {
      "supplyPoint": "TBBM Balikpapan",
      "fuelPrices": {
        "basePrice": 18000,
        "sellingPrice": { "ppkb": 1800, "ppn": 1980 }
      }
    }
  }'
```

```json
{
  "id": "uuid-ol-baru",
  "offering_letter_number": "723/MAP/II-06/26",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "location": "Samarinda",
  "date": "2026-07-23",
  "regarding": "Penawaran BBM Solar",
  "receiver": "PT Bintang Jaya",
  "fuel_total_price": 17950000,
  "transport_price": 1000000,
  "status": "po_received",
  "details": {
    "supplyPoint": "TBBM Balikpapan",
    "fuelPrices": {
      "basePrice": 18000,
      "sellingPrice": { "ppkb": 1800, "ppn": 1980 }
    }
  },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T10:32:00"
}
```

### DELETE /offering-letters/{id} — Hapus

```bash
curl -X DELETE http://localhost:8000/api/v1/offering-letters/uuid-ol-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Purchase Orders

### GET /purchase-orders — List (paginated + filter)

Query params: `?page=1&page_size=20&type=customer` (atau `type=supplier`)

```bash
curl "http://localhost:8000/api/v1/purchase-orders?page=1&page_size=10&type=supplier"
```

```json
{
  "items": [
    {
      "id": "uuid-po-1",
      "po_number": "PO/MAP/VI-26/001",
      "type": "supplier",
      "customer_id": null,
      "supplier_id": "uuid-supplier-1",
      "customer_name": "",
      "supplier_name": "PT Solar Indo",
      "date": "2026-07-20",
      "total": 50000000,
      "status": "created",
      "details": null,
      "created_at": "2026-07-20T09:00:00",
      "updated_at": "2026-07-20T09:00:00"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 10
}
```

### GET /purchase-orders/{id} — Detail

```bash
curl -X GET http://localhost:8000/api/v1/purchase-orders/uuid-po-1
```

```json
{
  "id": "uuid-po-1",
  "po_number": "PO/MAP/VI-26/001",
  "type": "supplier",
  "customer_id": null,
  "supplier_id": "uuid-supplier-1",
  "customer_name": "",
  "supplier_name": "PT Solar Indo",
  "date": "2026-07-20",
  "total": 50000000,
  "status": "created",
  "details": {
    "companyInformation": {
      "name": "PT Mitra Andalan Petroleum",
      "address": "Jl. Contoh No. 1",
      "npwp": "12.345.678.9-000.000",
      "contactPerson": "Andi",
      "email": "map@example.com"
    },
    "po": {
      "date": "2026-07-20",
      "number": "PO/MAP/VI-26/001"
    },
    "vat": 11,
    "paymentAddress": {
      "bankName": "Bank Mandiri",
      "accountNumber": "1234567890",
      "accountName": "PT Mitra Andalan Petroleum"
    },
    "products": [
      {
        "name": "Solar Industri",
        "qty": 10000,
        "unit": "Liter",
        "price": 5000,
        "totalPrice": 50000000
      }
    ],
    "totalProductsPrice": 50000000,
    "termAndCondition": "Pembayaran 7 hari setelah DO",
    "delivery": {
      "loadingTerminal": "TBBM Balikpapan",
      "loadingDate": "2026-07-22",
      "picOperationMap": "Budi"
    },
    "forwarder": {
      "trucking": "PT Logistik Nusantara"
    },
    "signed": {
      "createdBy": "Marketing",
      "approvedBy": "Direktur"
    }
  },
  "created_at": "2026-07-20T09:00:00",
  "updated_at": "2026-07-20T09:00:00"
}
```

### POST /purchase-orders — Buat baru

```bash
curl -X POST http://localhost:8000/api/v1/purchase-orders \
  -H "Content-Type: application/json" \
  -d '{
    "po_number": "PO/MAP/VII-26/002",
    "type": "supplier",
    "supplier_id": "uuid-supplier-1",
    "date": "2026-07-26",
    "total": 30000000,
    "status": "created",
    "details": {
      "po": { "date": "2026-07-26", "number": "PO/MAP/VII-26/002" },
      "products": [
        { "name": "Diesel", "qty": 5000, "unit": "Liter", "price": 6000, "totalPrice": 30000000 }
      ],
      "totalProductsPrice": 30000000,
      "vat": 11,
      "paymentAddress": {
        "bankName": "BNI",
        "accountNumber": "0987654321",
        "accountName": "PT Mitra Andalan Petroleum"
      },
      "termAndCondition": "Pembayaran 14 hari",
      "forwarder": { "trucking": "PT Angkut Cepat" },
      "signed": { "createdBy": "Marketing", "approvedBy": "Finance" }
    }
  }'
```

```json
{
  "id": "uuid-po-baru",
  "po_number": "PO/MAP/VII-26/002",
  "type": "supplier",
  "customer_id": null,
  "supplier_id": "uuid-supplier-1",
  "customer_name": "",
  "supplier_name": "PT Solar Indo",
  "date": "2026-07-26",
  "total": 30000000,
  "status": "created",
  "details": { ... },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T10:30:00"
}
```

### PUT /purchase-orders/{id} — Update

```bash
curl -X PUT http://localhost:8000/api/v1/purchase-orders/uuid-po-baru \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "total": 33000000,
    "details": {
      "vat": 11,
      "products": [
        { "name": "Diesel", "qty": 5000, "unit": "Liter", "price": 6000, "totalPrice": 30000000 }
      ],
      "totalProductsPrice": 30000000
    }
  }'
```

```json
{
  "id": "uuid-po-baru",
  "po_number": "PO/MAP/VII-26/002",
  "type": "supplier",
  "customer_id": null,
  "supplier_id": "uuid-supplier-1",
  "customer_name": "",
  "supplier_name": "PT Solar Indo",
  "date": "2026-07-26",
  "total": 33000000,
  "status": "approved",
  "details": { ... },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T10:35:00"
}
```

### DELETE /purchase-orders/{id} — Hapus

```bash
curl -X DELETE http://localhost:8000/api/v1/purchase-orders/uuid-po-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Delivery Orders

### GET /delivery-orders — List (paginated)

```bash
curl "http://localhost:8000/api/v1/delivery-orders?page=1&page_size=10"
```

```json
{
  "items": [
    {
      "id": "uuid-do-1",
      "do_number": "DO/MAP/VI-26/001",
      "customer_id": "uuid-customer-1",
      "customer_name": "PT Bintang Jaya",
      "po_number": "PO/MAP/VI-26/001",
      "transport_name": "PT Logistik Nusantara",
      "fuel_total": 20000,
      "status": "delivered",
      "details": null,
      "created_at": "2026-07-21T08:00:00",
      "updated_at": "2026-07-21T08:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10
}
```

### GET /delivery-orders/{id} — Detail

```bash
curl -X GET http://localhost:8000/api/v1/delivery-orders/uuid-do-1
```

```json
{
  "id": "uuid-do-1",
  "do_number": "DO/MAP/VI-26/001",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "po_number": "PO/MAP/VI-26/001",
  "transport_name": "PT Logistik Nusantara",
  "fuel_total": 20000,
  "status": "delivered",
  "details": {
    "companyInformation": {
      "name": "PT Mitra Andalan Petroleum",
      "address": "Jl. Contoh No. 1",
      "phoneNumber": "08123456789"
    },
    "doInformation": {
      "doNumber": "DO/MAP/VI-26/001",
      "doDateCreated": "2026-07-21",
      "poCustomerNumber": "PO/MAP/VI-26/001",
      "soNumber": "SO/001"
    },
    "receiver": {
      "customerName": "PT Bintang Jaya",
      "address": "Jl. A. Yani No. 10",
      "receiverInformation": { "name": "Budi", "phoneNumber": "08123456789" },
      "dateReceived": "2026-07-21"
    },
    "transport": {
      "transportName": "PT Logistik Nusantara",
      "transportId": "TRK-001",
      "address": "Jl. Transport No. 1",
      "driverInformation": { "name": "Slamet", "phoneNumber": "08234567890" },
      "helperName": "Joko",
      "dateReceived": "2026-07-21"
    },
    "detailsTransport": {
      "productInformation": { "name": "Solar", "qty": 20000, "temperature": 30, "topSeal": "12345", "bottomSeal": "54321" },
      "transportInformation": { "transportType": "Tangki", "transportNumber": "KT 1234 AB", "startKm": 1000, "endKm": 1100, "sgMeter": 0.84, "timeInformation": { "departureTime": "08:00", "arrivalTime": "14:00", "unloadingTime": "15:00", "depotArrivalTime": "07:00" } },
      "total": 20000
    },
    "additional": { "notes": [{ "note": "Hati-hati muatan" }], "t2Depot": 30, "t2Unloading": 28, "indexSensitivity": 0.5, "fuelReceived": 19980 },
    "footer": { "companyCoordinator": "Andi", "distributionAdmin": "Rina", "receiver": "Budi", "driver": "Slamet" }
  },
  "created_at": "2026-07-21T08:00:00",
  "updated_at": "2026-07-21T08:00:00"
}
```

### POST /delivery-orders — Buat baru

```bash
curl -X POST http://localhost:8000/api/v1/delivery-orders \
  -H "Content-Type: application/json" \
  -d '{
    "do_number": "DO/MAP/VII-26/002",
    "customer_id": "uuid-customer-1",
    "po_number": "PO/MAP/VII-26/002",
    "transport_name": "PT Angkut Cepat",
    "fuel_total": 15000,
    "status": "created",
    "details": {
      "companyInformation": {
        "name": "PT Mitra Andalan Petroleum",
        "address": "Jl. Contoh No. 1",
        "phoneNumber": "08123456789"
      },
      "doInformation": {
        "doNumber": "DO/MAP/VII-26/002",
        "doDateCreated": "2026-07-26",
        "poCustomerNumber": "PO/MAP/VII-26/002"
      },
      "receiver": {
        "customerName": "PT Bintang Jaya",
        "address": "Jl. A. Yani No. 10",
        "receiverInformation": { "name": "Budi" },
        "dateReceived": "2026-07-26"
      },
      "transport": {
        "transportName": "PT Angkut Cepat",
        "driverInformation": { "name": "Slamet" },
        "dateReceived": "2026-07-26"
      },
      "footer": { "companyCoordinator": "Andi", "distributionAdmin": "Rina" }
    }
  }'
```

```json
{
  "id": "uuid-do-baru",
  "do_number": "DO/MAP/VII-26/002",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "po_number": "PO/MAP/VII-26/002",
  "transport_name": "PT Angkut Cepat",
  "fuel_total": 15000,
  "status": "created",
  "details": { ... },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T10:30:00"
}
```

### PUT /delivery-orders/{id} — Update

```bash
curl -X PUT http://localhost:8000/api/v1/delivery-orders/uuid-do-baru \
  -H "Content-Type: application/json" \
  -d '{
    "status": "delivered",
    "details": {
      "detailsTransport": {
        "productInformation": { "name": "Solar", "qty": 15000, "temperature": 31 },
        "transportInformation": {
          "transportType": "Tangki", "transportNumber": "KT 5678 CD",
          "startKm": 2000, "endKm": 2100
        },
        "total": 15000
      },
      "additional": { "fuelReceived": 14980 }
    }
  }'
```

```json
{
  "id": "uuid-do-baru",
  "do_number": "DO/MAP/VII-26/002",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "po_number": "PO/MAP/VII-26/002",
  "transport_name": "PT Angkut Cepat",
  "fuel_total": 15000,
  "status": "delivered",
  "details": { ... },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T11:00:00"
}
```

### DELETE /delivery-orders/{id} — Hapus

```bash
curl -X DELETE http://localhost:8000/api/v1/delivery-orders/uuid-do-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Invoices

### GET /invoices — List (paginated)

```bash
curl "http://localhost:8000/api/v1/invoices?page=1&page_size=10"
```

```json
{
  "items": [
    {
      "id": "uuid-inv-1",
      "invoice_number": "INV/MAP/VI-26/001",
      "customer_id": "uuid-customer-1",
      "customer_name": "PT Bintang Jaya",
      "terms_day": 30,
      "grand_total": 50000000,
      "invoice_status": "unpaid",
      "deadline_status": "on_time",
      "details": null,
      "created_at": "2026-07-22T09:00:00",
      "updated_at": "2026-07-22T09:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10
}
```

### GET /invoices/{id} — Detail

```bash
curl -X GET http://localhost:8000/api/v1/invoices/uuid-inv-1
```

```json
{
  "id": "uuid-inv-1",
  "invoice_number": "INV/MAP/VI-26/001",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "terms_day": 30,
  "grand_total": 50000000,
  "invoice_status": "unpaid",
  "deadline_status": "on_time",
  "details": {
    "companyInformation": {
      "name": "PT Mitra Andalan Petroleum",
      "address": "Jl. Contoh No. 1, Samarinda",
      "phoneNumber": "08123456789",
      "email": "map@example.com"
    },
    "billToInformation": "PT Bintang Jaya",
    "deliveryPointInformation": "TBBM Palaran",
    "invoiceInformation": {
      "invoiceNumber": "INV/MAP/VI-26/001",
      "invoiceDate": "2026-07-22",
      "terms": 30,
      "invoiceDueDate": "2026-08-21"
    },
    "customerPurchaseInformation": {
      "deliveryOrderNumberData": ["DO/MAP/VI-26/001"],
      "customerPurchaseOrderNumber": "PO/MAP/VI-26/001",
      "taxInvoiceNumber": "010.000-24.00000001",
      "salesOrderNumber": "SO/001"
    },
    "products": [
      { "qty": 10000, "unit": "Liter", "name": "Solar Industri", "price": 5000, "totalPrice": 50000000 }
    ],
    "priceSummary": {
      "subTotal": 50000000,
      "prePaid": 0,
      "discount": 0,
      "ppn": 5500000,
      "grandTotal": 55500000,
      "spellNumber": "Lima puluh lima juta lima ratus ribu rupiah"
    },
    "termsAndCondition": [{ "term": "Pembayaran 30 hari setelah invoice" }],
    "paymentInformation": {
      "bankName": "Bank Mandiri",
      "accountNumber": "1234567890",
      "accountName": "PT Mitra Andalan Petroleum"
    },
    "signature": { "companyName": "PT Mitra Andalan Petroleum", "createdBy": "Finance" }
  },
  "created_at": "2026-07-22T09:00:00",
  "updated_at": "2026-07-22T09:00:00"
}
```

### POST /invoices — Buat baru

```bash
curl -X POST http://localhost:8000/api/v1/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV/MAP/VII-26/003",
    "customer_id": "uuid-customer-1",
    "terms_day": 14,
    "grand_total": 30000000,
    "invoice_status": "unpaid",
    "deadline_status": "on_time",
    "details": {
      "companyInformation": {
        "name": "PT Mitra Andalan Petroleum",
        "address": "Jl. Contoh No. 1, Samarinda",
        "phoneNumber": "08123456789",
        "email": "map@example.com"
      },
      "billToInformation": "PT Bintang Jaya",
      "invoiceInformation": {
        "invoiceNumber": "INV/MAP/VII-26/003",
        "invoiceDate": "2026-07-26",
        "terms": 14,
        "invoiceDueDate": "2026-08-09"
      },
      "products": [
        { "qty": 5000, "unit": "Liter", "name": "Diesel", "price": 6000, "totalPrice": 30000000 }
      ],
      "priceSummary": {
        "subTotal": 30000000,
        "ppn": 3300000,
        "grandTotal": 33300000,
        "spellNumber": "Tiga puluh tiga juta tiga ratus ribu rupiah"
      },
      "paymentInformation": {
        "bankName": "Bank Mandiri",
        "accountNumber": "1234567890",
        "accountName": "PT Mitra Andalan Petroleum"
      },
      "signature": { "companyName": "PT Mitra Andalan Petroleum", "createdBy": "Finance" }
    }
  }'
```

```json
{
  "id": "uuid-inv-baru",
  "invoice_number": "INV/MAP/VII-26/003",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "terms_day": 14,
  "grand_total": 30000000,
  "invoice_status": "unpaid",
  "deadline_status": "on_time",
  "details": { ... },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T10:30:00"
}
```

### PUT /invoices/{id} — Update

```bash
curl -X PUT http://localhost:8000/api/v1/invoices/uuid-inv-baru \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_status": "paid",
    "deadline_status": "on_time"
  }'
```

```json
{
  "id": "uuid-inv-baru",
  "invoice_number": "INV/MAP/VII-26/003",
  "customer_id": "uuid-customer-1",
  "customer_name": "PT Bintang Jaya",
  "terms_day": 14,
  "grand_total": 30000000,
  "invoice_status": "paid",
  "deadline_status": "on_time",
  "details": { ... },
  "created_at": "2026-07-26T10:30:00",
  "updated_at": "2026-07-26T11:00:00"
}
```

### DELETE /invoices/{id} — Hapus

```bash
curl -X DELETE http://localhost:8000/api/v1/invoices/uuid-inv-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Sales

### GET /sales — List (dengan limit)

Query params: `?limit=5`

```bash
curl "http://localhost:8000/api/v1/sales?limit=5"
```

```json
[
  {
    "id": "uuid-sale-1",
    "date": "2026-07-25",
    "status": "completed",
    "email": "customer@example.com",
    "amount": 50000000,
    "created_at": "2026-07-25T10:00:00"
  }
]
```

### GET /sales/{id} — Detail

```bash
curl -X GET http://localhost:8000/api/v1/sales/uuid-sale-1
```

```json
{
  "id": "uuid-sale-1",
  "date": "2026-07-25",
  "status": "completed",
  "email": "customer@example.com",
  "amount": 50000000,
  "created_at": "2026-07-25T10:00:00"
}
```

### POST /sales — Buat baru

```bash
curl -X POST http://localhost:8000/api/v1/sales \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-07-26",
    "status": "pending",
    "email": "customer@example.com",
    "amount": 30000000
  }'
```

```json
{
  "id": "uuid-sale-baru",
  "date": "2026-07-26",
  "status": "pending",
  "email": "customer@example.com",
  "amount": 30000000,
  "created_at": "2026-07-26T10:30:00"
}
```

### PUT /sales/{id} — Update

```bash
curl -X PUT http://localhost:8000/api/v1/sales/uuid-sale-baru \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

```json
{
  "id": "uuid-sale-baru",
  "date": "2026-07-26",
  "status": "completed",
  "email": "customer@example.com",
  "amount": 30000000,
  "created_at": "2026-07-26T10:30:00"
}
```

### DELETE /sales/{id} — Hapus

```bash
curl -X DELETE http://localhost:8000/api/v1/sales/uuid-sale-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Notifications

### GET /notifications — List semua

```bash
curl -X GET http://localhost:8000/api/v1/notifications
```

```json
[
  {
    "id": "uuid-notif-1",
    "title": "PO Baru",
    "message": "PO dari customer PT Bintang Jaya telah masuk",
    "type": "info",
    "sender_id": null,
    "to": "/marketing/customer",
    "created_at": "2026-07-26T10:00:00"
  }
]
```

### GET /notifications/{id} — Detail

```bash
curl -X GET http://localhost:8000/api/v1/notifications/uuid-notif-1
```

```json
{
  "id": "uuid-notif-1",
  "title": "PO Baru",
  "message": "PO dari customer PT Bintang Jaya telah masuk",
  "type": "info",
  "sender_id": null,
  "to": "/marketing/customer",
  "created_at": "2026-07-26T10:00:00"
}
```

### POST /notifications — Buat baru

```bash
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Invoice Jatuh Tempo",
    "message": "Invoice INV/MAP/VI-26/001 akan jatuh tempo dalam 3 hari",
    "type": "warning",
    "sender_id": "uuid-user-1",
    "to": "/finance/invoice/data-invoice-customer"
  }'
```

```json
{
  "id": "uuid-notif-baru",
  "title": "Invoice Jatuh Tempo",
  "message": "Invoice INV/MAP/VI-26/001 akan jatuh tempo dalam 3 hari",
  "type": "warning",
  "sender_id": "uuid-user-1",
  "to": "/finance/invoice/data-invoice-customer",
  "created_at": "2026-07-26T10:30:00"
}
```

### PUT /notifications/{id} — Update (misal: mark read)

```bash
curl -X PUT http://localhost:8000/api/v1/notifications/uuid-notif-baru \
  -H "Content-Type: application/json" \
  -d '{
    "type": "read"
  }'
```

```json
{
  "id": "uuid-notif-baru",
  "title": "Invoice Jatuh Tempo",
  "message": "Invoice INV/MAP/VI-26/001 akan jatuh tempo dalam 3 hari",
  "type": "read",
  "sender_id": "uuid-user-1",
  "to": "/finance/invoice/data-invoice-customer",
  "created_at": "2026-07-26T10:30:00"
}
```

### DELETE /notifications/{id} — Hapus

```bash
curl -X DELETE http://localhost:8000/api/v1/notifications/uuid-notif-baru
```

```json
{
  "message": "Deleted",
  "code": 200
}
```

---

## Uploads

Upload file signature, dokumen, atau lampiran lainnya. File disimpan di `backend/media/` dan bisa diakses via URL langsung.

### POST /upload — Upload file

Request: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Ya | File yang akan diupload (max 50MB) |
| `folder` | String | Tidak | Subfolder tujuan (`signatures`, `documents`, `returned`, `general`) |

Format file yang diizinkan: JPG, JPEG, PNG, GIF, BMP, WebP, SVG, PDF, DOC, DOCX, XLS, XLSX.

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/signature.png"
```

```json
{
  "filename": "a1b2c3d4e5f6.png",
  "url": "/media/general/a1b2c3d4e5f6.png",
  "size": 102400
}
```

Dengan folder:

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/signature.png" \
  -F "folder=signatures"
```

```json
{
  "filename": "f6e5d4c3b2a1.png",
  "url": "/media/signatures/f6e5d4c3b2a1.png",
  "size": 102400
}
```

Akses file: `http://localhost:8000/media/signatures/f6e5d4c3b2a1.png`

---

## Stats

### GET /stats/marketing

```bash
curl -X GET http://localhost:8000/api/v1/stats/marketing
```

```json
{
  "stats": [
    { "title": "Penawaran dibuat", "icon": "i-lucide-file-text", "value": 15, "variation": 12.5, "to": "/marketing/customer" },
    { "title": "Penawaran belum disetujui", "icon": "i-lucide-clock", "value": 3, "variation": -5.2, "to": "/marketing/customer" },
    { "title": "PO dari Customer", "icon": "i-lucide-shopping-cart", "value": 5, "variation": 8.3, "to": "/marketing/customer" },
    { "title": "PO untuk logistik", "icon": "i-lucide-truck", "value": 4, "variation": 3.1, "to": "/marketing/supplier" }
  ]
}
```

### GET /stats/operations

```bash
curl -X GET http://localhost:8000/api/v1/stats/operations
```

```json
{
  "stats": [
    { "title": "Delivery Order Dibuat", "icon": "i-lucide-file-text", "value": 15, "variation": 7.8, "to": "/operations" }
  ]
}
```

### GET /stats/finance

```bash
curl -X GET http://localhost:8000/api/v1/stats/finance
```

```json
{
  "stats": [
    { "title": "DO Diterima", "icon": "i-lucide-file-check", "value": 15, "variation": 5.4, "to": "/finance/do" },
    { "title": "Invoice Belum Dibuat", "icon": "i-lucide-file-minus", "value": 5, "variation": -2.1, "to": "/finance/invoice" },
    { "title": "Invoice Belum Lunas", "icon": "i-lucide-alert-circle", "value": 10, "variation": 11.3, "to": "/finance/invoice/data-invoice-customer" }
  ]
}
```

### GET /stats/home

```bash
curl -X GET http://localhost:8000/api/v1/stats/home
```

```json
{
  "stats": [
    { "title": "Customers", "icon": "i-lucide-users", "value": 3, "variation": 3.2, "to": "/marketing/customer" },
    { "title": "Revenue", "icon": "i-lucide-trending-up", "value": 50000000, "variation": 8.1, "to": "/finance" },
    { "title": "Orders", "icon": "i-lucide-shopping-bag", "value": 15, "variation": -1.5, "to": "/operations" }
  ]
}
```

---

## Field `details` (JSON)

Dokumen **Offering Letter**, **Purchase Order**, **Delivery Order**, dan **Invoice** memiliki field `details` yang menyimpan seluruh data form dari frontend.

Frontend bebas mengirim struktur JSON apa pun di field ini — backend akan menyimpan dan mengembalikannya tanpa perubahan. Field summary (status, tanggal, total, dll) tetap terpisah untuk keperluan listing dan filtering di database.

Contoh struktur `details` mengacu pada Zod schemas di `frontend/app/types/schemas.ts`:

- **OL**: `supplyPoint`, `qualityAssurance`, `volumeUnit`, `paymentTerm`, `fuelPrices`, `personInCharge`, `paymentAddress`, dll
- **PO**: `po`, `products`, `vat`, `paymentAddress`, `forwarder`, `signed`, `termAndCondition`, dll
- **DO**: `companyInformation`, `doInformation`, `receiver`, `transport`, `detailsTransport`, `additional`, `footer`
- **Invoice**: `companyInformation`, `invoiceInformation`, `products`, `priceSummary`, `paymentInformation`, `signature`, dll

---

## Common Response Format

### Paginated (OL, PO, DO, Invoice)

```json
{ "items": [], "total": 0, "page": 1, "page_size": 20 }
```

### Error 404

```json
{ "detail": "Not found" }
```

### Error Validasi

```json
{
  "detail": [
    { "loc": ["body", "name"], "msg": "field required", "type": "value_error.missing" }
  ]
}
```

### Delete Success

```json
{ "message": "Deleted", "code": 200 }
```

---

## Tech Stack Backend

- **FastAPI** — framework Python
- **SQLAlchemy 2.0** — ORM async
- **aiomysql** — driver MySQL async
- **Pydantic v2** — validasi data
- **OpenAPI** — dokumentasi otomatis (Swagger UI)
