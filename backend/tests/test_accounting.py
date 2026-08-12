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


# ── Neraca (Balance Sheet) ──────────────────────────────────────

def test_balance_sheet_returns_structure(client: TestClient):
    """Neraca mengembalikan section assets, liabilities, equity."""
    cash = _create_account(client, "9-6000", "Kas Test BS", "asset").json()
    revenue = _create_account(client, "9-6001", "Pendapatan Test BS", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 250000)

    response = client.get("/api/v1/accounting/balance-sheet")
    assert response.status_code == 200
    data = response.json()
    assert "assets" in data
    assert "liabilities" in data
    assert "equity" in data
    assert data["total_assets"] >= 250000
    assert isinstance(data["assets"]["accounts"], list)
    assert isinstance(data["liabilities"]["accounts"], list)
    assert isinstance(data["equity"]["accounts"], list)


def test_balance_sheet_empty_db(client: TestClient):
    """Neraca dengan DB kosong mengembalikan semua 0."""
    response = client.get("/api/v1/accounting/balance-sheet")
    assert response.status_code == 200
    data = response.json()
    assert data["total_assets"] == 0
    assert data["total_liabilities"] == 0
    assert data["total_equity"] == 0


def test_balance_sheet_date_filter(client: TestClient):
    """Filter tanggal pada neraca."""
    cash = _create_account(client, "9-6002", "Kas Test BS2", "asset").json()
    revenue = _create_account(client, "9-6003", "Pendapatan Test BS2", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    # Filter di luar periode
    response = client.get("/api/v1/accounting/balance-sheet?date_from=2025-01-01&date_to=2025-01-31")
    assert response.status_code == 200
    data = response.json()
    assert data["total_assets"] == 0

    # Filter di dalam periode
    response = client.get("/api/v1/accounting/balance-sheet?date_from=2026-07-01&date_to=2026-07-31")
    assert response.status_code == 200
    data = response.json()
    assert data["total_assets"] >= 100000


# ── Rekap Cashflow ─────────────────────────────────────────────

def test_cashflow_returns_structure(client: TestClient):
    """Cashflow mengembalikan operating, investing, financing."""
    cash = _create_account(client, "9-6100", "Kas Test CF", "asset").json()
    revenue = _create_account(client, "9-6101", "Pendapatan Test CF", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 500000)

    response = client.get("/api/v1/accounting/cashflow")
    assert response.status_code == 200
    data = response.json()
    assert "operating" in data
    assert "investing" in data
    assert "financing" in data
    assert "net_cashflow" in data
    assert "opening_balance" in data
    assert "closing_balance" in data
    assert len(data["operating"]["items"]) >= 1


def test_cashflow_net_cashflow(client: TestClient):
    """Net cashflow = closing - opening."""
    cash = _create_account(client, "9-6102", "Kas Test CF2", "asset").json()
    revenue = _create_account(client, "9-6103", "Pendapatan Test CF2", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/cashflow")
    assert response.status_code == 200
    data = response.json()
    assert data["net_cashflow"] == data["closing_balance"] - data["opening_balance"]


def test_cashflow_date_filter(client: TestClient):
    """Filter tanggal pada cashflow."""
    cash = _create_account(client, "9-6104", "Kas Test CF3", "asset").json()
    revenue = _create_account(client, "9-6105", "Pendapatan Test CF3", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/cashflow?date_from=2025-01-01&date_to=2025-01-31")
    assert response.status_code == 200
    data = response.json()
    assert data["net_cashflow"] == 0


# ── Rekap Biaya (Cost Recap) ───────────────────────────────────

def test_cost_recap_returns_groups(client: TestClient):
    """Cost recap mengelompokkan biaya per akun."""
    cash = _create_account(client, "9-6200", "Kas Test CR", "asset").json()
    expense = _create_account(client, "9-6201", "Beban Test CR", "expense").json()
    client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Beban test CR",
        "lines": [
            {"account_id": expense["id"], "debit": 75000, "credit": 0},
            {"account_id": cash["id"], "debit": 0, "credit": 75000},
        ],
    })

    response = client.get("/api/v1/accounting/cost-recap")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cost"] >= 75000
    assert len(data["groups"]) >= 1
    # Cek struktur group
    group = data["groups"][0]
    assert "account_code" in group
    assert "account_name" in group
    assert "total" in group
    assert "items" in group
    assert len(group["items"]) >= 1


def test_cost_recap_empty(client: TestClient):
    """Cost recap dengan DB kosong."""
    response = client.get("/api/v1/accounting/cost-recap")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cost"] == 0
    assert len(data["groups"]) == 0


def test_cost_recap_date_filter(client: TestClient):
    """Filter tanggal pada cost recap."""
    cash = _create_account(client, "9-6202", "Kas Test CR2", "asset").json()
    expense = _create_account(client, "9-6203", "Beban Test CR2", "expense").json()
    client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Beban test CR2",
        "lines": [
            {"account_id": expense["id"], "debit": 50000, "credit": 0},
            {"account_id": cash["id"], "debit": 0, "credit": 50000},
        ],
    })

    response = client.get("/api/v1/accounting/cost-recap?date_from=2026-08-01&date_to=2026-08-31")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cost"] == 0


