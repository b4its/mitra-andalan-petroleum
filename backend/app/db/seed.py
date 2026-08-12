import argparse
import asyncio
import gc
import json
import sys
from datetime import date, datetime, timedelta

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
from app.models.upload import Upload
from app.models.accounting import Account, JournalEntry, JournalLine


# ── Urutan hapus data (FK-safe: child dulu, parent belakangan) ──
_CLEAR_ORDER = [
    Upload, JournalLine, JournalEntry, Notification,
    Invoice, DeliveryOrder, PurchaseOrder, OfferingLetter,
    Sale, Account, Supplier, Customer, User,
]


async def seed_database(db: AsyncSession, force: bool = False):
    """Isi database dengan data contoh.

    Tanpa `force` (dipakai saat startup backend): hanya berjalan jika database
    masih kosong (tabel `users`). Jangan pernah menghapus data yang sudah ada —
    tanpa guard ini, setiap restart backend akan menghapus SEMUA data termasuk
    `uploads` (record lampiran), sehingga file yang sudah di-upload user hilang
    dari sistem meski file-nya masih ada di disk.

    Dengan `force=True` (CLI `python -m app.db.seed --force`): hapus dulu
    SEMUA data (FK-safe) lalu isi ulang dari nol.
    """
    if not force:
        existing = (await db.execute(select(User))).scalars().all()
        if existing:
            print("[seed] Dilewati: database sudah berisi data.")
            print("[seed] Gunakan `python -m app.db.seed --force` (atau `make reseed`) untuk mengisi ulang dari nol.")
            return

    await _clear_all(db)
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
    print("[seed] Selesai mengisi data contoh (5 user, 3 customer, 2 supplier, 15 OL, 10 PO, 15 DO, 15 invoice, notifikasi, penjualan, akuntansi).")


async def _clear_all(db: AsyncSession):
    """Hapus semua data dari tabel yang dikenal (FK-safe)."""
    for model in _CLEAR_ORDER:
        rows = await db.execute(select(model))
        for row in rows.scalars().all():
            await db.delete(row)
    await db.flush()


# ── Users ──────────────────────────────────────────────────────

async def _seed_users(db: AsyncSession):
    users = [
        User(name="Admin", email="admin@email.com", password=bcrypt.hash("admin123"), demo_password="admin123", role="admin"),
        User(name="Baits", email="ops@email.com", password=bcrypt.hash("ops123"), demo_password="ops123", role="operations"),
        User(name="Nico", email="marketing@email.com", password=bcrypt.hash("marketing123"), demo_password="marketing123", role="marketing"),
        User(name="Alea", email="finance@email.com", password=bcrypt.hash("finance123"), demo_password="finance123", role="finance"),
        User(name="Rina", email="accounting@email.com", password=bcrypt.hash("accounting123"), demo_password="accounting123", role="accounting"),
    ]
    for u in users:
        db.add(u)
    await db.flush()


# ── Customers ──────────────────────────────────────────────────

async def _seed_customers(db: AsyncSession):
    customers = [
        Customer(name="PT. Bina Karya Sentosa", npwp="01.234.567.8-901.000", address="Jl. Jenderal Sudirman No. 45, Samarinda", province="Kalimantan Timur", city="Samarinda", phone="0541-1234567", email="bina@karya-sentosa.com"),
        Customer(name="CV. Maju Jaya Abadi", npwp="02.345.678.9-012.000", address="Jl. Pahlawan No. 88, Balikpapan", province="Kalimantan Timur", city="Balikpapan", phone="0542-2345678", email="maju.jaya@abadi.co.id"),
        Customer(name="PT. Sumber Rejeki Mandiri", npwp="03.456.789.0-123.000", address="Jl. Empat Lima No. 12, Tenggarong", province="Kalimantan Timur", city="Tenggarong", phone="0541-3456789", email="sumber.rejeki@gmail.com"),
    ]
    for c in customers:
        db.add(c)
    await db.flush()


# ── Suppliers ──────────────────────────────────────────────────

async def _seed_suppliers(db: AsyncSession):
    suppliers = [
        Supplier(name="PT. Supplier Logistik Mandiri", npwp="021234567890123", address="Jl. Industri No. 7, Samarinda", province="Kalimantan Timur", city="Samarinda", phone="021-5678910", email="logistik@mandiri.co.id"),
        Supplier(name="CV. Bahan Bakar Utama", npwp="032345678901234", address="Jl. Minyak No. 33, Balikpapan", province="Kalimantan Timur", city="Balikpapan", phone="0542-1234567", email="bbu@bahanbakar.com"),
    ]
    for s in suppliers:
        db.add(s)
    await db.flush()


