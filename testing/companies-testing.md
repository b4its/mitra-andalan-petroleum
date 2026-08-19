# Companies Feature Testing Guide

## Backend API Tests

All endpoints work correctly:
- ✅ GET /api/v1/companies - List all
- ✅ POST /api/v1/companies - Create new
- ✅ GET /api/v1/companies/{id} - Get single  
- ✅ PUT /api/v1/companies/{id} - Update
- ✅ DELETE /api/v1/companies/{id} - Delete

### Sample Commands:

```bash
# Create company
curl -X POST localhost:8012/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{"name": "PT. Test", "abbreviation": "TST"}'

# Update company  
curl -X PUT localhost:8012/api/v1/companies/<id> \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete company
curl -X DELETE localhost:8012/api/v1/companies/<id>
```

---

## Frontend Verification

### 1. Companies Page (`/admin/companies`)
Features implemented:
- Full CRUD UI
- Search by name/abbreviation
- Pagination (8 items/page)
- Modal for create/edit
- Confirmation for delete
- Image logo support

### 2. Users Page (`/admin/users`)
New feature added:
- Role filter dropdown
- Combined filtering + search

---

## Sample Data Created

1. PT. Mitra Andalan Petroleum (MAP)
2. PT. Pertamina Hulu Energi (PHE)
3. PT. Total E&P Indonesia (TEPI)
4. PT. Medco Power Indonesia (MEDI)
