from starlette.testclient import TestClient


def test_list_suppliers(client: TestClient, seeded_db):
    response = client.get("/api/v1/suppliers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_supplier_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/suppliers")
    supp_id = list_resp.json()[0]["id"]
    response = client.get(f"/api/v1/suppliers/{supp_id}")
    assert response.status_code == 200


def test_get_supplier_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/suppliers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_supplier(client: TestClient, seeded_db):
    response = client.post("/api/v1/suppliers", json={
        "name": "PT Supplier Baru", "address": "Jl. Baru"
    })
    assert response.status_code == 201


def test_create_supplier_missing_name(client: TestClient, seeded_db):
    response = client.post("/api/v1/suppliers", json={"address": "Test"})
    assert response.status_code == 422


def test_update_supplier(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/suppliers")
    supp_id = list_resp.json()[0]["id"]
    response = client.put(f"/api/v1/suppliers/{supp_id}", json={
        "name": "Updated Supplier"
    })
    assert response.status_code == 200


def test_update_supplier_not_found(client: TestClient, seeded_db):
    response = client.put("/api/v1/suppliers/00000000-0000-0000-0000-000000000000",
                          json={"name": "X"})
    assert response.status_code == 404


def test_delete_supplier(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/suppliers")
    supp_id = list_resp.json()[0]["id"]
    response = client.delete(f"/api/v1/suppliers/{supp_id}")
    assert response.status_code == 200


def test_delete_supplier_not_found(client: TestClient, seeded_db):
    response = client.delete("/api/v1/suppliers/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