# ── Detail JSON helpers ────────────────────────────────────────

def _ol_details(ol_number: str, customer_name: str, address: str, fuel_price: float, transport_price: float) -> str:
    return json.dumps({
        "location": "Samarinda",
        "date": "2025-06-01",
        "offeringLetterNumber": ol_number,
        "regarding": "Penawaran Harga BBM Solar Industri",
        "receiver": customer_name,
        "supplyPoint": "Tanki Timbun Pelabuhan Samarinda",
        "qualityAssurance": "Sesuai spesifikasi BBM Solar Industri berlaku",
        "custodyTransfer": "Setelah muat di mobil tangki di Pelabuhan",
        "unloadingProcedure": "Menggunakan selang muat milik armada",
        "volumeUnit": "Liter observed",
        "volumeTolerance": 0.025,
        "paymentTerm": 7,
        "latePenalty": 0.02,
        "servicePattern": "Setiap hari kerja (Senin-Sabtu)",
        "personInCharge": {"name": "Nico", "phoneNumber": "08123456789"},
        "paymentAddress": {
            "bankName": "BANK BCA",
            "accountNumber": "1234567890",
            "accountName": "PT. MITRA ANDALAN PETROLEUM"
        },
        "fuelPrices": {
            "logisticInformation": "Armada sendiri (Mobil Tangki 10 KL / 5 KL)",
            "productName": "Bio Diesel (B35)",
            "hppPrice": 15000,
            "basePrice": 17950,
            "totalPrice": fuel_price,
            "sellingPrice": {"ppkb": 0, "oat": transport_price, "ppn": 0.11 * fuel_price},
            "percentageNum": {"oat": 0, "ppkb": 0.1, "ppn": 0.11}
        },
        "purchaseOrderDeadline": 30,
        "offeror": {"name": "Nico"},
        "companyInformation": {
            "address": "Jl. Belatuk Samarinda, Indonesia",
            "phoneNumber": "0541-1234567",
            "email": "marketing.mapetroleum@gmail.com"
        }
    })


def _po_details(main_company: dict, receiver: dict, po_number: str, products: list, vat: float = 0.11) -> str:
    return json.dumps({
        "companyInformation": main_company,
        "receiver": receiver,
        "po": {"date": "2025-06-01", "number": po_number},
        "vat": vat,
        "paymentAddress": {
            "bankName": "BCA Samarinda",
            "accountNumber": "1234567890",
            "accountName": "PT. Mitra Andalan Petroleum"
        },
        "selectedOfferingLetter": {},
        "products": products,
        "totalProductsPrice": sum(p["totalPrice"] for p in products),
        "termAndCondition": "Pembayaran dilakukan 7 hari setelah invoice diterbitkan",
        "delivery": {
            "loadingTerminal": "Pelabuhan Samarinda",
            "loadingDate": "2025-06-05",
            "picOperationMap": "Baits",
            "distance": 120
        },
        "forwarder": {"trucking": "Armada sendiri"},
        "signed": {"createdBy": "Nico", "approvedBy": "Admin"}
    })


