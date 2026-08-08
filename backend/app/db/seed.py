from datetime import date

from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.offering_letter import OfferingLetter
from app.models.purchase_order import PurchaseOrder
from app.models.delivery_order import DeliveryOrder
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.models.sale import Sale
from app.models.accounting import Account, JournalEntry, JournalLine


async def seed_database(db: AsyncSession):
    await _seed_users(db)
    await _seed_customers(db)
    await _seed_suppliers(db)
    await _seed_offering_letters(db)
    await _seed_purchase_orders(db)
    await _seed_delivery_orders(db)
    await _seed_invoices(db)
    await _seed_notifications(db)
    await _seed_sales(db)
    await _seed_accounting(db)
    await db.commit()


async def _seed_users(db: AsyncSession):
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        existing_accounting = await db.execute(select(User).where(User.email == "accounting@email.com"))
        if existing_accounting.scalar_one_or_none():
            return
        db.add(User(name="Rina", email="accounting@email.com", password=bcrypt.hash("accounting123"), role="accounting"))
        await db.flush()
        return

    users = [
        User(name="Admin", email="admin@email.com", password=bcrypt.hash("admin123"), role="admin"),
        User(name="Baits", email="ops@email.com", password=bcrypt.hash("ops123"), role="operations"),
        User(name="Nico", email="marketing@email.com", password=bcrypt.hash("marketing123"), role="marketing"),
        User(name="Alea", email="finance@email.com", password=bcrypt.hash("finance123"), role="finance"),
        User(name="Rina", email="accounting@email.com", password=bcrypt.hash("accounting123"), role="accounting"),
    ]
    for u in users:
        db.add(u)
    await db.flush()


async def _seed_customers(db: AsyncSession):
    result = await db.execute(select(Customer).limit(1))
    if result.scalar_one_or_none():
        return

    customers = [
        Customer(name="PT. Bina Karya Sentosa"),
        Customer(name="CV. Maju Jaya Abadi"),
        Customer(name="PT. Sumber Rejeki Mandiri"),
    ]
    for c in customers:
        db.add(c)
    await db.flush()


async def _seed_suppliers(db: AsyncSession):
    result = await db.execute(select(Supplier).limit(1))
    if result.scalar_one_or_none():
        return

    suppliers = [
        Supplier(name="PT. Supplier Logistik Mandiri"),
        Supplier(name="CV. Bahan Bakar Utama"),
    ]
    for s in suppliers:
        db.add(s)
    await db.flush()


async def _seed_offering_letters(db: AsyncSession):
    result = await db.execute(select(OfferingLetter).limit(1))
    if result.scalar_one_or_none():
        return

    customers = (await db.execute(select(Customer))).scalars().all()
    users = (await db.execute(select(User).where(User.role == "marketing"))).scalars().all()
    ol_numbers = ["001/OL/VI/2025", "002/OL/VI/2025", "003/OL/VI/2025", "004/OL/VI/2025"]

    for i in range(15):
        customer = customers[i % len(customers)]
        creator = users[i % len(users)] if users else None
        ol = OfferingLetter(
            offering_letter_number=ol_numbers[i % len(ol_numbers)],
            customer_id=customer.id,
            location="Samarinda",
            date="2025-06-01",
            regarding="Penawaran BBM Solar Industri",
            receiver=customer.name,
            fuel_total_price=50000000 + (i * 1000000),
            transport_price=2500000 + (i * 100000),
            status=["created", "under_revision", "po_received"][i % 3],
            created_by=creator.id if creator else None,
        )
        db.add(ol)
    await db.flush()


async def _seed_purchase_orders(db: AsyncSession):
    result = await db.execute(select(PurchaseOrder).limit(1))
    if result.scalar_one_or_none():
        return

    customers = (await db.execute(select(Customer))).scalars().all()
    suppliers = (await db.execute(select(Supplier))).scalars().all()
    users = (await db.execute(select(User).where(User.role == "marketing"))).scalars().all()

    for i in range(5):
        creator = users[i % len(users)] if users else None
        po = PurchaseOrder(
            po_number=f"PO/2025/VI/{100 + i}",
            type="customer",
            customer_id=customers[i % len(customers)].id,
            date="2025-06-01",
            total=50000000,
            status="created",
            created_by=creator.id if creator else None,
        )
        db.add(po)

    for i in range(5):
        creator = users[i % len(users)] if users else None
        po = PurchaseOrder(
            po_number=f"PO-SUP/2025/VI/{100 + i}",
            type="supplier",
            supplier_id=suppliers[i % len(suppliers)].id,
            date="2025-06-01",
            total=45000000,
            status="created",
            created_by=creator.id if creator else None,
        )
        db.add(po)
    await db.flush()


