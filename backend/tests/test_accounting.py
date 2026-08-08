from starlette.testclient import TestClient


def _create_account(client: TestClient, code="9-1000", name="Akun Test", type="asset"):
    return client.post("/api/v1/accounting/accounts", json={
        "code": code, "name": name, "type": type
    })


def _create_journal(client: TestClient, cash_id, revenue_id, amount=100000):
    return client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Jurnal test",
        "reference": "TEST/001",
        "status": "posted",
        "lines": [
            {"account_id": cash_id, "debit": amount, "credit": 0},
            {"account_id": revenue_id, "debit": 0, "credit": amount},
        ],
    })


# ── Accounts ───────────────────────────────────────────────────

def test_list_accounts_empty(client: TestClient):
    response = client.get("/api/v1/accounting/accounts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_account(client: TestClient):
    response = _create_account(client)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "9-1000"
    assert data["type"] == "asset"
    assert data["is_active"] is True


def test_create_account_duplicate_code(client: TestClient):
    _create_account(client)
    response = _create_account(client)
    assert response.status_code == 400


def test_create_account_invalid_type(client: TestClient):
    response = client.post("/api/v1/accounting/accounts", json={
        "code": "9-2000", "name": "Salah", "type": "invalid"
    })
    assert response.status_code == 422


def test_get_account_by_id(client: TestClient):
    acc = _create_account(client).json()
    response = client.get(f"/api/v1/accounting/accounts/{acc['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Akun Test"


def test_update_account(client: TestClient):
    acc = _create_account(client).json()
    response = client.put(f"/api/v1/accounting/accounts/{acc['id']}", json={"name": "Akun Diubah"})
    assert response.status_code == 200
    assert response.json()["name"] == "Akun Diubah"


def test_delete_account(client: TestClient):
    acc = _create_account(client).json()
    response = client.delete(f"/api/v1/accounting/accounts/{acc['id']}")
    assert response.status_code == 200


def test_delete_account_in_use(client: TestClient):
    cash = _create_account(client, "9-3000", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4000", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"])
    response = client.delete(f"/api/v1/accounting/accounts/{cash['id']}")
    assert response.status_code == 400


# ── Journal ────────────────────────────────────────────────────

def test_create_journal(client: TestClient):
    cash = _create_account(client, "9-3100", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4100", "Pendapatan Test", "revenue").json()
    response = _create_journal(client, cash["id"], revenue["id"])
    assert response.status_code == 201
    data = response.json()
    assert data["entry_number"].startswith("JRM-")
    assert len(data["lines"]) == 2
    assert data["status"] == "posted"


def test_create_journal_unbalanced(client: TestClient):
    cash = _create_account(client, "9-3200", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4200", "Pendapatan Test", "revenue").json()
    response = client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Tidak balance",
        "lines": [
            {"account_id": cash["id"], "debit": 100000, "credit": 0},
            {"account_id": revenue["id"], "debit": 0, "credit": 50000},
        ],
    })
    assert response.status_code == 422


def test_create_journal_single_line(client: TestClient):
    cash = _create_account(client, "9-3300", "Kas Test", "asset").json()
    response = client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Satu baris",
        "lines": [
            {"account_id": cash["id"], "debit": 100000, "credit": 0},
        ],
    })
    assert response.status_code == 422


def test_create_journal_duplicate_debit_credit(client: TestClient):
    cash = _create_account(client, "9-3400", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4400", "Pendapatan Test", "revenue").json()
    response = client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Debit kredit bersamaan",
        "lines": [
            {"account_id": cash["id"], "debit": 100000, "credit": 100000},
            {"account_id": revenue["id"], "debit": 0, "credit": 100000},
        ],
    })
    assert response.status_code == 422