def _do_details(customer_name: str, customer_address: str, po_customer_number: dict, transport_name: str, driver_name: str, fuel_total: float) -> str:
    return json.dumps({
        "companyInformation": {
            "name": "PT. MITRA ANDALAN PETROLEUM",
            "nameSub": "MAP",
            "address": "Jl. Belatuk Samarinda, Indonesia",
            "phoneNumber": "0541-1234567"
        },
        "doInformation": {
            "doNumber": "001/DO/MAP/VI/2025",
            "doDateCreated": "2025-06-02",
            "poCustomerNumber": po_customer_number,
            "soNumber": "SO/001/VI/2025"
        },
        "customerName": customer_name,
        "customerId": po_customer_number.get("customerId") or "",
        "customerAddress": customer_address,
        "receiverInformation": {"name": customer_name, "phoneNumber": "08123456789"},
        "receiverDateReceived": "2025-06-02",
        "transportName": transport_name,
        "transportId": "",
        "transportAddress": "Jl. Angkut No. 1, Samarinda",
        "driverInformation": {"name": driver_name, "phoneNumber": "08129876543"},
        "helperName": "Budi",
        "transportDateReceived": "2025-06-02",
        "dueDate": "2025-06-03",
        "productInformation": {
            "name": "Solar Industri (B35)",
            "qty": fuel_total,
            "temperature": 28.5,
            "topSeal": "MAP-001",
            "bottomSeal": "MAP-001-B"
        },
        "transportInformation": {
            "transportType": "Mobil Tangki",
            "transportNumber": "KT 1234 AB",
            "startKm": 12500,
            "endKm": 12680,
            "sgMeter": 0.845,
            "timeInformation": {
                "departureTime": "08:00",
                "arrivalTime": "10:30",
                "unloadingTime": "11:00",
                "depotArrivalTime": "14:00"
            }
        },
        "total": fuel_total,
        "notes": [
            {"note": "Sebelum BBM diserahterimakan, mohon periksa terlebih dahulu surat tera, jarum tera, segel, kualitas, SGMeter, kuantitas, kadar air, flow meter yang digunakan"},
            {"note": "Setelah pembongkaran, BBM industri yang sudah diterima dengan baik dan ditanda tangani kedua belah pihak, tidak dapat dikembalikan dan BBM tersebut sudah tidak menjadi tanggung jawab kami"},
            {"note": "Lainnya :"}
        ],
        "t2Depot": 28.5,
        "t2Unloading": 29.0,
        "indexSensitivity": 0.05,
        "fuelReceived": fuel_total,
        "companyCoordinator": "Baits",
        "distributionAdmin": "Rina",
        "receiver": customer_name,
        "driver": driver_name
    })


def _invoice_details(customer_name: str, customer_address: str, invoice_number: str, products: list, grand_total: float, po_customer_number: dict, do_numbers: list) -> str:
    return json.dumps({
        "companyInformation": {
            "name": "PT. MITRA ANDALAN PETROLEUM",
            "nameSub": "MAP",
            "address": "Jl. Belatuk No. 1, Samarinda, Kalimantan Timur",
            "phoneNumber": "0541-1234567",
            "email": "marketing.mapetroleum@gmail.com"
        },
        "billToInformation": customer_name,
        "deliveryPointInformation": customer_address,
        "invoiceInformation": {
            "invoiceNumber": invoice_number,
            "invoiceDate": "2025-06-10",
            "terms": 30,
            "invoiceDueDate": "2025-07-10"
        },
        "customerPurchaseInformation": {
            "deliveryOrderNumberData": do_numbers,
            "customerPurchaseOrderNumber": po_customer_number,
            "taxInvoiceNumber": "010.000-25.00000001",
            "salesOrderNumber": "SO/001/VI/2025"
        },
        "products": products,
        "priceSummary": {
            "subTotal": grand_total / 1.11,
            "prePaid": 0,
            "discount": 0,
            "ppn": grand_total - (grand_total / 1.11),
            "grandTotal": grand_total,
            "spellNumber": f"{grand_total:,.0f} rupiah"
        },
        "termsAndCondition": [
            {"term": "Pembayaran dilakukan transfer ke rekening BANK BCA"},
            {"term": "Invoice jatuh tempo 30 hari setelah diterbitkan"}
        ],
        "paymentInformation": {
            "bankName": "BANK BCA",
            "accountNumber": "1234567890",
            "accountName": "PT. MITRA ANDALAN PETROLEUM"
        },
        "signature": {
            "companyName": "PT. Mitra Andalan Petroleum",
            "createdBy": "Alea"
        }
    })


# ── Offering Letters ───────────────────────────────────────────

async def _seed_offering_letters(db: AsyncSession):
    customers = (await db.execute(select(Customer))).scalars().all()
    marketing_users = (await db.execute(select(User).where(User.role == "marketing"))).scalars().all()
    creator = marketing_users[0] if marketing_users else None
    statuses = ["created", "under_revision", "po_received"]

    for i in range(15):
        customer = customers[i % len(customers)]
        ol_number = f"{i + 1:03d}/OL/VI/2025"
        fuel_price = 50000000 + (i * 1000000)
        transport_price = 2500000 + (i * 100000)
        status = statuses[i % len(statuses)]
        ol = OfferingLetter(
            offering_letter_number=ol_number,
            customer_id=customer.id,
            location="Samarinda",
            date="2025-06-01",
            regarding="Penawaran BBM Solar Industri",
            receiver=customer.name,
            fuel_total_price=fuel_price,
            transport_price=transport_price,
            status=status,
            created_by=creator.id if creator else None,
            details=_ol_details(ol_number, customer.name, customer.address or "", fuel_price, transport_price),
        )
        db.add(ol)
    await db.flush()