async def _seed_delivery_orders(db: AsyncSession):
    result = await db.execute(select(DeliveryOrder).limit(1))
    if result.scalar_one_or_none():
        return

    customers = (await db.execute(select(Customer))).scalars().all()
    users = (await db.execute(select(User).where(User.role == "operations"))).scalars().all()
    do_numbers = ["001/DO/VI/2025", "002/DO/VI/2025", "003/DO/VI/2025", "004/DO/VI/2025"]
    po_numbers = ["PO/2025/VI/100", "PO/2025/VI/101", "PO/2025/VI/102"]
    transports = ["PT. Transport Logistik", "CV. Angkutan Cepat", "PT. Distribusi Mandiri"]

    for i in range(15):
        creator = users[i % len(users)] if users else None
        do = DeliveryOrder(
            do_number=do_numbers[i % len(do_numbers)],
            customer_id=customers[i % len(customers)].id,
            po_number=po_numbers[i % len(po_numbers)],
            transport_name=transports[i % len(transports)],
            fuel_total=8000 + (i * 500),
            status=["created", "document_returned"][i % 2],
            created_by=creator.id if creator else None,
        )
        db.add(do)
    await db.flush()


async def _seed_invoices(db: AsyncSession):
    result = await db.execute(select(Invoice).limit(1))
    if result.scalar_one_or_none():
        return

    customers = (await db.execute(select(Customer))).scalars().all()
    inv_numbers = ["INV/2025/VI/001", "INV/2025/VI/002", "INV/2025/VI/003", "INV/2025/VI/004", "INV/2025/VI/005"]
    statuses = ["unpaid", "paid", "overdue"]
    deadlines = ["on_time", "overdue", "due_soon"]

    for i in range(15):
        inv = Invoice(
            invoice_number=inv_numbers[i % len(inv_numbers)],
            customer_id=customers[i % len(customers)].id,
            terms_day=30,
            grand_total=50000000 + (i * 2500000),
            invoice_status=statuses[i % 3],
            deadline_status=deadlines[i % 3],
        )
        db.add(inv)
    await db.flush()


async def _seed_notifications(db: AsyncSession):
    result = await db.execute(select(Notification).limit(1))
    if result.scalar_one_or_none():
        return

    users = {u.role: u for u in (await db.execute(select(User))).scalars().all()}
    marketing_user = users.get("marketing")
    ops_user = users.get("operations")
    finance_user = users.get("finance")

    notifications = [
        Notification(title="PO Baru Masuk", message="Purchase Order baru dari PT. Bina Karya Sentosa telah masuk.", type="info", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=True),
        Notification(title="Invoice Jatuh Tempo", message="Invoice INV/2025/VI/001 akan jatuh tempo dalam 3 hari.", type="warning", sender_id=finance_user.id if finance_user else None, to="/finance/invoice/data-invoice-customer", is_read=True),
        Notification(title="DO Selesai", message="Delivery Order 001/DO/VI/2025 telah selesai diproses.", type="success", sender_id=ops_user.id if ops_user else None, to="/operations", is_read=True),
        Notification(title="Revisi Surat Penawaran", message="Surat penawaran 002/OL/VI/2025 memerlukan revisi.", type="error", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=True),
        Notification(title="Penawaran Baru", message="Surat penawaran 003/OL/VI/2025 berhasil dibuat oleh tim marketing.", type="info", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=False),
        Notification(title="PO Supplier Dibuat", message="Purchase Order ke PT. Supplier Logistik Mandiri berhasil dibuat.", type="success", sender_id=marketing_user.id if marketing_user else None, to="/marketing/supplier", is_read=False),
    ]
    for n in notifications:
        db.add(n)
    await db.flush()


async def _seed_sales(db: AsyncSession):
    result = await db.execute(select(Sale).limit(1))
    if result.scalar_one_or_none():
        return

    emails = ["admin@email.com", "marketing@email.com", "finance@email.com", "ops@email.com", "user@email.com"]
    statuses = ["paid", "failed", "refunded"]

    for i in range(5):
        sale = Sale(
            date="2025-06-01",
            status=statuses[i % 3],
            email=emails[i % len(emails)],
            amount=25000000 + (i * 5000000),
        )
        db.add(sale)
    await db.flush()


