from starlette.testclient import TestClient


def test_list_notifications(client: TestClient, seeded_db):
    response = client.get("/api/v1/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_notification_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/notifications")
    notif_id = list_resp.json()[0]["id"]
    response = client.get(f"/api/v1/notifications/{notif_id}")
    assert response.status_code == 200


def test_get_notification_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/notifications/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_notification(client: TestClient, seeded_db):
    response = client.post("/api/v1/notifications", json={
        "title": "Test Notification", "message": "This is a test"
    })
    assert response.status_code == 201


def test_create_notification_missing_title(client: TestClient, seeded_db):
    response = client.post("/api/v1/notifications", json={
        "message": "Missing title"
    })
    assert response.status_code == 422


def test_create_notification_missing_message(client: TestClient, seeded_db):
    response = client.post("/api/v1/notifications", json={
        "title": "Missing message"
    })
    assert response.status_code == 422


def test_mark_notification_read(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/notifications")
    notif_id = list_resp.json()[0]["id"]
    response = client.put(f"/api/v1/notifications/{notif_id}", json={
        "is_read": True
    })
    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_delete_notification(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/notifications")
    notif_id = list_resp.json()[0]["id"]
    response = client.delete(f"/api/v1/notifications/{notif_id}")
    assert response.status_code == 200