# ── Purchase Orders ────────────────────────────────────────────

async def _seed_purchase_orders(db: AsyncSession):
    customers = (await db.execute(select(Customer))).scalars().all()
    suppliers = (await db.execute(select(Supplier))).scalars().all()
    users = (await db.execute(select(User))).scalars().all()
    marketing_user = next((u for u in users if u.role == "marketing"), None)
    finance_user = next((u for u in users if u.role == "finance"), None)

    main_company = {
        "name": "PT. MITRA ANDALAN PETROLEUM",
        "address": "Jl. Belatuk Samarinda, Indonesia",
        "npwp": "00.000.000.0-000.000",
        "contactPerson": "0812 3456 7898",
        "email": "marketing.mapetroleum@gmail.com"
    }

    # PO Customer
    for i in range(5):
        customer = customers[i % len(customers)]
        po_number = f"PO/2025/VI/{100 + i}"
        products = [
            {"name": "Solar Industri (B35)", "qty": 8000, "unit": "Liter", "price": 6250, "totalPrice": 50000000}
        ]
        po = PurchaseOrder(
            po_number=po_number,
            type="customer",
            customer_id=customer.id,
            date="2025-06-01",
            total=50000000,
            status=["created", "po_received"][i % 2],
            created_by=marketing_user.id if marketing_user else None,
            details=_po_details(main_company, {
                "id": customer.id, "name": customer.name, "npwp": customer.npwp,
                "address": customer.address, "contactPerson": customer.phone, "email": customer.email
            }, po_number, products),
        )
        db.add(po)

    # PO Supplier
    for i in range(5):
        supplier = suppliers[i % len(suppliers)]
        po_number = f"PO-SUP/2025/VI/{100 + i}"
        products = [
            {"name": "Solar Industri (B35)", "qty": 8000, "unit": "Liter", "price": 5625, "totalPrice": 45000000}
        ]
        po = PurchaseOrder(
            po_number=po_number,
            type="supplier",
            supplier_id=supplier.id,
            date="2025-06-01",
            total=45000000,
            status="created",
            created_by=marketing_user.id if marketing_user else None,
            details=_po_details(main_company, {
                "id": supplier.id, "name": supplier.name, "npwp": "",
                "address": supplier.address or "", "contactPerson": supplier.phone or "", "email": supplier.email or ""
            }, po_number, products),
        )
        db.add(po)
    await db.flush()

    # Hubungkan beberapa PO ke OL (id_offering_letters)
    pos = (await db.execute(select(PurchaseOrder))).scalars().all()
    ols = (await db.execute(select(OfferingLetter))).scalars().all()
    if ols and pos:
        pos[0].id_offering_letters = json.dumps([ols[0].id, ols[1].id])
        if len(pos) > 1:
            pos[1].id_offering_letters = json.dumps([ols[1].id])
    await db.flush()


# ── Delivery Orders ────────────────────────────────────────────

async def _seed_delivery_orders(db: AsyncSession):
    customers = (await db.execute(select(Customer))).scalars().all()
    pos = (await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.type == "customer")
    )).scalars().all()
    ops_users = (await db.execute(select(User).where(User.role == "operations"))).scalars().all()
    creator = ops_users[0] if ops_users else None
    customer_by_id = {c.id: c for c in customers}
    transports = ["PT. Transport Logistik", "CV. Angkutan Cepat", "PT. Distribusi Mandiri"]
    drivers = ["Supriyanto", "Hendra", "Agus", "Bambang"]
    statuses = ["created", "document_returned"]

    for i in range(15):
        po = pos[i % len(pos)]
        customer = customer_by_id.get(po.customer_id) or customers[i % len(customers)]
        fuel_total = 8000 + (i * 500)
        transport_name = transports[i % len(transports)]
        status = statuses[i % 2]
        do_number = f"{i + 1:03d}/DO/MAP/VI/2025"
        po_customer_number = {
            "id": po.id,
            "purchaseOrderNumber": po.po_number,
            "customerName": customer.name,
            "customerId": customer.id,
            "dateCreated": po.date,
            "dateChanged": po.date,
            "fuelTotalQty": fuel_total
        }
        do = DeliveryOrder(
            do_number=do_number,
            customer_id=po.customer_id,
            id_purchase_order=po.id,
            po_number=po.po_number,
            transport_name=transport_name,
            fuel_total=fuel_total,
            status=status,
            created_by=creator.id if creator else None,
            details=_do_details(
                customer.name, customer.address or "",
                po_customer_number,
                transport_name, drivers[i % len(drivers)], fuel_total,
            ),
        )
        db.add(do)
    await db.flush()


