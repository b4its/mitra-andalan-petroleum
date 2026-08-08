from starlette.testclient import TestClient


def test_list_delivery_orders(client: TestClient, seeded_db):
    response = client.get("/api/v1/delivery-orders?page=1&page_size=10")
    assert response.status_code == 200
    assert "items" in response.json()


def test_get_do_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/delivery-orders?page=1&page_size=10")
    do_id = list_resp.json()["items"][0]["id"]
    response = client.get(f"/api/v1/delivery-orders/{do_id}")
    assert response.status_code == 200


def test_get_do_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/delivery-orders/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_delivery_order(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/delivery-orders", json={
        "do_number": "NEW/DO/001", "customer_id": cust_id,
        "transport_name": "PT Express", "fuel_total": 8000
    })
    assert response.status_code == 201
    assert response.json()["status"] == "created"


def test_create_do_missing_number(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/delivery-orders", json={
        "customer_id": cust_id
    })
    assert response.status_code == 422


def test_create_do_negative_fuel(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.post("/api/v1/delivery-orders", json={
        "do_number": "NEG/DO/001", "customer_id": cust_id, "fuel_total": -100
    })
    assert response.status_code in (201, 422)


def test_update_do(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/delivery-orders?page=1&page_size=10")
    do_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/delivery-orders/{do_id}", json={
        "status": "document_returned"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "document_returned"


def test_update_do_transport(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/delivery-orders?page=1&page_size=10")
    do_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/delivery-orders/{do_id}", json={
        "transport_name": "PT New Express"
    })
    assert response.status_code == 200


def test_delete_do(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/delivery-orders?page=1&page_size=10")
    do_id = list_resp.json()["items"][0]["id"]
    response = client.delete(f"/api/v1/delivery-orders/{do_id}")
    assert response.status_code == 200
