from starlette.testclient import TestClient


def test_list_offering_letters(client: TestClient, seeded_db):
    response = client.get("/api/v1/offering-letters?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


def test_get_offering_letter_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/offering-letters?page=1&page_size=10")
    ol_id = list_resp.json()["items"][0]["id"]
    response = client.get(f"/api/v1/offering-letters/{ol_id}")
    assert response.status_code == 200
    assert response.json()["offering_letter_number"] == "001/OL/VI/2025"


def test_get_offering_letter_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/offering-letters/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_offering_letter(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/offering-letters", json={
        "offering_letter_number": "NEW/OL/001",
        "customer_id": cust_id,
        "location": "Jakarta",
        "fuel_total_price": 50000000,
    })
    assert response.status_code == 201
    assert response.json()["status"] == "created"


def test_create_ol_with_invalid_created_by(client: TestClient, seeded_db):
    """Regresi 500: created_by stale (id user tidak ada) tidak boleh menggagalkan pembuatan OL."""
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/offering-letters", json={
        "offering_letter_number": "STALE/OL/001",
        "customer_id": cust_id,
        "created_by": "00000000-0000-0000-0000-000000000000",
        "details": {"additionalInfo": [{"text": "Info tambahan"}]},
    })
    assert response.status_code == 201


def test_create_ol_missing_number(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/offering-letters", json={
        "customer_id": cust_id
    })
    assert response.status_code == 422


def test_create_ol_invalid_customer(client: TestClient, seeded_db):
    response = client.post("/api/v1/offering-letters", json={
        "offering_letter_number": "INV/OL/001",
        "customer_id": "00000000-0000-0000-0000-000000000000"
    })
    assert response.status_code in (201, 400, 422)


def test_create_ol_negative_price(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/offering-letters", json={
        "offering_letter_number": "NEG/OL/001",
        "customer_id": cust_id,
        "fuel_total_price": -1000
    })
    assert response.status_code in (201, 422)


def test_update_offering_letter(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/offering-letters?page=1&page_size=10")
    ol_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/offering-letters/{ol_id}", json={
        "status": "under_revision"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "under_revision"


def test_update_ol_not_found(client: TestClient, seeded_db):
    response = client.put(
        "/api/v1/offering-letters/00000000-0000-0000-0000-000000000000",
        json={"status": "under_revision"}
    )
    assert response.status_code == 404


def test_delete_offering_letter(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/offering-letters?page=1&page_size=10")
    ol_id = list_resp.json()["items"][0]["id"]
    response = client.delete(f"/api/v1/offering-letters/{ol_id}")
    assert response.status_code == 200


def test_delete_ol_not_found(client: TestClient, seeded_db):
    response = client.delete(
        "/api/v1/offering-letters/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


def test_ol_pagination_out_of_range(client: TestClient, seeded_db):
    response = client.get("/api/v1/offering-letters?page=999&page_size=10")
    assert response.status_code == 200
    assert response.json()["items"] == []