# ── Invoices ───────────────────────────────────────────────────

async def _seed_invoices(db: AsyncSession):
    customers = (await db.execute(select(Customer))).scalars().all()
    pos = (await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.type == "customer")
    )).scalars().all()
    customer_by_id = {c.id: c for c in customers}
    statuses = ["unpaid", "paid", "overdue"]
    deadlines = ["on_time", "overdue", "due_soon"]
    do_numbers = [f"{i + 1:03d}/DO/MAP/VI/2025" for i in range(3)]

    for i in range(15):
        po = pos[i % len(pos)]
        customer = customer_by_id.get(po.customer_id) or customers[i % len(customers)]
        grand_total = 50000000 + (i * 2500000)
        products = [
            {"qty": 8000, "unit": "Liter", "name": "Solar Industri (B35)", "price": 6250, "totalPrice": 50000000}
        ]
        po_customer_number = {
            "id": po.id,
            "purchaseOrderNumber": po.po_number,
            "customerName": customer.name,
            "customerId": customer.id,
            "dateCreated": po.date,
            "dateChanged": po.date,
            "fuelTotalQty": 8000
        }
        inv = Invoice(
            invoice_number=f"INV/2025/VI/{i + 1:03d}",
            customer_id=po.customer_id,
            terms_day=30,
            grand_total=grand_total,
            invoice_status=statuses[i % 3],
            deadline_status=deadlines[i % 3],
            details=_invoice_details(
                customer.name, customer.address or "",
                f"INV/2025/VI/{i + 1:03d}",
                products, grand_total, po_customer_number, do_numbers,
            ),
        )
        db.add(inv)
    await db.flush()


# ── Notifications ──────────────────────────────────────────────

async def _seed_notifications(db: AsyncSession):
    users = {u.role: u for u in (await db.execute(select(User))).scalars().all()}
    marketing_user = users.get("marketing")
    ops_user = users.get("operations")
    finance_user = users.get("finance")
    accounting_user = users.get("accounting")

    notifications = [
        Notification(title="PO Baru Masuk", message="Purchase Order baru dari PT. Bina Karya Sentosa telah masuk.", type="info", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=True),
        Notification(title="Invoice Jatuh Tempo", message="Invoice INV/2025/VI/001 akan jatuh tempo dalam 3 hari.", type="warning", sender_id=finance_user.id if finance_user else None, to="/finance/invoice/data-invoice-customer", is_read=True),
        Notification(title="DO Selesai", message="Delivery Order 001/DO/MAP/VI/2025 telah selesai diproses.", type="success", sender_id=ops_user.id if ops_user else None, to="/operations", is_read=True),
        Notification(title="Revisi Surat Penawaran", message="Surat penawaran 002/OL/VI/2025 memerlukan revisi.", type="error", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=True),
        Notification(title="Penawaran Baru", message="Surat penawaran 003/OL/VI/2025 berhasil dibuat oleh tim marketing.", type="info", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=False),
        Notification(title="PO Supplier Dibuat", message="Purchase Order ke PT. Supplier Logistik Mandiri berhasil dibuat.", type="success", sender_id=marketing_user.id if marketing_user else None, to="/marketing/supplier", is_read=False),
        Notification(title="Jurnal Baru", message="Jurnal umum baru telah diposting oleh tim finance.", type="info", sender_id=finance_user.id if finance_user else None, role="accounting", to="/accounting/jurnal-umum", is_read=True),
        Notification(title="Laba Rugi Bulanan", message="Laporan laba rugi bulan Juli 2025 tersedia. Cek neraca dan rekap biaya.", type="info", sender_id=accounting_user.id if accounting_user else None, role="accounting", to="/accounting/neraca", is_read=False),
        Notification(title="Rekonsiliasi Bank", message="Data rekening bank BCA perlu direkonsiliasi untuk periode Agustus 2025.", type="warning", sender_id=finance_user.id if finance_user else None, role="accounting", to="/accounting/kas-harian", is_read=False),
    ]
    for n in notifications:
        db.add(n)
    await db.flush()