# ── Rekap Monitoring ───────────────────────────────────────────

def test_monitoring_returns_rows(client: TestClient):
    """Monitoring mengembalikan data bulanan."""
    cash = _create_account(client, "9-6300", "Kas Test MON", "asset").json()
    revenue = _create_account(client, "9-6301", "Pendapatan Test MON", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/monitoring?year=2026")
    assert response.status_code == 200
    data = response.json()
    assert "rows" in data
    assert "total_penghasilan" in data
    assert "total_operasional" in data
    assert "total_gross_margin" in data
    assert data["total_penghasilan"] >= 100000


def test_monitoring_row_structure(client: TestClient):
    """Setiap row monitoring memiliki field yang benar."""
    cash = _create_account(client, "9-6302", "Kas Test MON2", "asset").json()
    revenue = _create_account(client, "9-6303", "Pendapatan Test MON2", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/monitoring?year=2026")
    data = response.json()
    if data["rows"]:
        row = data["rows"][0]
        assert "bulan" in row
        assert "modal_elnusa" in row
        assert "oat" in row
        assert "gross_margin" in row
        assert "penghasilan" in row
        assert "fee_manajemen" in row


def test_monitoring_no_data_year(client: TestClient):
    """Monitoring periode tanpa data mengembalikan rows kosong."""
    cash = _create_account(client, "9-6304", "Kas Test MON3", "asset").json()
    revenue = _create_account(client, "9-6305", "Pendapatan Test MON3", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    response = client.get("/api/v1/accounting/monitoring?date_from=2020-01-01&date_to=2020-12-31")
    assert response.status_code == 200
    data = response.json()
    # Menampilkan 12 bulan (semua 0)
    assert len(data["rows"]) == 12
    assert data["total_penghasilan"] == 0


# ── Kas Harian (Daily Cash) ────────────────────────────────────

def test_daily_cash_returns_mutations(client: TestClient):
    """Kas harian menampilkan mutasi debit/kredit."""
    cash = _create_account(client, "9-6400", "Kas Test DC", "asset").json()
    revenue = _create_account(client, "9-6401", "Pendapatan Test DC", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    # Pastikan akun kas terdaftar sebagai 'Kas%'
    # Update nama akun jadi 'Kas Test DC' yang mengandung 'Kas'
    client.put(f"/api/v1/accounting/accounts/{cash['id']}", json={"name": "Kas Test DC"})

    response = client.get("/api/v1/accounting/daily-cash")
    assert response.status_code == 200
    data = response.json()
    assert "opening_balance" in data
    assert "closing_balance" in data
    assert "total_debit" in data
    assert "total_credit" in data
    assert "rows" in data


def test_daily_cash_running_balance(client: TestClient):
    """Saldo berjalan pada kas harian."""
    cash = _create_account(client, "9-6402", "Kas Test DC2", "asset").json()
    revenue = _create_account(client, "9-6403", "Pendapatan Test DC2", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)
    _create_journal(client, cash["id"], revenue["id"], 50000)

    client.put(f"/api/v1/accounting/accounts/{cash['id']}", json={"name": "Kas Test DC2"})

    response = client.get("/api/v1/accounting/daily-cash")
    assert response.status_code == 200
    data = response.json()
    if data["rows"]:
        assert data["rows"][-1]["balance"] == data["closing_balance"]


def test_daily_cash_date_filter(client: TestClient):
    """Filter tanggal pada kas harian."""
    cash = _create_account(client, "9-6404", "Kas Test DC3", "asset").json()
    revenue = _create_account(client, "9-6405", "Pendapatan Test DC3", "revenue").json()
    _create_journal(client, cash["id"], revenue["id"], 100000)

    client.put(f"/api/v1/accounting/accounts/{cash['id']}", json={"name": "Kas Test DC3"})

    response = client.get("/api/v1/accounting/daily-cash?date_from=2025-01-01&date_to=2025-01-31")
    assert response.status_code == 200
    data = response.json()
    assert data["total_debit"] == 0


# ── Rekap Bunga Bank ───────────────────────────────────────────

def test_bank_interest_returns_structure(client: TestClient):
    """Bank interest mengembalikan data pinjaman dan bunga."""
    # Buat akun pinjaman (liability with 'Pinjaman' in name)
    loan = client.post("/api/v1/accounting/accounts", json={
        "code": "9-6500", "name": "Pinjaman Bank Test", "type": "liability"
    }).json()
    cash = _create_account(client, "9-6501", "Kas Test BI", "asset").json()

    # Catat penerimaan pinjaman
    client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Penerimaan pinjaman bank",
        "reference": "LOAN/001",
        "lines": [
            {"account_id": cash["id"], "debit": 100000000, "credit": 0},
            {"account_id": loan["id"], "debit": 0, "credit": 100000000},
        ],
    })

    response = client.get("/api/v1/accounting/bank-interest")
    assert response.status_code == 200
    data = response.json()
    assert "total_principal" in data
    assert "total_interest" in data
    assert "total_paid" in data
    assert "rows" in data
    assert data["total_principal"] >= 100000000


def test_bank_interest_empty(client: TestClient):
    """Bank interest tanpa data."""
    response = client.get("/api/v1/accounting/bank-interest")
    assert response.status_code == 200
    data = response.json()
    assert data["total_principal"] == 0
    assert data["total_interest"] == 0
    assert len(data["rows"]) == 0


def test_bank_interest_with_interest_expense(client: TestClient):
    """Bank interest dengan pembayaran bunga."""
    loan = client.post("/api/v1/accounting/accounts", json={
        "code": "9-6502", "name": "Pinjaman Bank BI2", "type": "liability"
    }).json()
    interest_expense = client.post("/api/v1/accounting/accounts", json={
        "code": "9-6503", "name": "Bunga Pinjaman BI2", "type": "expense"
    }).json()
    cash = _create_account(client, "9-6504", "Kas Test BI2", "asset").json()

    # Pinjaman
    client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-07-01",
        "description": "Pinjaman bank",
        "lines": [
            {"account_id": cash["id"], "debit": 50000000, "credit": 0},
            {"account_id": loan["id"], "debit": 0, "credit": 50000000},
        ],
    })

    # Bayar bunga
    client.post("/api/v1/accounting/journal", json={
        "entry_date": "2026-08-01",
        "description": "Pembayaran bunga bank",
        "lines": [
            {"account_id": interest_expense["id"], "debit": 250000, "credit": 0},
            {"account_id": cash["id"], "debit": 0, "credit": 250000},
        ],
    })

    response = client.get("/api/v1/accounting/bank-interest")
    assert response.status_code == 200
    data = response.json()
    assert data["total_principal"] >= 50000000
    assert data["total_paid"] >= 250000