def test_list_journals(client: TestClient):
    cash = _create_account(client, "9-3500", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4500", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"])
    response = client.get("/api/v1/accounting/journal?page=1&page_size=10")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_journal_by_id(client: TestClient):
    cash = _create_account(client, "9-3600", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4600", "Pendapatan Test", "revenue").json()
    entry = _create_journal(client, cash["id"], revenue["id"]).json()
    response = client.get(f"/api/v1/accounting/journal/{entry['id']}")
    assert response.status_code == 200
    assert len(response.json()["lines"]) == 2


def test_update_journal_lines(client: TestClient):
    cash = _create_account(client, "9-3700", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4700", "Pendapatan Test", "revenue").json()
    expense = _create_account(client, "9-5000", "Beban Test", "expense").json()
    entry = _create_journal(client, cash["id"], revenue["id"]).json()

    response = client.put(f"/api/v1/accounting/journal/{entry['id']}", json={
        "description": "Jurnal diubah",
        "lines": [
            {"account_id": expense["id"], "debit": 50000, "credit": 0},
            {"account_id": cash["id"], "debit": 0, "credit": 50000},
        ],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Jurnal diubah"
    assert len(data["lines"]) == 2


def test_delete_journal(client: TestClient):
    cash = _create_account(client, "9-3800", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4800", "Pendapatan Test", "revenue").json()
    entry = _create_journal(client, cash["id"], revenue["id"]).json()
    response = client.delete(f"/api/v1/accounting/journal/{entry['id']}")
    assert response.status_code == 200


# ── Buku Besar / Ledger ────────────────────────────────────────

def test_ledger_running_balance(client: TestClient):
    cash = _create_account(client, "9-3900", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4900", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)
    _create_journal(client, cash["id"], revenue["id"], 50000)

    response = client.get(f"/api/v1/accounting/ledger?account_id={cash['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["closing_balance"] == 150000
    assert len(data["rows"]) == 2
    assert data["rows"][1]["balance"] == 150000


def test_ledger_revenue_balance(client: TestClient):
    cash = _create_account(client, "9-3901", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4901", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 75000)

    response = client.get(f"/api/v1/accounting/ledger?account_id={revenue['id']}")
    data = response.json()
    assert data["closing_balance"] == 75000


def test_ledger_not_found(client: TestClient):
    response = client.get("/api/v1/accounting/ledger?account_id=00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ── Neraca Saldo ───────────────────────────────────────────────

def test_trial_balance(client: TestClient):
    cash = _create_account(client, "9-3902", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4902", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/trial-balance")
    assert response.status_code == 200
    data = response.json()
    assert round(data["total_debit"], 2) == round(data["total_credit"], 2)
    assert data["total_debit"] >= 100000


# ── Pemasukan & Pengeluaran ────────────────────────────────────

def test_income(client: TestClient):
    cash = _create_account(client, "9-3903", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4903", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 200000)

    response = client.get("/api/v1/accounting/income")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["amount"] == 200000


def test_expenses(client: TestClient):
    cash = _create_account(client, "9-3904", "Kas Test", "asset").json()
    expense = _create_account(client, "9-5004", "Beban Test", "expense").json()
    client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-02",
        "description": "Beban test",
        "lines": [
            {"account_id": expense["id"], "debit": 30000, "credit": 0},
            {"account_id": cash["id"], "debit": 0, "credit": 30000},
        ],
    })

    response = client.get("/api/v1/accounting/expenses")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["items"][0]["amount"] == 30000


def test_income_expense_date_filter(client: TestClient):
    cash = _create_account(client, "9-3905", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4905", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"])

    response = client.get("/api/v1/accounting/income?date_from=2026-08-01&date_to=2026-08-31")
    assert response.status_code == 200
    assert response.json()["total"] == 0


# ── Summary ────────────────────────────────────────────────────

def test_summary(client: TestClient):
    cash = _create_account(client, "9-3906", "Kas Test", "asset").json()
    revenue = _create_account(client, "9-4906", "Pendapatan Test", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_income"] >= 100000
    assert data["total_expense"] >= 0
    assert data["journal_count"] >= 1
    assert data["account_count"] >= 2
    assert len(data["recent_journals"]) >= 1
