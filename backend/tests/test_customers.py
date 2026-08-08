from starlette.testclient import TestClient


def test_list_customers(client: TestClient, seeded_db):
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_customer_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.get(f"/api/v1/customers/{cust_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "PT Bina Karya"


def test_get_customer_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/customers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_customer(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={
        "name": "PT ABC", "address": "Jl. Test", "phone": "021-9999",
        "email": "abc@email.com"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "PT ABC"
    assert "id" in data


def test_create_customer_with_npwp(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={
        "name": "PT NPWP Test",
        "npwp": "01.234.567.8-901.000",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["npwp"] == "01.234.567.8-901.000"


def test_create_customer_npwp_optional(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={"name": "PT Tanpa NPWP"})
    assert response.status_code == 201
    assert response.json()["npwp"] is None


def test_create_customer_npwp_too_long(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={
        "name": "PT NPWP Panjang",
        "npwp": "12.345.678.9-012.345-EXTRA",
    })
    assert response.status_code == 422


def test_update_customer_npwp(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.put(f"/api/v1/customers/{cust_id}", json={
        "npwp": "99.888.777.6-555.000"
    })
    assert response.status_code == 200
    assert response.json()["npwp"] == "99.888.777.6-555.000"


def test_create_customer_missing_name(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={"address": "Test"})
    assert response.status_code == 422


def test_create_customer_empty_body(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={})
    assert response.status_code == 422


def test_create_customer_extra_fields_ignored(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={
        "name": "PT XYZ", "hacker": True
    })
    assert response.status_code < 500


def test_update_customer(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/customers")
    cust_id = list_resp.json()[0]["id"]
    response = client.put(f"/api/v1/customers/{cust_id}", json={
        "name": "PT Updated"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "PT Updated"


def test_update_customer_not_found(client: TestClient, seeded_db):
    response = client.put("/api/v1/customers/00000000-0000-0000-0000-000000000000",
                          json={"name": "X"})
    assert response.status_code == 404


def test_delete_customer_without_dependencies(client: TestClient, seeded_db):
    response = client.post("/api/v1/customers", json={"name": "Temp"})
    assert response.status_code == 201
    new_id = response.json()["id"]
    response = client.delete(f"/api/v1/customers/{new_id}")
    assert response.status_code == 200
    get_resp = client.get(f"/api/v1/customers/{new_id}")
    assert get_resp.status_code == 404


def test_delete_customer_not_found(client: TestClient, seeded_db):
    response = client.delete("/api/v1/customers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