# ── Sales ──────────────────────────────────────────────────────

async def _seed_sales(db: AsyncSession):
    sales = [
        Sale(date="2025-06-01", status="paid", email="admin@email.com", amount=25000000),
        Sale(date="2025-06-05", status="paid", email="marketing@email.com", amount=35000000),
        Sale(date="2025-06-10", status="failed", email="finance@email.com", amount=30000000),
        Sale(date="2025-06-15", status="paid", email="ops@email.com", amount=45000000),
        Sale(date="2025-06-20", status="refunded", email="user@email.com", amount=40000000),
    ]
    for s in sales:
        db.add(s)
    await db.flush()


# ── Accounting ─────────────────────────────────────────────────

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
    accounts: dict[str, Account] = {}
    for acc_type, items in ACCOUNT_GROUPS.items():
        for code, name, desc in items:
            acc = Account(code=code, name=name, type=acc_type, description=desc)
            db.add(acc)
            accounts[code] = acc
    await db.flush()

    kas = accounts["1-1000"]
    bank = accounts["1-1100"]
    piutang = accounts["1-1200"]
    pendapatan = accounts["4-1000"]
    ongkir = accounts["4-1100"]
    beban_transport = accounts["5-1010"]
    beban_operasional = accounts["5-1000"]

    entries = [
        {"entry_number": "JRM-202606-0001", "entry_date": date(2026, 6, 5), "description": "Penjualan BBM tunai ke PT. Bina Karya Sentosa", "reference": "INV/2026/VI/001", "lines": [(kas, None, 50000000, 0), (pendapatan, None, 0, 50000000)]},
        {"entry_number": "JRM-202606-0002", "entry_date": date(2026, 6, 10), "description": "Penjualan BBM kredit ke CV. Maju Jaya Abadi", "reference": "INV/2026/VI/002", "lines": [(piutang, None, 75000000, 0), (pendapatan, None, 0, 75000000)]},
        {"entry_number": "JRM-202606-0003", "entry_date": date(2026, 6, 15), "description": "Pembayaran jasa angkut transportir", "reference": "DO/2026/VI/003", "lines": [(beban_transport, None, 2500000, 0), (kas, None, 0, 2500000)]},
        {"entry_number": "JRM-202606-0004", "entry_date": date(2026, 6, 20), "description": "Penerimaan pembayaran piutang dari CV. Maju Jaya Abadi", "reference": "PAY/2026/VI/004", "lines": [(bank, None, 75000000, 0), (piutang, None, 0, 75000000)]},
        {"entry_number": "JRM-202606-0005", "entry_date": date(2026, 6, 25), "description": "Pembayaran beban operasional bulan Juni", "reference": "EXP/2026/VI/005", "lines": [(beban_operasional, None, 8000000, 0), (kas, None, 0, 8000000)]},
        {"entry_number": "JRM-202606-0006", "entry_date": date(2026, 6, 28), "description": "Pendapatan jasa angkut diterima tunai", "reference": "TR/2026/VI/006", "lines": [(kas, None, 5000000, 0), (ongkir, None, 0, 5000000)]},
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


# ── Verifikasi pola hasil seed (CLI --check) ───────────────────

async def _check_seed(db: AsyncSession) -> bool:
    """Periksa jumlah data dan pola relasi antar dokumen hasil seed."""
    async def count(model) -> int:
        return len((await db.execute(select(model))).scalars().all())

    all_ok = True

    print("[seed] Jumlah data:")
    for name, actual, expected in [
        ("users", await count(User), 5),
        ("customers", await count(Customer), 3),
        ("suppliers", await count(Supplier), 2),
        ("offering_letters", await count(OfferingLetter), 15),
        ("purchase_orders", await count(PurchaseOrder), 10),
        ("delivery_orders", await count(DeliveryOrder), 15),
        ("invoices", await count(Invoice), 15),
        ("accounts", await count(Account), 21),
        ("journal_entries", await count(JournalEntry), 6),
    ]:
        ok = actual == expected
        all_ok = all_ok and ok
        print(f"  [{'OK' if ok else 'FAIL'}] {name}: {actual} (diharapkan {expected})")

    print("[seed] Pola relasi dokumen:")
    dos = (await db.execute(select(DeliveryOrder))).scalars().all()
    pos = {p.id: p for p in (await db.execute(select(PurchaseOrder))).scalars().all()}
    po_numbers = {p.po_number for p in pos.values()}
    ols = (await db.execute(select(OfferingLetter))).scalars().all()
    ol_ids = {o.id for o in ols}

    for do in dos:
        if do.po_number not in po_numbers:
            print(f"  [FAIL] DO {do.do_number}: po_number '{do.po_number}' tidak cocok dengan PO mana pun")
            all_ok = False
        if do.id_purchase_order and do.id_purchase_order not in pos:
            print(f"  [FAIL] DO {do.do_number}: id_purchase_order tidak merujuk PO yang valid")
            all_ok = False
    print(f"  [{'OK' if all_ok else 'FAIL'}] delivery_orders -> purchase_orders ({len(dos)} DO terhubung ke PO)")

    pois = (await db.execute(select(PurchaseOrder))).scalars().all()
    po_linked = 0
    for po in pois:
        if not po.id_offering_letters:
            continue  # link ke OL tidak wajib (seeder hanya menghubungkan sebagian PO)
        po_linked += 1
        try:
            linked = json.loads(po.id_offering_letters)
        except (TypeError, json.JSONDecodeError):
            print(f"  [FAIL] PO {po.po_number}: id_offering_letters bukan JSON valid")
            all_ok = False
            continue
        if linked and not set(linked).issubset(ol_ids):
            print(f"  [FAIL] PO {po.po_number}: merujuk offering letter yang tidak ada")
            all_ok = False
    print(f"  [{'OK' if all_ok else 'FAIL'}] purchase_orders -> offering_letters ({po_linked} PO terhubung ke OL)")

    import re
    format_ok = True
    for do in dos:
        if not re.fullmatch(r"\d{3}/DO/MAP/VI/2025", do.do_number or ""):
            print(f"  [FAIL] DO {do.do_number}: format nomor tidak sesuai pola 001/DO/MAP/VI/2025")
            format_ok = False
    for ol in ols:
        if not re.fullmatch(r"\d{3}/OL/VI/2025", ol.offering_letter_number or ""):
            print(f"  [FAIL] OL {ol.offering_letter_number}: format nomor tidak sesuai pola 001/OL/VI/2025")
            format_ok = False
    for po in pois:
        if not re.fullmatch(r"(PO|PO-SUP)/2025/VI/\d{3}", po.po_number or ""):
            print(f"  [FAIL] PO {po.po_number}: format nomor tidak sesuai pola PO/2025/VI/100")
            format_ok = False
    invs = (await db.execute(select(Invoice))).scalars().all()
    for inv in invs:
        if not re.fullmatch(r"INV/2025/VI/\d{3}", inv.invoice_number or ""):
            print(f"  [FAIL] INV {inv.invoice_number}: format nomor tidak sesuai pola INV/2025/VI/001")
            format_ok = False
    all_ok = all_ok and format_ok
    print(f"  [{'OK' if format_ok else 'FAIL'}] format nomor dokumen (OL/PO/DO/INV)")

    return all_ok


async def _cli() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.db.seed",
        description="Seeder database Mitra Andalan Petroleum (backend/app/db/seed.py).",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Hapus dulu SEMUA data (FK-safe) lalu isi ulang dari nol (reseed)."
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Periksa hasil seed: jumlah data per tabel dan pola relasi antar dokumen."
    )
    args = parser.parse_args()

    from app.db.session import engine, async_session_factory

    session = async_session_factory()
    try:
        if args.check:
            print(f"[seed] Mode: verifikasi ({'setelah reseed' if args.force else 'data saat ini'})")
            ok = await _check_seed(session)
            print("[seed] SEMUA POLA VALID" if ok else "[seed] ADA POLA TIDAK VALID")
            return 0 if ok else 1
        print("[seed] Mode: reseed --force" if args.force else "[seed] Mode: seed (database kosong saja)")
        await seed_database(session, force=args.force)
        print("[seed] Selesai.")
        return 0
    finally:
        await session.close()
        await engine.dispose()


if __name__ == "__main__":
    # Tutup session + engine di dalam loop yang masih hidup agar tidak ada
    # `Exception ignored ... Event loop is closed` saat interpreter keluar.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        code = loop.run_until_complete(_cli())
    finally:
        loop.close()
    sys.exit(code)