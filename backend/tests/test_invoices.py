from starlette.testclient import TestClient


def test_list_invoices(client: TestClient, seeded_db):
    response = client.get("/api/v1/invoices?page=1&page_size=10")
    assert response.status_code == 200
    assert "items" in response.json()


def test_get_invoice_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/invoices?page=1&page_size=10")
    inv_id = list_resp.json()["items"][0]["id"]
    response = client.get(f"/api/v1/invoices/{inv_id}")
    assert response.status_code == 200
    assert response.json()["invoice_number"] == "INV/2025/VI/001"


def test_get_invoice_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/invoices/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_invoice(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/invoices", json={
        "invoice_number": "NEW/INV/001", "customer_id": cust_id,
        "terms_day": 30, "grand_total": 75000000
    })
    assert response.status_code == 201
    data = response.json()
    assert data["invoice_status"] == "unpaid"
    assert data["deadline_status"] == "on_time"


def test_create_invoice_missing_number(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/invoices", json={
        "customer_id": cust_id, "grand_total": 50000
    })
    assert response.status_code == 422


def test_create_invoice_negative_total(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/invoices", json={
        "invoice_number": "NEG/INV/001", "customer_id": cust_id,
        "grand_total": -1, "terms_day": 30
    })
    assert response.status_code in (201, 422)


def test_create_invoice_zero_terms(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/invoices", json={
        "invoice_number": "ZER/INV/001", "customer_id": cust_id,
        "terms_day": 0, "grand_total": 50000
    })
    assert response.status_code in (201, 422)


def test_update_invoice_status(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/invoices?page=1&page_size=10")
    inv_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/invoices/{inv_id}", json={
        "invoice_status": "paid"
    })
    assert response.status_code == 200
    assert response.json()["invoice_status"] == "paid"


def test_update_invoice_overdue(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/invoices?page=1&page_size=10")
    inv_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/invoices/{inv_id}", json={
        "invoice_status": "overdue"
    })
    assert response.status_code == 200


def test_update_invoice_total(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/invoices?page=1&page_size=10")
    inv_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/invoices/{inv_id}", json={
        "grand_total": 100000000
    })
    assert response.status_code == 200


def test_delete_invoice(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/invoices?page=1&page_size=10")
    inv_id = list_resp.json()["items"][0]["id"]
    response = client.delete(f"/api/v1/invoices/{inv_id}")
    assert response.status_code == 200
