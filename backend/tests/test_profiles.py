from starlette.testclient import TestClient


def test_list_profiles(client: TestClient, seeded_db):
    response = client.get("/api/v1/profiles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_profile_by_id(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/profiles")
    user_id = list_resp.json()[0]["id"]
    response = client.get(f"/api/v1/profiles/{user_id}")
    assert response.status_code == 200
    assert "name" in response.json()


def test_get_profile_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/profiles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_profile(client: TestClient, seeded_db):
    response = client.post("/api/v1/profiles", json={
        "name": "New User", "email": "new@email.com",
        "password": "test123", "role": "marketing"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New User"
    assert data["email"] == "new@email.com"
    assert "password" not in data


def test_create_profile_duplicate_email(client: TestClient, seeded_db):
    response = client.post("/api/v1/profiles", json={
        "name": "Duplikat", "email": "admin@mapetroleum.co.id",
        "password": "test123", "role": "admin"
    })
    assert response.status_code == 400


def test_create_profile_missing_password(client: TestClient, seeded_db):
    response = client.post("/api/v1/profiles", json={
        "name": "No Pass", "email": "nopass@email.com"
    })
    assert response.status_code == 422


def test_update_profile(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/profiles")
    user_id = list_resp.json()[0]["id"]
    response = client.put(f"/api/v1/profiles/{user_id}", json={
        "name": "Updated Name"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_delete_profile(client: TestClient, seeded_db):
    list_resp = client.get("/api/v1/profiles")
    user_id = list_resp.json()[-1]["id"]
    response = client.delete(f"/api/v1/profiles/{user_id}")
    assert response.status_code == 200


def test_delete_profile_not_found(client: TestClient, seeded_db):
    response = client.delete("/api/v1/profiles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
