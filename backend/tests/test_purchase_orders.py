from starlette.testclient import TestClient


def test_list_purchase_orders(client: TestClient, seeded_db):
    response = client.get("/api/v1/purchase-orders?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


def test_get_po_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/purchase-orders?page=1&page_size=10")
    po_id = list_resp.json()["items"][0]["id"]
    response = client.get(f"/api/v1/purchase-orders/{po_id}")
    assert response.status_code == 200


def test_get_po_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/purchase-orders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_po_customer(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/purchase-orders", json={
        "po_number": "NEW/PO/001", "type": "customer",
        "customer_id": cust_id, "total": 50000000
    })
    assert response.status_code == 201


def test_create_po_supplier(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/suppliers")
    supp_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/purchase-orders", json={
        "po_number": "NEW/PO/SUP/001", "type": "supplier",
        "supplier_id": supp_id, "total": 45000000
    })
    assert response.status_code == 201


def test_create_po_customer_with_invalid_created_by(client: TestClient, seeded_db):
    """Regresi 500: created_by stale (id user tidak ada) tidak boleh menggagalkan pembuatan PO."""
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/purchase-orders", json={
        "po_number": "STALE/PO/001", "type": "customer",
        "customer_id": cust_id, "total": 1000,
        "created_by": "00000000-0000-0000-0000-000000000000",
    })
    assert response.status_code == 201


def test_create_po_customer_missing_customer_id(client: TestClient, seeded_db):
    response = client.post("/api/v1/purchase-orders", json={
        "po_number": "ERR/PO/001", "type": "customer", "total": 1000
    })
    assert response.status_code in (201, 422)


def test_create_po_supplier_missing_supplier_id(client: TestClient, seeded_db):
    response = client.post("/api/v1/purchase-orders", json={
        "po_number": "ERR/PO/002", "type": "supplier", "total": 1000
    })
    assert response.status_code in (201, 422)


def test_create_po_negative_total(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/purchase-orders", json={
        "po_number": "NEG/PO/001", "type": "customer",
        "customer_id": cust_id, "total": -100
    })
    assert response.status_code in (201, 422)


def test_update_po(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/purchase-orders?page=1&page_size=10")
    po_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/purchase-orders/{po_id}", json={
        "total": 60000000
    })
    assert response.status_code == 200


def test_delete_po(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/purchase-orders?page=1&page_size=10")
    po_id = list_resp.json()["items"][0]["id"]
    response = client.delete(f"/api/v1/purchase-orders/{po_id}")
    assert response.status_code == 200


def test_filter_po_by_type(client: TestClient, seeded_db):
    response = client.get("/api/v1/purchase-orders?type=customer&page=1&page_size=10")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["type"] == "customer"
