from starlette.testclient import TestClient

from app.api.v1.endpoints.admin_database import _split_sql, _literal
from datetime import date, datetime, timezone


# ── _split_sql ─────────────────────────────────────────────────

def test_split_sql_strips_comments():
    sql = """-- header comment
/* block comment */
INSERT INTO t (v) VALUES (1);
-- another comment
SELECT 2;"""
    stmts = _split_sql(sql)
    assert stmts == ["INSERT INTO t (v) VALUES (1)", "SELECT 2"]


def test_split_sql_skips_comment_only():
    sql = "-- only a comment\n/* block */\n;\n# another"
    assert _split_sql(sql) == []


def test_split_sql_semicolon_inside_string():
    sql = "INSERT INTO t (v) VALUES ('a;b'); SELECT 1;"
    stmts = _split_sql(sql)
    assert stmts == ["INSERT INTO t (v) VALUES ('a;b')", "SELECT 1"]


def test_split_sql_double_dash_inside_string():
    sql = "INSERT INTO t (v) VALUES ('a -- b'); SELECT 1;"
    stmts = _split_sql(sql)
    assert stmts == ["INSERT INTO t (v) VALUES ('a -- b')", "SELECT 1"]


def test_split_sql_escaped_quote():
    sql = r"INSERT INTO t (v) VALUES ('it\'s'); SELECT 4;"
    stmts = _split_sql(sql)
    assert len(stmts) == 2
    assert stmts[0] == r"INSERT INTO t (v) VALUES ('it\'s')"


def test_split_sql_no_trailing_semicolon():
    assert _split_sql("SELECT 5") == ["SELECT 5"]


# ── _literal ───────────────────────────────────────────────────

def test_literal_timezone_aware_datetime():
    dt = datetime(2026, 8, 8, 12, 4, 8, tzinfo=timezone.utc)
    assert _literal(dt) == "'2026-08-08 12:04:08'"


def test_literal_naive_datetime():
    assert _literal(datetime(2026, 8, 8, 12, 4, 8)) == "'2026-08-08 12:04:08'"


def test_literal_date():
    assert _literal(date(2026, 8, 8)) == "'2026-08-08'"


def test_literal_quote_escaped():
    assert _literal("It's a test") == "'It''s a test'"


def test_literal_backslash_escaped():
    assert _literal(r"C:\temp\file") == r"'C:\\temp\\file'"


def test_literal_types():
    assert _literal(None) == "NULL"
    assert _literal(True) == "1"
    assert _literal(False) == "0"
    assert _literal(42) == "42"
    assert _literal(4.5) == "4.5"
    assert _literal(b"\x01\x02") == "X'0102'"


# ── Export / Import round-trip via API ─────────────────────────

def test_export_returns_sql(client: TestClient, seeded_db):
    response = client.get("/api/v1/admin/database/export")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "INSERT INTO" in content
    assert "DELETE FROM" in content


def test_import_requires_sql_extension(client: TestClient):
    response = client.post(
        "/api/v1/admin/database/import",
        files={"file": ("data.txt", b"SELECT 1;", "text/plain")},
    )
    assert response.status_code == 400


def test_import_rejects_empty(client: TestClient):
    response = client.post(
        "/api/v1/admin/database/import",
        files={"file": ("data.sql", b"", "application/sql")},
    )
    assert response.status_code == 400


def test_import_rejects_comment_only(client: TestClient):
    response = client.post(
        "/api/v1/admin/database/import",
        files={"file": ("data.sql", b"-- hanya komentar\n", "application/sql")},
    )
    assert response.status_code == 400


def test_export_then_import_roundtrip(client: TestClient, seeded_db):
    # Export dulu
    export_resp = client.get("/api/v1/admin/database/export")
    assert export_resp.status_code == 200
    sql_content = export_resp.content

    # Clear
    clear_resp = client.post("/api/v1/admin/database/clear")
    assert clear_resp.status_code == 200

    # Import kembali
    import_resp = client.post(
        "/api/v1/admin/database/import",
        files={"file": ("backup.sql", sql_content, "application/sql")},
    )
    assert import_resp.status_code == 200
    body = import_resp.json()
    assert body["statements"] > 0

    # Verifikasi data bisa dibaca lagi
    customers_resp = client.get("/api/v1/customers")
    assert customers_resp.status_code == 200
    assert len(customers_resp.json()) >= 1


def test_clear_database(client: TestClient, seeded_db):
    response = client.post("/api/v1/admin/database/clear")
    assert response.status_code == 200
    body = response.json()
    assert body["tables"] > 0

    # Data sudah kosong
    customers_resp = client.get("/api/v1/customers")
    assert customers_resp.status_code == 200
    assert customers_resp.json() == []
