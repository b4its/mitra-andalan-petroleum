import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from starlette.testclient import TestClient

from tests.conftest import DB_PATH

sync_engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def _insert_activity(resource_type: str, action: str = "create",
                     actor_name: str = "Ahmad Fauzi", actor_role: str = "admin") -> str:
    now = datetime.now(timezone.utc).isoformat()
    act_id = str(uuid.uuid4())
    with sync_engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO activities (id, user_id, actor_name, actor_role, action,
                resource_type, resource_id, resource_name, created_at, updated_at)
            VALUES (:id, NULL, :actor, :role, :action, :rtype, NULL, NULL, :now, :now)
        """), {
            "id": act_id, "actor": actor_name, "role": actor_role,
            "action": action, "rtype": resource_type, "now": now
        })
    return act_id


def test_list_activities_empty(client: TestClient):
    response = client.get("/api/v1/activities?page=1&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_activities_paginated(client: TestClient, seeded_db):
    _insert_activity("customer")
    _insert_activity("supplier")
    response = client.get("/api/v1/activities?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["page_size"] == 1
    assert len(data["items"]) == 1


def test_list_activities_filter_by_resource_type(client: TestClient, seeded_db):
    _insert_activity("customer", actor_name="Alea Rahmawati")
    _insert_activity("supplier", actor_name="Ahmad Fauzi")
    response = client.get("/api/v1/activities?resource_type=supplier")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["resource_type"] == "supplier"


def test_list_activities_filter_by_action(client: TestClient, seeded_db):
    _insert_activity("customer", action="create")
    _insert_activity("customer", action="delete")
    response = client.get("/api/v1/activities?action=delete")
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_list_resource_types(client: TestClient, seeded_db):
    _insert_activity("customer")
    _insert_activity("purchase_order")
    _insert_activity("customer")
    response = client.get("/api/v1/activities/resource-types")
    assert response.status_code == 200
    assert response.json() == ["customer", "purchase_order"]


def test_list_resource_types_empty(client: TestClient):
    response = client.get("/api/v1/activities/resource-types")
    assert response.status_code == 200
    assert response.json() == []


def test_get_activity_by_id(client: TestClient, seeded_db):
    act_id = _insert_activity("customer")
    response = client.get(f"/api/v1/activities/{act_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == act_id
    assert data["resource_type"] == "customer"


def test_get_activity_not_found(client: TestClient, seeded_db):
    response = client.get("/api/v1/activities/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404