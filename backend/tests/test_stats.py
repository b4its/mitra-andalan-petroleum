from starlette.testclient import TestClient


def test_home_stats_structure(client: TestClient, seeded_db):
    response = client.get("/api/v1/stats/home")
    assert response.status_code == 200
    assert "stats" in response.json()


def test_home_stats_has_3_items(client: TestClient, seeded_db):
    response = client.get("/api/v1/stats/home")
    assert len(response.json()["stats"]) == 3


def test_home_stats_zero_values(client: TestClient):
    response = client.get("/api/v1/stats/home")
    assert response.status_code == 200
    for stat in response.json()["stats"]:
        assert stat["value"] == 0 or stat["value"] == "Rp 0"


def test_marketing_stats(client: TestClient, seeded_db):
    response = client.get("/api/v1/stats/marketing")
    assert response.status_code == 200
    assert "stats" in response.json()


def test_operations_stats(client: TestClient, seeded_db):
    response = client.get("/api/v1/stats/operations")
    assert response.status_code == 200
    assert "stats" in response.json()


def test_finance_stats(client: TestClient, seeded_db):
    response = client.get("/api/v1/stats/finance")
    assert response.status_code == 200
    assert "stats" in response.json()
