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
    await db.commit()


async def _seed_users(db: AsyncSession):
    result = await db.execute(select(User).limit(1))
    if result.scalar_one_or_none():
        return

    users = [
        User(name="Admin", email="admin@email.com", password="admin123", role="admin"),
        User(name="Baits", email="ops@email.com", password="ops123", role="operations"),
        User(name="Nico", email="marketing@email.com", password="marketing123", role="marketing"),
        User(name="Alea", email="finance@email.com", password="finance123", role="finance"),
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
    ol_numbers = ["001/OL/VI/2025", "002/OL/VI/2025", "003/OL/VI/2025", "004/OL/VI/2025"]

    letters = []
    for i in range(15):
        customer = customers[i % len(customers)]
        ol = OfferingLetter(
            offering_letter_number=ol_numbers[i % len(ol_numbers)],
            customer_id=customer.id,
            location="Jakarta",
            date="2025-06-01",
            regarding="Penawaran BBM Solar Industri",
            receiver=customer.name,
            fuel_total_price=50000000 + (i * 1000000),
            transport_price=2500000 + (i * 100000),
            status=["created", "under_revision", "po_received"][i % 3],
        )
        letters.append(ol)
    for l in letters:
        db.add(l)
    await db.flush()


async def _seed_purchase_orders(db: AsyncSession):
    result = await db.execute(select(PurchaseOrder).limit(1))
    if result.scalar_one_or_none():
        return

    customers = (await db.execute(select(Customer))).scalars().all()
    suppliers = (await db.execute(select(Supplier))).scalars().all()

    for i in range(5):
        po = PurchaseOrder(
            po_number=f"PO/2025/VI/{100 + i}",
            type="customer",
            customer_id=customers[i % len(customers)].id,
            date="2025-06-01",
            total=50000000,
            status="created",
        )
        db.add(po)

    for i in range(5):
        po = PurchaseOrder(
            po_number=f"PO-SUP/2025/VI/{100 + i}",
            type="supplier",
            supplier_id=suppliers[i % len(suppliers)].id,
            date="2025-06-01",
            total=45000000,
            status="created",
        )
        db.add(po)
    await db.flush()


async def _seed_delivery_orders(db: AsyncSession):
    result = await db.execute(select(DeliveryOrder).limit(1))
    if result.scalar_one_or_none():
        return

    customers = (await db.execute(select(Customer))).scalars().all()
    do_numbers = ["001/DO/VI/2025", "002/DO/VI/2025", "003/DO/VI/2025", "004/DO/VI/2025"]
    po_numbers = ["PO/2025/VI/100", "PO/2025/VI/101", "PO/2025/VI/102"]
    transports = ["PT. Transport Logistik", "CV. Angkutan Cepat", "PT. Distribusi Mandiri"]

    for i in range(15):
        do = DeliveryOrder(
            do_number=do_numbers[i % len(do_numbers)],
            customer_id=customers[i % len(customers)].id,
            po_number=po_numbers[i % len(po_numbers)],
            transport_name=transports[i % len(transports)],
            fuel_total=8000 + (i * 500),
            status=["created", "document_returned"][i % 2],
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

    notifications = [
        Notification(title="PO Baru Masuk", message="Purchase Order baru dari PT. Bina Karya Sentosa telah masuk.", type="info", to="/marketing/customer", is_read=True),
        Notification(title="Invoice Jatuh Tempo", message="Invoice INV/2025/VI/001 akan jatuh tempo dalam 3 hari.", type="warning", to="/finance/invoice/data-invoice-customer", is_read=True),
        Notification(title="DO Selesai", message="Delivery Order 001/DO/VI/2025 telah selesai diproses.", type="success", to="/operations", is_read=True),
        Notification(title="Revisi Surat Penawaran", message="Surat penawaran 002/OL/VI/2025 memerlukan revisi.", type="error", to="/marketing/customer", is_read=True),
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
