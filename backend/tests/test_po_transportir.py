from starlette.testclient import TestClient


def test_list_po_transportir(client: TestClient, seeded_db):
    response = client.get("/api/v1/po-transportir?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 0


def test_get_po_transportir_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/po-transportir?page=1&page_size=10")
    po_id = list_resp.json()["items"][0]["id"]
    response = client.get(f"/api/v1/po-transportir/{po_id}")
    assert response.status_code == 200
    assert response.json()["id"] == po_id
    # Pastikan field baru ada di response
    assert "id_purchase_order" in response.json()


def test_get_po_transportir_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/po-transportir/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_po_transportir(client: TestClient, seeded_db):
    response = client.post("/api/v1/po-transportir", json={
        "po_number": "199/PO-TRANS/MAP/VI/2026",
        "date": "2026-06-30",
        "pic_person": "Bpk Bambang Nugroho",
        "receiver": "PT Armada Kaltim Sejahtera",
        "total": 4440000,
        "status": "created",
        "details": {
            "products": [
                {"name": "Solar", "qty": 8000, "ratePrice": 500, "totalPrice": 4000000,
                 "loadingDate": "2026-06-30", "unloadingDate": "2026-07-01"}
            ],
            "loadingInformation": "Masbro, Pendingin",
            "discharge": "Site MHU",
            "offeror": {"name": "Nico Pratama"}
        }
    })
    assert response.status_code == 201
    data = response.json()
    assert data["po_number"] == "199/PO-TRANS/MAP/VI/2026"
    assert data["status"] == "created"
    assert data["details"]["products"][0]["qty"] == 8000
    assert "id" in data


def test_create_po_transportir_missing_number(client: TestClient, seeded_db):
    response = client.post("/api/v1/po-transportir", json={
        "receiver": "PT Armada Kaltim Sejahtera"
    })
    assert response.status_code == 422


def test_create_po_transportir_stale_created_by(client: TestClient, seeded_db):
    response = client.post("/api/v1/po-transportir", json={
        "po_number": "200/PO-TRANS/MAP/VI/2026",
        "date": "2026-06-30",
        "pic_person": "Bpk Bambang Nugroho",
        "receiver": "PT Armada Kaltim Sejahtera",
        "total": 4440000,
        "status": "created",
        "created_by": "00000000-0000-0000-0000-000000000000",
        "details": {"products": [], "offeror": {"name": "Nico Pratama"}}
    })
    assert response.status_code == 201
    data = response.json()
    assert data["po_number"] == "200/PO-TRANS/MAP/VI/2026"
    assert data["created_by"] is None


def test_update_po_transportir(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/po-transportir?page=1&page_size=10")
    po_id = list_resp.json()["items"][0]["id"]
    response = client.put(f"/api/v1/po-transportir/{po_id}", json={
        "status": "document_returned",
        "total": 5000000
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "document_returned"
    assert body["total"] == 5000000


def test_delete_po_transportir(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/po-transportir?page=1&page_size=10")
    po_id = list_resp.json()["items"][0]["id"]
    response = client.delete(f"/api/v1/po-transportir/{po_id}")
    assert response.status_code == 200
    get_resp = client.get(f"/api/v1/po-transportir/{po_id}")
    assert get_resp.status_code == 404


def test_list_po_transportir_search(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/po-transportir?page=1&page_size=10")
    po_number = list_resp.json()["items"][0]["po_number"]
    response = client.get("/api/v1/po-transportir?search=" + po_number)
    assert response.status_code == 200
    assert response.json()["total"] >= 1