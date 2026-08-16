from starlette.testclient import TestClient


def test_login_success(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@mapetroleum.co.id", "password": "admin123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "admin"
    assert "token" in data
    assert "logged_in_at" in data


def test_login_marketing(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "marketing@mapetroleum.co.id", "password": "marketing123"
    })
    assert resp.status_code == 200
    assert resp.json()["role"] == "marketing"


def test_login_wrong_password(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@mapetroleum.co.id", "password": "wrongpass"
    })
    assert resp.status_code == 401


def test_login_email_not_found(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@email.com", "password": "x"
    })
    assert resp.status_code == 401


def test_login_empty_email(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "", "password": "x"
    })
    assert resp.status_code in (401, 422)


def test_login_empty_password(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@mapetroleum.co.id", "password": ""
    })
    assert resp.status_code in (401, 422)


def test_login_empty_body(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 422


def test_login_sql_injection(client: TestClient, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "' OR 1=1--", "password": "x"
    })
    assert resp.status_code in (401, 422)


def test_health(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["message"] == "OK"
