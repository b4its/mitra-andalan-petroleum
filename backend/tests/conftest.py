import os
import uuid
from contextlib import asynccontextmanager

import pytest
from sqlalchemy import create_engine, text
from starlette.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:////tmp/test.db"
os.environ["DEBUG"] = "False"

from app.main import app
from app.core.database import Base


@asynccontextmanager
async def noop_lifespan_context(app_):
    yield None


app.router.lifespan_context = noop_lifespan_context

DB_PATH = "/tmp/test.db"
sync_engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=sync_engine)
    tables = _get_table_names()
    with sync_engine.begin() as conn:
        for table in tables:
            conn.execute(text(f"DELETE FROM {table}"))
    yield


def _get_table_names():
    with sync_engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ))
        return [row[0] for row in result]


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def seeded_db(client):
    from passlib.hash import bcrypt
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    ids = {}

    with sync_engine.begin() as conn:
        ids["user_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO users (id, name, email, password, role, created_at, updated_at)
            VALUES (:id, :name, :email, :password, :role, :now, :now)"""),
            {"id": ids["user_id"], "name": "Admin", "email": "admin@email.com",
             "password": bcrypt.hash("admin123"), "role": "admin", "now": now})
        conn.execute(text("""INSERT INTO users (id, name, email, password, role, created_at, updated_at)
            VALUES (:id, :name, :email, :password, :role, :now, :now)"""),
            {"id": str(uuid.uuid4()), "name": "Marketing", "email": "marketing@email.com",
             "password": bcrypt.hash("marketing123"), "role": "marketing", "now": now})

        ids["cust_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO customers (id, name, address, phone, email, created_at, updated_at)
            VALUES (:id, :name, :addr, :phone, :email, :now, :now)"""),
            {"id": ids["cust_id"], "name": "PT Bina Karya", "addr": "Jl. Merdeka No.1",
             "phone": "021-1234", "email": "bina@email.com", "now": now})

        ids["supp_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO suppliers (id, name, address, phone, email, created_at, updated_at)
            VALUES (:id, :name, :addr, :phone, :email, :now, :now)"""),
            {"id": ids["supp_id"], "name": "PT Supplier Logistik", "addr": "Jl. Industri No.2",
             "phone": "021-5678", "email": "supplier@email.com", "now": now})

        ids["ol_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO offering_letters (id, offering_letter_number, customer_id, location,
            date, receiver, fuel_total_price, transport_price, status, created_at, updated_at)
            VALUES (:id, :num, :cid, :loc, :dt, :recv, :ftp, :tp, :st, :now, :now)"""),
            {"id": ids["ol_id"], "num": "001/OL/VI/2025", "cid": ids["cust_id"], "loc": "Jakarta",
             "dt": "2025-06-01", "recv": "PT Bina Karya", "ftp": 50000000, "tp": 2500000,
             "st": "created", "now": now})

        ids["po_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO purchase_orders (id, po_number, type, customer_id, date, total,
            status, created_at, updated_at) VALUES (:id, :num, :type, :cid, :dt, :total, :st, :now, :now)"""),
            {"id": ids["po_id"], "num": "PO/2025/VI/100", "type": "customer", "cid": ids["cust_id"],
             "dt": "2025-06-01", "total": 50000000, "st": "created", "now": now})

        ids["do_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO delivery_orders (id, do_number, customer_id, po_number,
            transport_name, fuel_total, status, status_rilis_dana, status_ready_order,
            status_selesai_dikirim, status_lunas_ongkir, created_at, updated_at)
            VALUES (:id, :num, :cid, :po, :trans, :ft, :st, 0, 0, 0, 0, :now, :now)"""),
            {"id": ids["do_id"], "num": "001/DO/VI/2025", "cid": ids["cust_id"], "po": "PO/2025/VI/100",
             "trans": "PT Express", "ft": 8000, "st": "created", "now": now})

        ids["inv_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO invoices (id, invoice_number, customer_id, terms_day, grand_total,
            invoice_status, deadline_status, created_at, updated_at)
            VALUES (:id, :num, :cid, :terms, :gt, :ist, :dst, :now, :now)"""),
            {"id": ids["inv_id"], "num": "INV/2025/VI/001", "cid": ids["cust_id"], "terms": 30,
             "gt": 50000000, "ist": "unpaid", "dst": "on_time", "now": now})

        ids["notif_id"] = str(uuid.uuid4())
        conn.execute(text("""INSERT INTO notifications (id, title, message, type, is_read, created_at, updated_at)
            VALUES (:id, :title, :msg, :type, :is_read, :now, :now)"""),
            {"id": ids["notif_id"], "title": "Test Notif", "msg": "Test message",
             "type": "info", "is_read": False, "now": now})

    return ids
