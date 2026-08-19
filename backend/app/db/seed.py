import argparse
import asyncio
import gc
import json
import math
import struct
import sys
import uuid
import zlib
from datetime import date, datetime, timedelta
from pathlib import Path

from passlib.hash import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.offering_letter import OfferingLetter
from app.models.purchase_order import PurchaseOrder
from app.models.delivery_order import DeliveryOrder
from app.models.company import Company
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.models.sale import Sale
from app.models.upload import Upload
from app.models.po_transportir import PoTransportir
from app.models.accounting import Account, JournalEntry, JournalLine


# ── Urutan hapus data (FK-safe: child dulu, parent belakangan) ──
_CLEAR_ORDER = [
    Upload, JournalLine, JournalEntry, Notification,
    Invoice, PoTransportir, DeliveryOrder, PurchaseOrder, OfferingLetter,
    Sale, Account, Company, Supplier, Customer, User,
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
    await _seed_companies(db)
    await _seed_offering_letters(db)
    await _seed_purchase_orders(db)
    await _seed_po_transportir(db)
    await _seed_delivery_orders(db)
    await _seed_invoices(db)
    await _seed_notifications(db)
    await _seed_sales(db)
    await _seed_accounting(db)
    await _seed_signatures(db)
    await db.commit()
    print("[seed] Selesai mengisi data contoh (5 user, 3 company, 3 customer, 2 supplier, 15 OL, 10 PO, 3 PO transportir, 15 DO, 15 invoice, notifikasi, penjualan, akuntansi, tanda tangan).")




async def _seed_offering_letters(db: AsyncSession):
    """Seed surat penawaran data untuk sistem."""
    today = datetime.now()
    
    # Get customer IDs from seed
    result = await db.execute(select(Customer))
    customers = result.scalars().all()
    
    if not customers:
        print("[seed] Warning: No customers found, skipping OL generation")
        return
        
    # Create comprehensive OL records
    ol_numbers = [
        ("722/MAP/II-06/26", 15),
        ("723/MAP/III-07/26", 20), 
        ("724/MAP/IV-08/26", 25),
        ("725/MAP/V-09/26", 30),
        ("726/MAP/VI-10/26", 35),
        ("727/MAP/VII-11/26", 40),
        ("728/MAP/VIII-12/26", 45),
        ("729/MAP/IX-01/27", 50),
        ("730/MAP/X-02/27", 55),
        ("731/MAP/XI-03/27", 60),
        ("732/MAP/XII-04/27", 65),
        ("733/MAP/I-05/27", 70),
        ("734/MAP/II-06/27", 75),
        ("735/MAP/III-07/27", 80),
        ("736/MAP/IV-08/27", 85),
    ]
    
    for i in range(min(15, len(customers))):
        ol_number, days_delivery = ol_numbers[i % len(ol_numbers)]
        customer = customers[i % len(customers)]
        
        ol_data = {
            "id": str(uuid.uuid4()),
            "offering_letter_number": ol_number,
            "date": (today - timedelta(days=30-i)).strftime("%Y-%m-%d"),
            "location": "Balikpapan",
            "regarding": "Surat Penawaran Harga Bahan Bakar Minyak",
            "customer_id": customer.id,
            "payment_method": "kredit" if i % 2 == 0 else None,
            "payment_term": str((i + 1) * 7 if i < 10 else 30),
            "volume_tollerance": 0.005,
            "purchase_order_deadline": str((i + 1) * 7 if i < 5 else 14),
            "late_penalty_percent": 0.01,
            "price_service_type": "Truk Tangki" if i % 2 == 0 else "Pipeline",
            "fuel_product_name": "Bio Diesel",
            "fuel_hpp_price": round(17450 + (i * 100)),
            "fuel_base_price": round(17950 + (i * 100)),
            "fuel_selling_ppkb_percent": 0.005,
            "fuel_selling_oat_percent": 0.01,
            "fuel_selling_ppn_percent": 0.11,
            "fuel_selling_pph_percent": 0 if i < 10 else 0.02,
            "terms_and_conditions": json.dumps(["Harga dapat berubah mengikuti harga keekonomian Pertamina"])
        }
        
        ol = OfferingLetter(**ol_data)
        db.add(ol)
        
    await db.flush()
    print(f"[seed] Menambahkan {len(ol_numbers[:15])} surat penawaran.")


# ── Companies ────────────────────────────────────────────────────

async def _seed_companies(db: AsyncSession):
    """Seed perusahaan data untuk sistem."""
    companies = [
        {
            "id": str(uuid.uuid4()),
            "name": "PT. Mitra Andalan Petroleum",
            "abbreviation": "MAP",
            "company_image": None
        },
        {
            "id": str(uuid.uuid4()),
            "name": "PT. Pertamina Hulu Energi", 
            "abbreviation": "PHE",
            "company_image": None
        },
        {
            "id": str(uuid.uuid4()),
            "name": "PT. Total E&P Indonesia",
            "abbreviation": "TEPI", 
            "company_image": None
        }
    ]
    
    for comp_data in companies:
        comp = Company(**comp_data)
        db.add(comp)
        
    await db.flush()
    print(f"[seed] Menambahkan {len(companies)} perusahaan.")



async def _clear_all(db: AsyncSession):
    """Hapus semua data dari tabel yang dikenal (FK-safe)."""
    for model in _CLEAR_ORDER:
        rows = await db.execute(select(model))
        for row in rows.scalars().all():
            await db.delete(row)
    await db.flush()


# ── Users ──────────────────────────────────────────────────────

async def _seed_users(db: AsyncSession):
    """Seed user data untuk sistem."""
    users = [
        {
            "id": str(uuid.uuid4()),
            "name": "Ahmad Fauzi",
            "email": "admin@mapetroleum.co.id",
            "password": bcrypt.hash("admin123"),
            "demo_password": "admin123",
            "role": "admin",
            "signature_caption": "Ahmad Fauzi - Admin"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Bambang Nugroho", 
            "email": "ops@mapetroleum.co.id",
            "password": bcrypt.hash("ops123"),
            "demo_password": "ops123",
            "role": "operations",
            "signature_caption": "Bambang Nugroho - Operations"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Nico Pratama",
            "email": "marketing@mapetroleum.co.id",
            "password": bcrypt.hash("marketing123"),
            "demo_password": "marketing123",
            "role": "marketing",
            "signature_caption": "Nico Pratama - Marketing"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Alea Rahmawati",
            "email": "finance@mapetroleum.co.id",
            "password": bcrypt.hash("finance123"),
            "demo_password": "finance123",
            "role": "finance",
            "signature_caption": "Alea Rahmawati - Finance"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Rina Marlina",
            "email": "accounting@mapetroleum.co.id",
            "password": bcrypt.hash("accounting123"),
            "demo_password": "accounting123",
            "role": "accounting",
            "signature_caption": "Rina Marlina - Accounting"
        }
    ]
    
    for u_data in users:
        u = User(**u_data)
        db.add(u)
        
    await db.flush()
    print(f"[seed] Menambahkan {len(users)} user.")


# ── Customers ──────────────────────────────────────────────────

async def _seed_customers(db: AsyncSession):
    customers = [
        Customer(name="PT. Surya Tambang Energi", npwp="01.609.052.4-091.000", address="Jl. A. W. Syahrani No. 45, Samarinda", province="Kalimantan Timur", city="Samarinda", phone="0541-741231", phone2="0812 5617 8230", email="cs@suryatambangenergi.co.id"),
        Customer(name="CV. Kaltim Jaya Abadi", npwp="02.104.783.2-091.000", address="Jl. Jend. Sudirman No. 88, Balikpapan", province="Kalimantan Timur", city="Balikpapan", phone="0542-426817", phone2="0813 9920 4471", email="admin@kaltimjayaabadi.co.id"),
        Customer(name="PT. Borneo Energi Utama", npwp="02.345.219.6-091.000", address="Jl. Teuku Umar No. 12, Tenggarong", province="Kalimantan Timur", city="Tenggarong", phone="0541-661234", phone2="0821 5507 1198", email="info@borneoenergiutama.co.id"),
    ]
    for c in customers:
        db.add(c)
    await db.flush()


# ── Suppliers ──────────────────────────────────────────────────

async def _seed_suppliers(db: AsyncSession):
    suppliers = [
        Supplier(name="PT. Persada Energi Nusantara", npwp="01.457.812.4-091.000", address="Jl. MT Haryono No. 7, Samarinda", province="Kalimantan Timur", city="Samarinda", phone="0541-746912", phone2="0811 235 7819", email="penjualan@persadaenerginusantara.co.id", bank_name="BANK BCA", bank_account="2881306571"),
        Supplier(name="CV. Sinar Petrolindo", npwp="02.451.963.9-091.000", address="Jl. Soekarno Hatta No. 33, Balikpapan", province="Kalimantan Timur", city="Balikpapan", phone="0542-882345", phone2="0852 4710 6653", email="cv.sinarpetrolindo@gmail.com", bank_name="BANK BRI", bank_account="002901123456789"),
    ]
    for s in suppliers:
        db.add(s)
    await db.flush()


# ── Detail JSON helpers ────────────────────────────────────────

def _ol_details(ol_number: str, customer_name: str, address: str, fuel_price: float, transport_price: float) -> str:
    return json.dumps({
        "location": "Samarinda",
        "date": "2026-06-01",
        "offeringLetterNumber": ol_number,
        "regarding": "Penawaran Harga BBM Solar Industri",
        "receiver": customer_name,
        "supplyPoint": "Tanki Timbun Pelabuhan Samarinda",
        "qualityAssurance": "Sesuai spesifikasi BBM Solar Industri berlaku",
        "custodyTransfer": "Setelah muat di mobil tangki di Pelabuhan",
        "unloadingProcedure": "Menggunakan selang muat milik armada",
        "volumeUnit": "Liter observed",
        "volumeTolerance": 0.025,
        "paymentMethod": "kredit",
        "paymentTerm": "1 - 14",
        "latePenalty": 0.02,
        "servicePattern": "Setiap hari kerja (Senin-Sabtu)",
        "personInCharge": {"name": "Nico Pratama", "phoneNumber": "0812 3456 7890"},
        "paymentAddress": {
            "bankName": "BANK BCA",
            "accountNumber": "2881306571",
            "accountName": "PT. MITRA ANDALAN PETROLEUM"
        },
        "fuelPrices": {
            "logisticInformation": "Armada sendiri (Mobil Tangki 10 KL / 5 KL)",
            "productName": "Bio Diesel (B35)",
            "hppPrice": 15000,
            "basePrice": 17950,
            "totalPrice": fuel_price,
            "sellingPrice": {"ppkb": 0, "oat": transport_price, "ppn": 0.11 * fuel_price, "pph": 0},
            "percentageNum": {"oat": 0, "ppkb": 0, "ppn": 0.11, "pph": 0}
        },
        "purchaseOrderDeadline": "1 - 14",
        "offeror": {"name": "Nico Pratama"},
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
        "po": {"date": "2026-06-01", "number": po_number},
        "vat": vat,
        "paymentAddress": {
            "bankName": "BCA Samarinda",
            "accountNumber": "2881306571",
            "accountName": "PT. Mitra Andalan Petroleum"
        },
        "selectedOfferingLetter": {},
        "products": products,
        "totalProductsPrice": sum(p["totalPrice"] for p in products),
        "termAndCondition": "Pembayaran dilakukan 7 hari setelah invoice diterbitkan",
        "delivery": {
            "loadingTerminal": "Pelabuhan Samarinda",
            "loadingDate": "2026-06-05",
            "picOperationMap": "Bambang Nugroho",
            "distance": 120
        },
        "forwarder": {"trucking": "Armada sendiri"},
        "signed": {"createdBy": "Nico Pratama", "approvedBy": "Ahmad Fauzi"}
    })


def _do_details(customer_name: str, customer_address: str, customer_phone: str, po_customer_number: dict, transport_name: str, transport_number: str, driver_name: str, driver_phone: str, fuel_total: float) -> str:
    return json.dumps({
        "companyInformation": {
            "name": "PT. MITRA ANDALAN PETROLEUM",
            "nameSub": "MAP",
            "address": "Jl. Belatuk Samarinda, Indonesia",
            "phoneNumber": "0541-1234567"
        },
        "doInformation": {
            "doNumber": "001/DO/MAP/VI/2026",
            "doDateCreated": "2026-06-02",
            "poCustomerNumber": po_customer_number,
            "soNumber": "SO/001/VI/2026"
        },
        "customerName": customer_name,
        "customerId": po_customer_number.get("customerId") or "",
        "customerAddress": customer_address,
        "receiverInformation": {"name": customer_name, "phoneNumber": customer_phone},
        "receiverDateReceived": "2026-06-02",
        "transportName": transport_name,
        "transportId": "",
        "transportAddress": "Jl. Pelita No. 18, Samarinda",
        "driverInformation": {"name": driver_name, "phoneNumber": driver_phone},
        "helperName": "Joko Susilo",
        "transportDateReceived": "2026-06-02",
        "dueDate": "2026-06-03",
        "productInformation": {
            "name": "Solar Industri (B35)",
            "qty": fuel_total,
            "temperature": 28.5,
            "topSeal": "MAP-001",
            "bottomSeal": "MAP-001-B"
        },
        "transportInformation": {
            "transportType": "Mobil Tangki",
            "transportNumber": transport_number,
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
        "companyCoordinator": "Bambang Nugroho",
        "distributionAdmin": "Rina Marlina",
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
            "invoiceDate": "2026-06-10",
            "terms": 30,
            "invoiceDueDate": "2026-07-10"
        },
        "customerPurchaseInformation": {
            "deliveryOrderNumberData": do_numbers,
            "customerPurchaseOrderNumber": po_customer_number,
            "taxInvoiceNumber": "010.000-26.00000001",
            "salesOrderNumber": "SO/001/VI/2026"
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
            "accountNumber": "2881306571",
            "accountName": "PT. MITRA ANDALAN PETROLEUM"
        },
        "signature": {
            "companyName": "PT. Mitra Andalan Petroleum",
            "createdBy": "Alea Rahmawati"
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
        ol_number = f"{i + 1:03d}/OL/VI/2026"
        fuel_price = 8000 * 17950
        transport_price = 2500000 + (i * 100000)
        status = statuses[i % len(statuses)]
        ol = OfferingLetter(
            offering_letter_number=ol_number,
            customer_id=customer.id,
            location="Samarinda",
            date="2026-06-01",
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
        po_number = f"PO/2026/VI/{100 + i}"
        products = [
            {"name": "Solar Industri (B35)", "qty": 8000, "unit": "Liter", "price": 17950, "totalPrice": 8000 * 17950}
        ]
        po = PurchaseOrder(
            po_number=po_number,
            type="customer",
            customer_id=customer.id,
            date="2026-06-01",
            total=8000 * 17950,
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
        po_number = f"PO-SUP/2026/VI/{100 + i}"
        products = [
            {"name": "Solar Industri (B35)", "qty": 8000, "unit": "Liter", "price": 15000, "totalPrice": 8000 * 15000, "ppkb": 0, "pph": 0.5, "ppn": 0.11 * 8000 * 15000}
        ]
        # Sebagian PO supplier sudah dirilis dana oleh admin (menyesuaikan alur:
        # marketing buat PO supplier -> admin rilis dana -> baru bisa lihat surat)
        rilis = i % 2 == 0
        po = PurchaseOrder(
            po_number=po_number,
            type="supplier",
            supplier_id=supplier.id,
            date="2026-06-01",
            total=8000 * 15000,
            status="created",
            created_by=marketing_user.id if marketing_user else None,
            rilis_dana_at=datetime(2026, 6, 2, 9, 0, 0) if rilis else None,
            status_rilis_dana=rilis,
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
    po_transportirs = (await db.execute(select(PoTransportir))).scalars().all()
    ops_users = (await db.execute(select(User).where(User.role == "operations"))).scalars().all()
    creator = ops_users[0] if ops_users else None
    customer_by_id = {c.id: c for c in customers}
    po_by_id = {p.id: p for p in pos}
    transports = [
        ("PT. Armada Kaltim Sejahtera", "KT 1832 AJ"),
        ("CV. Tiga Putra Transport", "KT 5741 BE"),
        ("PT. Borneo Distribusi Logistik", "KT 2906 CA"),
    ]
    drivers = [
        ("Supriyanto", "0812 3027 4491"),
        ("Hendra Gunawan", "0813 4538 2210"),
        ("Agus Salim", "0821 3762 9950"),
        ("Bambang Purnomo", "0852 2147 8836"),
    ]
    statuses = ["created", "document_returned"]

    for i in range(15):
        # Ambil PO Transportir (cycle) untuk di-link
        pt = po_transportirs[i % len(po_transportirs)] if po_transportirs else None
        # Resolve PO Customer dari PO Transportir
        linked_po = po_by_id.get(pt.id_purchase_order) if pt and pt.id_purchase_order else pos[i % len(pos)]
        customer = customer_by_id.get(linked_po.customer_id) if linked_po else customers[i % len(customers)]
        fuel_total = 8000 + (i * 500)
        transport_name, transport_number = transports[i % len(transports)]
        driver_name, driver_phone = drivers[i % len(drivers)]
        status = statuses[i % 2]
        do_number = f"{i + 1:03d}/DO/MAP/VI/2026"
        po_customer_number = {
            "id": linked_po.id if linked_po else "",
            "purchaseOrderNumber": linked_po.po_number if linked_po else "",
            "customerName": customer.name,
            "customerId": customer.id,
            "dateCreated": linked_po.date if linked_po else "",
            "dateChanged": linked_po.date if linked_po else "",
            "fuelTotalQty": fuel_total
        }
        do = DeliveryOrder(
            do_number=do_number,
            customer_id=customer.id,
            id_purchase_order=linked_po.id if linked_po else None,
            id_po_transportir=pt.id if pt else None,
            po_number=linked_po.po_number if linked_po else "",
            transport_name=transport_name,
            fuel_total=fuel_total,
            status=status,
            created_by=creator.id if creator else None,
            details=_do_details(
                customer.name, customer.address or "", customer.phone2 or "",
                po_customer_number,
                transport_name, transport_number, driver_name, driver_phone, fuel_total,
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

    for i in range(15):
        po = pos[i % len(pos)]
        customer = customer_by_id.get(po.customer_id) or customers[i % len(customers)]
        sub_total = 8000 * 17950
        grand_total = round(sub_total * 1.11)
        products = [
            {"qty": 8000, "unit": "Liter", "name": "Solar Industri (B35)", "price": 17950, "totalPrice": sub_total}
        ]
        do_numbers = [f"{i + 1:03d}/DO/MAP/VI/2026"]
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
            invoice_number=f"INV/2026/VI/{i + 1:03d}",
            customer_id=po.customer_id,
            terms_day=30,
            grand_total=grand_total,
            invoice_status=statuses[i % 3],
            deadline_status=deadlines[i % 3],
            details=_invoice_details(
                customer.name, customer.address or "",
                f"INV/2026/VI/{i + 1:03d}",
                products, grand_total, po_customer_number, do_numbers,
            ),
        )
        db.add(inv)
    await db.flush()


# ── PO Transportir ─────────────────────────────────────────────

def _po_transportir_details(po_number: str, receiver: str, pic_person: str, products: list, loading_date: str, discharge: str, customer_name: str | None = None) -> str:
    sub_total = sum(p["totalPrice"] for p in products)
    ppn = round(sub_total * 0.11)
    return json.dumps({
        "date": loading_date,
        "poTransportNumber": po_number,
        "regarding": "Purchase Order Transportir (PO)",
        "receiver": receiver,
        "picPerson": pic_person,
        "products": products,
        "percentageNum": {"ppn": 0.11},
        "priceSummary": {"subTotal": sub_total, "ppn": ppn, "grandTotal": sub_total + ppn},
        "loadingInformation": "Masbro, Pendingin, Kutai Kartanegara, Kalimantan Timur",
        "discharge": discharge,
        "termsOfPayment": "30 Hari kerja setelah invoice beserta kelengkapan dokumen selesai diverifikasi",
        "shrinkageTolerance": "Toleransi susut 0.3 %, Claim Susut Rp. 25.000,- / Liter",
        "contactPerson": {
            "companyName": "PT. Mitra Andalan Petroleum",
            "customerName": customer_name or receiver,
            "companyContactPerson": [{"name": "Nico Pratama", "phoneNumber": "0812 3456 7890"}],
            "customerContactPerson": [{"name": "Dedi Kurniawan", "phoneNumber": "0812 5617 8230"}],
        },
        "offeror": {"name": "Nico Pratama"},
    })


async def _seed_po_transportir(db: AsyncSession):
    ops_users = (await db.execute(select(User).where(User.role == "operations"))).scalars().all()
    creator = ops_users[0] if ops_users else None
    pic_person = "Bpk Bambang Nugroho"

    # Ambil PO Customer untuk di-link
    pos = (await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.type == "customer")
    )).scalars().all()
    customers = {c.id: c for c in (await db.execute(select(Customer))).scalars().all()}

    records = [
        ("121/PO-TRANS/MAP/VI/2026", "2026-06-05", "PT. Armada Kaltim Sejahtera",
         [{"name": "Solar", "loadingDate": "2026-06-05", "unloadingDate": "2026-06-06", "qty": 8000, "ratePrice": 500, "totalPrice": 4000000}],
         "Site MHU - Kutai Kartanegara", "created"),
        ("122/PO-TRANS/MAP/VI/2026", "2026-06-12", "CV. Tiga Putra Transport",
         [{"name": "Solar", "loadingDate": "2026-06-12", "unloadingDate": "2026-06-13", "qty": 10000, "ratePrice": 500, "totalPrice": 5000000}],
         "Site TDM / Separi - Kutai Kartanegara", "created"),
        ("123/PO-TRANS/MAP/VI/2026", "2026-06-20", "PT. Borneo Distribusi Logistik",
         [{"name": "Solar", "loadingDate": "2026-06-20", "unloadingDate": "2026-06-21", "qty": 8000, "ratePrice": 475, "totalPrice": 3800000}],
         "Site MHU - Kutai Kartanegara", "completed"),
    ]

    for i, (po_number, po_date, receiver, products, discharge, status) in enumerate(records):
        sub_total = sum(p["totalPrice"] for p in products)
        # Link ke PO Customer (cycle melalui PO yang ada)
        linked_po = pos[i % len(pos)] if pos else None
        customer_id = linked_po.customer_id if linked_po else None
        customer = customers.get(customer_id) if customer_id else None
        po = PoTransportir(
            po_number=po_number,
            date=po_date,
            pic_person=pic_person,
            receiver=receiver,
            total=sub_total + round(sub_total * 0.11),
            status=status,
            created_by=creator.id if creator else None,
            id_purchase_order=linked_po.id if linked_po else None,
            customer_id=customer_id,
            details=_po_transportir_details(
                po_number, receiver, pic_person, products, po_date, discharge,
                customer_name=customer.name if customer else None,
            ),
        )
        db.add(po)
    await db.flush()


# ── Notifications ──────────────────────────────────────────────

async def _seed_notifications(db: AsyncSession):
    users = {u.role: u for u in (await db.execute(select(User))).scalars().all()}
    marketing_user = users.get("marketing")
    ops_user = users.get("operations")
    finance_user = users.get("finance")
    accounting_user = users.get("accounting")

    notifications = [
        Notification(title="PO Baru Masuk", message="Purchase Order baru dari PT. Surya Tambang Energi telah masuk.", type="info", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=True),
        Notification(title="Invoice Jatuh Tempo", message="Invoice INV/2026/VI/001 akan jatuh tempo dalam 3 hari.", type="warning", sender_id=finance_user.id if finance_user else None, to="/finance/invoice/data-invoice-customer", is_read=True),
        Notification(title="DO Selesai", message="Delivery Order 001/DO/MAP/VI/2026 telah selesai diproses.", type="success", sender_id=ops_user.id if ops_user else None, to="/operations", is_read=True),
        Notification(title="Revisi Surat Penawaran", message="Surat penawaran 002/OL/VI/2026 memerlukan revisi.", type="error", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=True),
        Notification(title="Penawaran Baru", message="Surat penawaran 003/OL/VI/2026 berhasil dibuat oleh tim marketing.", type="info", sender_id=marketing_user.id if marketing_user else None, to="/marketing/customer", is_read=False),
        Notification(title="PO Supplier Dibuat", message="Purchase Order ke PT. Persada Energi Nusantara berhasil dibuat.", type="success", sender_id=marketing_user.id if marketing_user else None, to="/marketing/supplier", is_read=False),
        Notification(title="Jurnal Baru", message="Jurnal umum baru telah diposting oleh tim finance.", type="info", sender_id=finance_user.id if finance_user else None, role="accounting", to="/accounting/jurnal-umum", is_read=True),
        Notification(title="Laba Rugi Bulanan", message="Laporan laba rugi bulan Juli 2026 tersedia. Cek neraca dan rekap biaya.", type="info", sender_id=accounting_user.id if accounting_user else None, role="accounting", to="/accounting/neraca", is_read=False),
        Notification(title="Rekonsiliasi Bank", message="Data rekening bank BCA perlu direkonsiliasi untuk periode Agustus 2026.", type="warning", sender_id=finance_user.id if finance_user else None, role="accounting", to="/accounting/kas-harian", is_read=False),
    ]
    for n in notifications:
        db.add(n)
    await db.flush()


# ── Sales ──────────────────────────────────────────────────────

async def _seed_sales(db: AsyncSession):
    sales = [
        Sale(date="2026-06-01", status="paid", email="admin@mapetroleum.co.id", amount=25000000),
        Sale(date="2026-06-05", status="paid", email="marketing@mapetroleum.co.id", amount=35000000),
        Sale(date="2026-06-10", status="failed", email="finance@mapetroleum.co.id", amount=30000000),
        Sale(date="2026-06-15", status="paid", email="ops@mapetroleum.co.id", amount=45000000),
        Sale(date="2026-06-20", status="refunded", email="accounting@mapetroleum.co.id", amount=40000000),
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
    kas_kecil = accounts["1-1010"]
    bank = accounts["1-1100"]
    piutang = accounts["1-1200"]
    pendapatan = accounts["4-1000"]
    ongkir = accounts["4-1100"]
    beban_operasional = accounts["5-1000"]
    beban_transport = accounts["5-1010"]
    beban_gaji = accounts["5-1020"]
    beban_listrik_air = accounts["5-1030"]

    entries = [
        {"entry_number": "JRM-202606-0001", "entry_date": date(2026, 6, 5), "description": "Penjualan BBM tunai ke PT. Surya Tambang Energi", "reference": "INV/2026/VI/001", "lines": [(kas, None, 50000000, 0), (pendapatan, None, 0, 50000000)]},
        {"entry_number": "JRM-202606-0002", "entry_date": date(2026, 6, 10), "description": "Penjualan BBM kredit ke CV. Kaltim Jaya Abadi", "reference": "INV/2026/VI/002", "lines": [(piutang, None, 75000000, 0), (pendapatan, None, 0, 75000000)]},
        {"entry_number": "JRM-202606-0003", "entry_date": date(2026, 6, 15), "description": "Pembayaran jasa angkut transportir", "reference": "DO/2026/VI/003", "lines": [(beban_transport, None, 2500000, 0), (kas, None, 0, 2500000)]},
        {"entry_number": "JRM-202606-0004", "entry_date": date(2026, 6, 20), "description": "Penerimaan pembayaran piutang dari CV. Kaltim Jaya Abadi", "reference": "PAY/2026/VI/004", "lines": [(bank, None, 75000000, 0), (piutang, None, 0, 75000000)]},
        {"entry_number": "JRM-202606-0005", "entry_date": date(2026, 6, 25), "description": "Pembayaran beban operasional bulan Juni", "reference": "EXP/2026/VI/005", "lines": [(beban_operasional, None, 8000000, 0), (kas, None, 0, 8000000)]},
        {"entry_number": "JRM-202606-0006", "entry_date": date(2026, 6, 28), "description": "Pendapatan jasa angkut diterima tunai", "reference": "TR/2026/VI/006", "lines": [(kas, None, 5000000, 0), (ongkir, None, 0, 5000000)]},
        # Pemasukan (mutasi kredit pada akun pendapatan)
        {"entry_number": "JRM-202606-0007", "entry_date": date(2026, 6, 30), "description": "Pendapatan jasa angkut dibayar tunai oleh CV. Kaltim Jaya Abadi", "reference": "DO/2026/VI/007", "lines": [(kas, None, 6000000, 0), (ongkir, None, 0, 6000000)]},
        {"entry_number": "JRM-202607-0001", "entry_date": date(2026, 7, 3), "description": "Penjualan BBM kredit ke PT. Borneo Energi Utama", "reference": "INV/2026/VI/003", "lines": [(piutang, None, 42000000, 0), (pendapatan, None, 0, 42000000)]},
        # Pengeluaran (mutasi debit pada akun beban)
        {"entry_number": "JRM-202606-0008", "entry_date": date(2026, 6, 29), "description": "Pembayaran beban listrik & air bulan Juni", "reference": "UTL/2026/VI/001", "lines": [(beban_listrik_air, None, 1250000, 0), (kas_kecil, None, 0, 1250000)]},
        {"entry_number": "JRM-202607-0002", "entry_date": date(2026, 7, 5), "description": "Pembayaran gaji karyawan bulan Juni", "reference": "PAY/2026/VII/001", "lines": [(beban_gaji, None, 28000000, 0), (bank, None, 0, 28000000)]},
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


# ── Tanda tangan user (upload otomatis) ────────────────────────

def _png_chunk(typ: bytes, data: bytes) -> bytes:
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c


def _signature_png(name: str) -> bytes:
    """Buat PNG sederhana (murni Python, tanpa Pillow) berisi coretan tanda tangan."""
    w, h = 320, 110
    seed = sum(ord(c) for c in (name or "MAP"))
    rows = bytearray()
    for y in range(h):
        rows.append(0)  # filter none
        for x in range(w):
            r, g, b = 255, 255, 255
            # Coretan seperti tanda tangan: gelombang + garis miring
            yy = h // 2 + int(math.sin((x + seed) * 0.06) * (h // 4))
            if abs(y - yy) < 3:
                r, g, b = 25, 25, 60
            if 40 < x < w - 40 and abs(y - (h // 2 + 18)) < 2:
                r, g, b = 25, 25, 60
            rows.extend((r, g, b))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(rows), 9))
            + _png_chunk(b"IEND", b""))


async def _seed_signatures(db: AsyncSession):
    """Generate file tanda tangan (PNG) + record upload untuk tiap user.

    Menyesuaikan alur sistem saat ini: user meng-upload tanda tangan di profil,
    lalu tanda tangan tampil (QR/barcode) di dokumen marketing.
    """
    users = (await db.execute(select(User))).scalars().all()
    if not users:
        return

    media_dir = Path(__file__).resolve().parent.parent.parent / "media"
    profiles_dir = media_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    for user in users:
        stored = f"{uuid.uuid4().hex}.png"
        file_path = profiles_dir / stored
        png_bytes = _signature_png(user.name or "MAP")
        file_path.write_bytes(png_bytes)

        db.add(Upload(
            original_filename=f"signature-{user.name.replace(' ', '_')}.png",
            stored_filename=stored,
            folder="profiles",
            mime_type="image/png",
            size=len(png_bytes),
            url=f"/media/profiles/{stored}",
            document_type="profile",
            document_id=user.id,
        ))
    await db.flush()
    print(f"[seed] Tanda tangan {len(users)} user dibuat (folder profiles).")


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
        ("po_transportir", await count(PoTransportir), 3),
        ("accounts", await count(Account), 21),
        ("journal_entries", await count(JournalEntry), 10),
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

    do_po_ok = True
    for do in dos:
        if do.po_number not in po_numbers:
            print(f"  [FAIL] DO {do.do_number}: po_number '{do.po_number}' tidak cocok dengan PO mana pun")
            do_po_ok = False
        if do.id_purchase_order and do.id_purchase_order not in pos:
            print(f"  [FAIL] DO {do.do_number}: id_purchase_order tidak merujuk PO yang valid")
            do_po_ok = False
    all_ok = all_ok and do_po_ok
    print(f"  [{'OK' if do_po_ok else 'FAIL'}] delivery_orders -> purchase_orders ({len(dos)} DO terhubung ke PO)")

    # Validasi PO Customer → Offering Letter
    pois = (await db.execute(select(PurchaseOrder))).scalars().all()
    po_ol_ok = True
    po_linked = 0
    for po in pois:
        if not po.id_offering_letters:
            continue  # link ke OL tidak wajib (seeder hanya menghubungkan sebagian PO)
        po_linked += 1
        try:
            linked = json.loads(po.id_offering_letters)
        except (TypeError, json.JSONDecodeError):
            print(f"  [FAIL] PO {po.po_number}: id_offering_letters bukan JSON valid")
            po_ol_ok = False
            continue
        if linked and not set(linked).issubset(ol_ids):
            print(f"  [FAIL] PO {po.po_number}: merujuk offering letter yang tidak ada")
            po_ol_ok = False
    all_ok = all_ok and po_ol_ok
    print(f"  [{'OK' if po_ol_ok else 'FAIL'}] purchase_orders -> offering_letters ({po_linked} PO terhubung ke OL)")

    # Validasi PO Transportir → PO Customer
    potrans = (await db.execute(select(PoTransportir))).scalars().all()
    potrans_ok = True
    potrans_po_linked = 0
    for pt in potrans:
        if pt.id_purchase_order:
            if pt.id_purchase_order not in pos:
                print(f"  [FAIL] PO Transportir {pt.po_number}: id_purchase_order tidak merujuk PO yang valid")
                potrans_ok = False
            else:
                potrans_po_linked += 1
    print(f"  [{'OK' if potrans_ok else 'FAIL'}] po_transportir -> purchase_orders ({potrans_po_linked}/{len(potrans)} PO Transportir terhubung ke PO Customer)")
    all_ok = all_ok and potrans_ok

    # Validasi DO → PO Transportir
    do_potrans_ok = True
    do_potrans_linked = 0
    potrans_ids = {pt.id for pt in potrans}
    for do in dos:
        if do.id_po_transportir:
            if do.id_po_transportir not in potrans_ids:
                print(f"  [FAIL] DO {do.do_number}: id_po_transportir tidak merujuk PO Transportir yang valid")
                do_potrans_ok = False
            else:
                do_potrans_linked += 1
    print(f"  [{'OK' if do_potrans_ok else 'FAIL'}] delivery_orders -> po_transportir ({do_potrans_linked}/{len(dos)} DO terhubung ke PO Transportir)")
    all_ok = all_ok and do_potrans_ok

    import re
    format_ok = True
    for do in dos:
        if not re.fullmatch(r"\d{3}/DO/MAP/VI/2026", do.do_number or ""):
            print(f"  [FAIL] DO {do.do_number}: format nomor tidak sesuai pola 001/DO/MAP/VI/2026")
            format_ok = False
    for ol in ols:
        if not re.fullmatch(r"\d{3}/OL/VI/2026", ol.offering_letter_number or ""):
            print(f"  [FAIL] OL {ol.offering_letter_number}: format nomor tidak sesuai pola 001/OL/VI/2026")
            format_ok = False
    for po in pois:
        if not re.fullmatch(r"(PO|PO-SUP)/2026/VI/\d{3}", po.po_number or ""):
            print(f"  [FAIL] PO {po.po_number}: format nomor tidak sesuai pola PO/2026/VI/100")
            format_ok = False
    invs = (await db.execute(select(Invoice))).scalars().all()
    for inv in invs:
        if not re.fullmatch(r"INV/2026/VI/\d{3}", inv.invoice_number or ""):
            print(f"  [FAIL] INV {inv.invoice_number}: format nomor tidak sesuai pola INV/2026/VI/001")
            format_ok = False
    po_trans = (await db.execute(select(PoTransportir))).scalars().all()
    for pt in po_trans:
        if not re.fullmatch(r"\d{3}/PO-TRANS/MAP/VI/2026", pt.po_number or ""):
            print(f"  [FAIL] PO Transportir {pt.po_number}: format nomor tidak sesuai pola 121/PO-TRANS/MAP/VI/2026")
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