ACCOUNT_GROUPS = {
    "asset": [
        ("1-1000", "Kas Besar", "Kas tunai di kantor"),
        ("1-1010", "Kas Kecil", "Kas untuk pengeluaran harian"),
        ("1-1100", "Bank BCA", "Rekening giro Bank BCA"),
        ("1-1200", "Piutang Usaha", "Piutang dari pelanggan"),
        ("1-1300", "Persediaan BBM", "Persediaan bahan bakar minyak"),
        ("1-1400", "Peralatan Kantor", "Peralatan dan inventaris kantor"),
    ],
    "liability": [
        ("2-1000", "Hutang Usaha", "Hutang kepada supplier"),
        ("2-1100", "Hutang Pajak", "Hutang PPN / pajak"),
        ("2-1200", "Hutang Gaji", "Hutang gaji karyawan"),
    ],
    "equity": [
        ("3-1000", "Modal", "Modal pemilik"),
        ("3-1100", "Prive", "Penarikan pribadi pemilik"),
        ("3-1200", "Laba Ditahan", "Laba yang ditahan perusahaan"),
    ],
    "revenue": [
        ("4-1000", "Pendapatan Penjualan BBM", "Pendapatan dari penjualan BBM"),
        ("4-1100", "Pendapatan Jasa Angkut", "Pendapatan dari jasa transportasi"),
        ("4-1200", "Pendapatan Lain-lain", "Pendapatan di luar usaha utama"),
    ],
    "expense": [
        ("5-1000", "Beban Operasional", "Beban operasional umum"),
        ("5-1010", "Beban Transportasi", "Beban transportasi & ongkir"),
        ("5-1020", "Beban Gaji", "Beban gaji karyawan"),
        ("5-1030", "Beban Listrik & Air", "Beban utilitas"),
        ("5-1040", "Beban Pemasaran", "Beban promosi dan pemasaran"),
        ("5-1050", "Beban Perawatan", "Beban perawatan kendaraan/alat"),
    ],
}


async def _seed_accounting(db: AsyncSession):
    result = await db.execute(select(Account).limit(1))
    if result.scalar_one_or_none():
        return

    accounts: dict[str, Account] = {}
    for acc_type, items in ACCOUNT_GROUPS.items():
        for code, name, desc in items:
            acc = Account(code=code, name=name, type=acc_type, description=desc)
            db.add(acc)
            accounts[code] = acc
    await db.flush()

    journal_result = await db.execute(select(JournalEntry).limit(1))
    if journal_result.scalar_one_or_none():
        return

    kas = accounts["1-1000"]
    bank = accounts["1-1100"]
    piutang = accounts["1-1200"]
    pendapatan = accounts["4-1000"]
    ongkir = accounts["4-1100"]
    beban_transport = accounts["5-1010"]
    beban_operasional = accounts["5-1000"]

    entries = [
        {
            "entry_number": "JRM-202606-0001",
            "entry_date": date(2026, 6, 5),
            "description": "Penjualan BBM tunai ke PT. Bina Karya Sentosa",
            "reference": "INV/2026/VI/001",
            "lines": [
                (kas, None, 50000000, 0),
                (pendapatan, None, 0, 50000000),
            ],
        },
        {
            "entry_number": "JRM-202606-0002",
            "entry_date": date(2026, 6, 10),
            "description": "Penjualan BBM kredit ke CV. Maju Jaya Abadi",
            "reference": "INV/2026/VI/002",
            "lines": [
                (piutang, None, 75000000, 0),
                (pendapatan, None, 0, 75000000),
            ],
        },
        {
            "entry_number": "JRM-202606-0003",
            "entry_date": date(2026, 6, 15),
            "description": "Pembayaran jasa angkut transportir",
            "reference": "DO/2026/VI/003",
            "lines": [
                (beban_transport, None, 2500000, 0),
                (kas, None, 0, 2500000),
            ],
        },
        {
            "entry_number": "JRM-202606-0004",
            "entry_date": date(2026, 6, 20),
            "description": "Penerimaan pembayaran piutang dari CV. Maju Jaya Abadi",
            "reference": "PAY/2026/VI/004",
            "lines": [
                (bank, None, 75000000, 0),
                (piutang, None, 0, 75000000),
            ],
        },
        {
            "entry_number": "JRM-202606-0005",
            "entry_date": date(2026, 6, 25),
            "description": "Pembayaran beban operasional bulan Juni",
            "reference": "EXP/2026/VI/005",
            "lines": [
                (beban_operasional, None, 8000000, 0),
                (kas, None, 0, 8000000),
            ],
        },
        {
            "entry_number": "JRM-202606-0006",
            "entry_date": date(2026, 6, 28),
            "description": "Pendapatan jasa angkut diterima tunai",
            "reference": "TR/2026/VI/006",
            "lines": [
                (kas, None, 5000000, 0),
                (ongkir, None, 0, 5000000),
            ],
        },
    ]

    for e in entries:
        entry = JournalEntry(
            entry_number=e["entry_number"],
            entry_date=e["entry_date"],
            description=e["description"],
            reference=e["reference"],
            status="posted",
        )
        db.add(entry)
        await db.flush()
        for account, memo, debit, credit in e["lines"]:
            db.add(JournalLine(
                journal_entry_id=entry.id,
                account_id=account.id,
                description=memo,
                debit=debit,
                credit=credit,
            ))
    await db.flush()
