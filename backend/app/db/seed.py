import argparse
import asyncio
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
from sqlalchemy import text
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
from app.models.activity import Activity, ActivityType
from app.utils.activity_logger import model_to_dict


# ── Urutan hapus data (FK-safe: child dulu, parent belakangan) ──
_CLEAR_ORDER = [
    # Level 0: Activity logs third (references users/resources)
    Activity,

    # Level 0: Uploads first (not referenced by others during clear)
    Upload,
    
    # Level 1: Accounting chain
    JournalLine,              # Child of JournalEntry
    JournalEntry,             # Can have journal lines
    
    # Level 2: Documents with FKs
    Invoice,                  # May have accounting entries
    Notification,             # Independent
    
    # Level 3: Document hierarchy (DEEP nesting)
    DeliveryOrder,            # FK to: po_transportir, purchase_order, CUSTOMER
    PurchaseOrder,            # FK to: offering_letter, customer
    PoTransportir,            # FK to: purchase_order
    OfferingLetter,           # FK to: customer
    
    # Level 4: Business records  
    Sale,                     # Independent sales
    
    # Level 5: Financial structure
    Account,                  # Chart of accounts
    
    # Level 6: External entities
    Company,                  # Internal company data
    Supplier,                 # Suppliers
    
    # Level 7: Customers (MUST BE AFTER delivery_orders!)
    Customer,                 # Referenced by delivery_orders, purchase_orders, offering_letters
    
    # Level 8: Users (delete LAST)
    User                      # Referenced by EVERYTHING
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
    await _seed_document_uploads(db)
    await _seed_activities(db)

    await db.commit()
    print("[seed] ✅ Selesai mengisi data:")
    print("   - 5 users")
    print("   - 60 customers")
    print("   - 60 suppliers")
    print("   - 85 offering_letters")
    print("   - 60 purchase_orders")
    print("   - 40 po_transportirs")
    print("   - 85 delivery_orders")
    print("   - 60 invoices")
    print("   - 100 sales")
    print("   - 70+ journal entries")
    print("   - Signatures + profiles")
    print("   - Activities")


async def _seed_activities(db: AsyncSession):
    """Seed catatan aktivitas seluruh entitas sesuai konvensi sistem
    (action create/update/delete via ActivityType, resource_type mengikuti entitas)."""
    print("[seed] Membuat data aktivitas...")

    users = (await db.execute(select(User))).scalars().all()
    if not users:
        print("[seed] Tidak ada user untuk atribusi aktivitas.")
        return

    companies = (await db.execute(select(Company))).scalars().all()
    customers = (await db.execute(select(Customer))).scalars().all()
    suppliers = (await db.execute(select(Supplier))).scalars().all()
    offering_letters = (await db.execute(select(OfferingLetter))).scalars().all()
    purchase_orders = (await db.execute(select(PurchaseOrder))).scalars().all()
    po_transportirs = (await db.execute(select(PoTransportir))).scalars().all()
    delivery_orders = (await db.execute(select(DeliveryOrder))).scalars().all()
    invoices = (await db.execute(select(Invoice))).scalars().all()
    notifications = (await db.execute(select(Notification))).scalars().all()
    journal_entries = (await db.execute(select(JournalEntry))).scalars().all()

    admin = users[0]
    marketing = next((u for u in users if u.role == "marketing"), admin)
    finance = next((u for u in users if u.role == "finance"), admin)
    operations = next((u for u in users if u.role == "operations"), admin)
    accounting = next((u for u in users if u.role == "accounting"), admin)

    span_days = 120
    start = datetime.now() - timedelta(days=span_days)
    activities: list[Activity] = []

    def add(actor, role, action, resource_type, resource_id, resource_name,
            details, days_ago, hour=9, old_data=None, new_data=None) -> None:
        old_values, new_values = Activity.serialize_changes(old_data or {}, new_data or {}, action)
        activities.append(Activity(
            user_id=actor.id,
            actor_name=actor.name,
            actor_role=role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            old_values=old_values,
            new_values=new_values,
            details=details,
            ip_address="10.0.0.1",
            user_agent="Seeder/Mandalan 1.0",
            created_at=start + timedelta(days=span_days - days_ago, hours=hour),
        ))

    def _safe_dict(obj, exclude: set[str] | None = None) -> dict:
        """Snapshot kolom model untuk log, tanpa kolom sensitif."""
        exclude = exclude or set()
        return {
            c.name: getattr(obj, c.name)
            for c in obj.__table__.columns
            if c.name not in exclude
        }

    for i, user in enumerate(users):
        add(admin, "admin", ActivityType.CREATE.value, "user", user.id, user.name,
            f"User {user.name} ({user.role}) ditambahkan ke sistem", 30, 9 + i,
            new_data=_safe_dict(user, {"password", "demo_password"}))

    for i, company in enumerate(companies):
        add(admin, "admin", ActivityType.CREATE.value, "company", company.id, company.name,
            f"Perusahaan {company.name} didaftarkan", 29, 9 + i,
            new_data=model_to_dict(company))
        if i == 0:
            add(admin, "admin", ActivityType.UPDATE.value, "company", company.id, company.name,
                f"Profil perusahaan {company.name} diperbarui", 28, 9,
                old_data=model_to_dict(company),
                new_data={**model_to_dict(company), "abbreviation": "MA Petroleum"})

    for i, customer in enumerate(customers):
        add(marketing, "marketing", ActivityType.CREATE.value, "customer", customer.id, customer.name,
            f"Customer {customer.name} ditambahkan", 27, 10 + i,
            new_data=model_to_dict(customer))
        add(marketing, "marketing", ActivityType.UPDATE.value, "customer", customer.id, customer.name,
            f"Data customer {customer.name} diperbarui", 26, 10 + i,
            old_data={"name": customer.name, "phone": customer.phone},
            new_data={"name": customer.name, "phone": (customer.phone or "") + " ext. 01",
                      "email": customer.email, "city": customer.city})

    for i, supplier in enumerate(suppliers):
        add(admin, "admin", ActivityType.CREATE.value, "supplier", supplier.id, supplier.name,
            f"Supplier {supplier.name} ditambahkan", 25, 9 + i,
            new_data=model_to_dict(supplier))
        add(admin, "admin", ActivityType.UPDATE.value, "supplier", supplier.id, supplier.name,
            f"Data supplier {supplier.name} diperbarui", 24, 9 + i,
            old_data={"name": supplier.name, "bank_account": supplier.bank_account},
            new_data={"name": supplier.name, "bank_account": (supplier.bank_account or "") + "9",
                      "phone": supplier.phone, "email": supplier.email})

    for i, ol in enumerate(offering_letters):
        add(marketing, "marketing", ActivityType.CREATE.value, "offering_letter", ol.id, ol.offering_letter_number,
            f"Surat penawaran {ol.offering_letter_number} dibuat", 22 - i % 5, 9 + i % 8,
            new_data=model_to_dict(ol))

    for i, po in enumerate(purchase_orders):
        add(marketing, "marketing", ActivityType.CREATE.value, "purchase_order", po.id, po.po_number,
            f"Purchase Order {po.po_number} dibuat", 18 - i % 6, 10 + i % 8,
            new_data=model_to_dict(po))
        if i == 0:
            add(admin, "admin", ActivityType.UPDATE.value, "purchase_order", po.id, po.po_number,
                f"Dana Purchase Order {po.po_number} dirilis", 16, 9,
                old_data={"status_rilis_dana": po.status_rilis_dana, "rilis_dana_at": None},
                new_data={"status_rilis_dana": True, "rilis_dana_at": str(start - timedelta(days=14))})

    for i, do in enumerate(delivery_orders):
        add(operations, "operations", ActivityType.CREATE.value, "delivery_order", do.id, do.do_number,
            f"Delivery Order {do.do_number} dibuat", 13 - i % 6, 9 + i % 8,
            new_data=model_to_dict(do))

    for i, pt in enumerate(po_transportirs):
        add(operations, "operations", ActivityType.CREATE.value, "po_transportir", pt.id, pt.po_number,
            f"PO Transportir {pt.po_number} dibuat", 15 - i % 4, 11 + i % 6,
            new_data=model_to_dict(pt))

    for i, note in enumerate(notifications[:5]):
        add(finance, "finance", ActivityType.CREATE.value, "notification", note.id, note.title,
            f"Notifikasi \"{note.title}\" dikirim", 12 - i % 5, 13 + i % 4,
            new_data=model_to_dict(note))

    for i, invoice in enumerate(invoices):
        add(finance, "finance", ActivityType.CREATE.value, "invoice", invoice.id, invoice.invoice_number,
            f"Invoice {invoice.invoice_number} dibuat", 8 - i % 5, 9 + i % 8,
            new_data=model_to_dict(invoice))
        if i == 0:
            add(finance, "finance", ActivityType.UPDATE.value, "invoice", invoice.id, invoice.invoice_number,
                f"Invoice {invoice.invoice_number} dilunasi", 6, 9,
                old_data={"invoice_status": invoice.invoice_status},
                new_data={"invoice_status": "paid"})

    for i, je in enumerate(journal_entries[:10]):
        add(accounting, "accounting", ActivityType.CREATE.value, "journal_entry", je.id, je.entry_number,
            f"Jurnal {je.entry_number} dicatat", 5 - i % 4, 9 + i % 8,
            new_data=model_to_dict(je))

    # ── Siklus hidup tambahan (transisi status dokumen) ────────
    for i, do in enumerate(delivery_orders):
        add(operations, "operations", ActivityType.UPDATE.value, "delivery_order", do.id, do.do_number,
            f"Dana Delivery Order {do.do_number} dirilis", 12 - i % 6, 10 + i % 6,
            old_data={"status_rilis_dana": False, "rilis_dana_at": None},
            new_data={"status_rilis_dana": True,
                      "rilis_dana_at": str(start + timedelta(days=span_days - 12 + i % 6, hours=10 + i % 6))})
        add(operations, "operations", ActivityType.UPDATE.value, "delivery_order", do.id, do.do_number,
            f"Pengantaran DO {do.do_number} disiapkan", 11 - i % 6, 11 + i % 6,
            old_data={"status_ready_order": False, "ready_order_at": None},
            new_data={"status_ready_order": True})
        if i % 3 == 0:
            add(operations, "operations", ActivityType.UPDATE.value, "delivery_order", do.id, do.do_number,
                f"Pengiriman DO {do.do_number} selesai", 10 - i % 6, 12 + i % 6,
                old_data={"status_selesai_dikirim": False, "selesai_dikirim_at": None},
                new_data={"status_selesai_dikirim": True})

    for i, po in enumerate(purchase_orders):
        if po.type == "supplier":
            add(admin, "admin", ActivityType.UPDATE.value, "purchase_order", po.id, po.po_number,
                f"Dana Purchase Order supplier {po.po_number} dirilis", 15 - i % 5, 11 + i % 5,
                old_data={"status_rilis_dana": False, "rilis_dana_at": None},
                new_data={"status_rilis_dana": True})
        else:
            add(marketing, "marketing", ActivityType.UPDATE.value, "purchase_order", po.id, po.po_number,
                f"Purchase Order {po.po_number} direvisi", 14 - i % 5, 10 + i % 5,
                old_data={"status": po.status},
                new_data={"status": "under_revision", "total": po.total})

    for i, inv in enumerate(invoices[1:6]):
        add(finance, "finance", ActivityType.UPDATE.value, "invoice", inv.id, inv.invoice_number,
            f"Invoice {inv.invoice_number} dilunasi", 7 - i % 4, 10 + i % 7,
            old_data={"invoice_status": inv.invoice_status, "deadline_status": inv.deadline_status},
            new_data={"invoice_status": "paid", "deadline_status": "on_time"})

    # ── Riwayat harian rutin (bulk) ─────────────────────────────
    # Aktivitas operasional harian dari semua role untuk memperkaya
    # halaman aktivitas hingga ribuan record.
    actors_cycle = [
        (admin, "admin"),
        (marketing, "marketing"),
        (operations, "operations"),
        (finance, "finance"),
        (accounting, "accounting"),
    ]
    fuel_products = ["Solar Industri (B35)", "Bio Diesel (B35)", "Pertamax", "Pertalite"]
    customer_names = [c.name for c in customers] or ["PT. Surya Tambang Energi"]
    supplier_names = [s.name for s in suppliers] or ["PT. Persada Energi Nusantara"]
    transport_names = ["PT. Armada Kaltim Sejahtera", "CV. Tiga Putra Transport", "PT. Borneo Distribusi Logistik"]

    day_count = 90
    for day in range(1, day_count + 1):
        for a_i, (actor, role) in enumerate(actors_cycle):
            hour = 8 + (day + a_i) % 9
            fuel = fuel_products[(day + a_i) % len(fuel_products)]
            ordinal = (day + a_i) % 7
            amount = 15_000_000 + ((day + a_i) % 30) * 1_000_000

            if ordinal == 0:
                # Update harga produk
                price = 17450 + ((day + a_i) % 40) * 25
                add(actor, role, ActivityType.UPDATE.value, "price",
                    f"PRC-{fuel.replace(' ', '-')}", fuel,
                    f"Harga {fuel} diperbarui menjadi Rp {price:,}", day + 1, hour,
                    old_data={"product_name": fuel, "price": price - 125},
                    new_data={"product_name": fuel, "price": price})
            elif ordinal == 1:
                # Cek akun / chart of accounts
                add(actor, role, ActivityType.CREATE.value, "account",
                    f"ACC-DEMO-{day}-{a_i}", f"Akun Uji {day}.{a_i}",
                    f"Akun uji {day}.{a_i} ditambahkan ke chart of accounts", day + 1, hour,
                    new_data={"code": f"9-{day:03d}{a_i}", "name": f"Akun Uji {day}.{a_i}",
                              "type": "expense", "is_active": True})
            elif ordinal == 2:
                # Upload lampiran dokumen
                add(actor, role, ActivityType.CREATE.value, "upload",
                    f"UPL-DEMO-{day}-{a_i}", f"lampiran-{day}.pdf",
                    f"File lampiran-{day}.pdf di-upload", day + 1, hour,
                    new_data={"original_filename": f"lampiran-{day}.pdf", "folder": "general",
                              "mime_type": "application/pdf", "size": 1024 * 50})
            elif ordinal == 3:
                # Penjualan harian
                add(actor, role, ActivityType.CREATE.value, "sale",
                    f"SALE-DEMO-{day}-{a_i}", f"Penjualan #{day + a_i}",
                    f"Penjualan #{day + a_i} sebesar Rp {amount:,}", day, hour,
                    new_data={"amount": amount, "status": "paid", "email": actor.email})
            elif ordinal == 4:
                # Notifikasi dibaca
                add(actor, role, ActivityType.UPDATE.value, "notification",
                    f"NTF-DEMO-{day}-{a_i}", f"Notifikasi {day + a_i}",
                    f"Notifikasi {day + a_i} ditandai sudah dibaca", day, hour,
                    old_data={"title": f"Notifikasi {day + a_i}", "is_read": False},
                    new_data={"title": f"Notifikasi {day + a_i}", "is_read": True})
            elif ordinal == 5:
                # Data customer dikunjungi/diperbarui
                cname = customer_names[(day + a_i) % len(customer_names)]
                add(actor, role, ActivityType.UPDATE.value, "customer",
                    f"CST-DEMO-{day}-{a_i}", cname,
                    f"Kunjungan/sales call dengan {cname}", day, hour,
                    old_data={"name": cname, "phone": "0541-741231"},
                    new_data={"name": cname, "phone": "0541-741231", "last_contact": str(start.date() + timedelta(days=span_days - day))})
            else:
                # Supplier / transportir dikontak
                sname = supplier_names[(day + a_i) % len(supplier_names)]
                if a_i % 2 == 0:
                    add(actor, role, ActivityType.UPDATE.value, "supplier",
                        f"SUP-DEMO-{day}-{a_i}", sname,
                        f"Data kontak supplier {sname} diperbarui", day, hour,
                        old_data={"name": sname, "phone": "0541-746912"},
                        new_data={"name": sname, "phone": "0541-746912", "email": f"kontak{day}@supplier.co.id"})
                else:
                    tname = transport_names[(day + a_i) % len(transport_names)]
                    add(actor, role, ActivityType.UPDATE.value, "po_transportir",
                        f"PTR-DEMO-{day}-{a_i}", tname,
                        f"Jadwal armada {tname} diperbarui", day, hour,
                        old_data={"transport_name": tname, "schedule": "08:00"},
                        new_data={"transport_name": tname, "schedule": "09:30"})

            # Satu aktivitas tambahan per hari per role (paruh kedua)
            second = (day * 3 + a_i * 5) % 6
            if second == 0:
                add(actor, role, ActivityType.CREATE.value, "offering_letter",
                    f"OL-DEMO-{day}-{a_i}", f"{day:03d}/OL/MAP/2026",
                    f"Surat penawaran {day:03d}/OL/MAP/2026 dibuat", day, hour+1,
                    new_data={"offering_letter_number": f"{day:03d}/OL/MAP/2026",
                              "status": "created", "created_by": actor.id})
            elif second == 1:
                add(actor, role, ActivityType.UPDATE.value, "invoice",
                    f"INV-DEMO-{day}-{a_i}", f"INV/2026/{day}",
                    f"Invoice INV/2026/{day} ditandai lunas", day, hour+1,
                    old_data={"invoice_status": "unpaid", "deadline_status": "due_soon"},
                    new_data={"invoice_status": "paid", "deadline_status": "on_time"})
            elif second == 2:
                add(actor, role, ActivityType.CREATE.value, "purchase_order",
                    f"PO-DEMO-{day}-{a_i}", f"PO/2026/{day}",
                    f"Purchase Order PO/2026/{day} dibuat", day, hour+1,
                    new_data={"po_number": f"PO/2026/{day}", "type": "customer",
                              "status": "created", "total": amount})
            elif second == 3:
                add(actor, role, ActivityType.UPDATE.value, "account",
                    f"ACC-DEMO2-{day}-{a_i}", "Bank BCA",
                    "Saldo Bank BCA direkonsiliasi", day, hour+1,
                    old_data={"balance": 50_000_000},
                    new_data={"balance": 50_000_000 + ((day + a_i) % 20) * 1_000_000})
            elif second == 4:
                add(actor, role, ActivityType.DELETE.value, "sale",
                    f"SALE-DEL-{day}-{a_i}", f"Penjualan batal #{day + a_i}",
                    f"Penjualan #{day + a_i} dibatalkan", day, hour+1,
                    old_data={"amount": amount, "status": "failed"})
            else:
                add(actor, role, ActivityType.CREATE.value, "upload",
                    f"UPL2-DEMO-{day}-{a_i}", f"dokumentasi-{day}.png",
                    f"Foto dokumentasi {day}.png di-upload", day, hour+1,
                    new_data={"original_filename": f"dokumentasi-{day}.png",
                              "folder": "delivery_order", "mime_type": "image/png"})

    for activity in activities:
        db.add(activity)
    await db.flush()
    print(f"[seed] ✅ Membuat {len(activities)} data aktivitas")


async def _seed_offering_letters(db: AsyncSession):
    """Generate 80+ surat penawaran dengan variasi realistis."""
    print("[seed] Generating 80 offering letters...")
    
    result = await db.execute(select(Customer))
    customers = result.scalars().all()
    
    if not customers:
        print("[seed] Warning: No customers found, skipping OL generation")
        return
    
    ol_numbers = [f"{i + 1:03d}/OL/VI/2026" for i in range(85)]
    
    creator_result = await db.execute(select(User).where(User.role == "marketing"))
    marketing_user = creator_result.scalars().first()
    
    today = datetime.now()
    statuses = ["created", "under_revision", "po_received"]
    
    for i, ol_number in enumerate(ol_numbers):
        customer = customers[i % len(customers)]
        fuel_price = round(17450 + ((i * 150) % 2000))
        transport_price = round(2500000 + (i * 100000))
        
        ol = OfferingLetter(
            id=str(uuid.uuid4()),
            offering_letter_number=ol_number,
            customer_id=customer.id,
            location=["Balikpapan", "Samarinda", "Tenggarong", "Tarakan"][i % 4],
            date=(today - timedelta(days=i % 90)).strftime("%Y-%m-%d"),
            regarding="Penawaran Harga BBM Solar Industri",
            receiver=customer.name,
            fuel_total_price=fuel_price,
            transport_price=transport_price,
            status=statuses[i % len(statuses)],
            created_by=marketing_user.id if marketing_user else None,
            details=_ol_details(ol_number, customer.name, customer.address or "", fuel_price, transport_price)
        )
        db.add(ol)
    
    await db.flush()
    print(f"[seed] Added {len(ol_numbers)} offering letters.")


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
    """Clear all data with FK constraints temporarily disabled."""
    
    print("[seed] Clearing all data...")
    
    # Disable foreign key checks to avoid constraint violations during bulk delete
    await db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    
    try:
        for model in _CLEAR_ORDER:  # Forward order is fine with FK disabled
            result = await db.execute(select(model))
            rows = result.scalars().all()
            if rows:
                print(f"[seed] Deleting {model.__tablename__} ({len(rows)} records)")
                for row in rows:
                    await db.delete(row)
        
        # Flush changes
        await db.flush()
        
    finally:
        # Re-enable foreign key checks
        await db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        
        print("[seed] ✅ All data cleared successfully!")




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
    """Generate 50+ customers dengan variasi realistis."""
    print("[seed] Generating 50 customers...")
    base_names = [
        "PT. Surya Tambang Energi", "CV. Kaltim Jaya Abadi", "PT. Borneo Energi Utama",
        "CV. Mulia Gemawan", "PT. Adaro Mining", "PT. Bayan Resources", "CV. Mitra Perkasa",
        "PT. Arutmin Indonesia", "CV. Bintang Kalimantan", "PT. Bukit Asam",
        "PT. Indika Energy", "CV. Jaya Makmur", "PT. KPC (Kentet Coal)", "CV. Lestari Sejahtera",
        "PT. Mega Persada", "CV. Nusa Perkasa", "PT. Oliver Global", "CV. Prima Abadi",
        "PT. Qolbu Mandiri", "CV. Raya Sentosa", "PT. Sigma Mineral", "CV. Tani Baru",
        "PT. Universal Energy", "CV. Victoria Sukses", "PT. Wira Usaha", "CV. Xanadu Group",
        "PT. Yamaha Industry", "CV. Yapen Jaya", "PT. Zion Capital", "CV. Abadi Karya"
    ]
    
    # Extend to exactly 60 customers
    names = base_names + [f"PT. Customer Test {i} {chr(65 + (i % 26))}" for i in range(30)]
    
    companies_list = [
        ("PT. Mitra Andalan Petroleum", "MAP"),
        ("PT. Pertamina Hulu Energi", "PHE"),
        ("PT. Total E&P Indonesia", "TEPI")
    ]
    
    cities = ["Samarinda", "Balikpapan", "Tenggarong", "Mahakam Ulu", "Passi", "Tarakan", "Bontang"]
    provinces = ["Kalimantan Timur", "Kalimantan Utara", "Kelurahan", "Malaysia", "Brunei"]
    
    customers = []
    for i, name in enumerate(names[:60]):
        c = Customer(
            name=name,
            npwp=f"{i + 1:02}.{i % 100:03d}.{i % 1000:03d}-091",
            address=f"Jl. Raya No. {100 + i}, Kelurahan {name.split()[-1]}",
            province=provinces[i % len(provinces)],
            city=cities[i % len(cities)],
            phone=f"05{4 + (i % 2)}{1}-{i + 1:04d}{i + 1:02d}",
            phone2=f"08{i + 1:02} {123 + (i % 9):04d} {456 + (i % 6):04d}",
            email=f"contact@{name.lower().replace(' ', '').replace('.', '')}.co.id" if i < 30 else f"admin{i}@test.com",
        )
        customers.append(c)
    
    for c in customers:
        db.add(c)
    await db.flush()
    print(f"[seed] Added {len(customers)} customers.")


# ── Suppliers ──────────────────────────────────────────────────

async def _seed_suppliers(db: AsyncSession):
    """Generate 60+ suppliers dengan variasi realistis."""
    print("[seed] Generating 60 suppliers...")
    
    # Extended supplier names - need at least 60
    names = [
        "PT. Persada Energi Nusantara", "CV. Sinar Petrolindo", "PT. Borneo Logistik Utama",
        "CV. Mandiri Transports", "PT. Kalimantan Sejahtera", "CV. Nusa Transport",
        "PT. Artha Graha Prima", "CV. Barata Jaya", "PT. Citra Mulia Perkasa", "CV. Darma Sentosa",
        "PT. Edelweiss Group", "CV. Fauzan Logistics", "PT. Garuda Abadi", "CV. Hendra Karya",
        "PT. Indoprima Makmur", "CV. Jasa Marga", "PT. Karyapersada Prima", "CV. Langit Biru",
        "PT. Mitra Usaha", "CV. Negeri Baru", "PT. Ocean Shipping", "CV. Permata Indah",
        "PT. Queen Shipping", "CV. Raya Mandiri", "PT. Satya Nugraha", "CV. Tri Utama",
        "PT. Ujung Pandang", "CV. Ventura Global", "PT. Wangi Logistics", "CV. Xerxes Corp",
        "PT. Yasmin Energy", "CV. Zaina Trade", "PT. Alpha Transport", "CV. Beta Services",
        "PT. Gamma Trading", "CV. Delta Express", "PT. Epsilon Power", "CV. Zeta Logistics",
        "PT. Eta Shipping", "CV. Theta Cargo", "PT. Iota Energy", "CV. Kappa Fuel",
        "PT. Lambda Oil", "CV. Mu Transport", "PT. Nu Shipping", "CV. Xi Cargo",
        "PT. Omicron Power", "CV. Pi Trading", "PT. Rho Energy", "CV. Sigma Fuel",
        "PT. Tau Logistics", "CV. Upsilon Trade", "PT. Phi Shipping", "CV. Chi Cargo",
        "PT. Psi Power", "CV. Omega Fuel",
        "PT. Alpha Sinar Mandiri", "CV. Bima Sakti Logistik", "PT. Cakra Petroleum", "CV. Damai Sejahtera"
    ]
    
    companies_list = [
        ("PT. Mitra Andalan Petroleum", "MAP"),
        ("PT. Pertamina Hulu Energi", "PHE"),
        ("PT. Total E&P Indonesia", "TEPI")
    ]
    
    cities = ["Samarinda", "Balikpapan", "Tenggarong", "Mahakam Ulu", "Tarakan"]
    provinces = ["Kalimantan Timur", "Kalimantan Utara", "Malaysia", "Brunei"]
    
    bank_names = ["BCA", "BRI", "BNI", "MANDIRI", "CIMB Niaga", "BTN"]
    bank_accounts = [f"{2881306571 + i * 1000:09d}" for i in range(6)]
    
    suppliers = []
    for i, name in enumerate(names[:60]):
        s = Supplier(
            name=name,
            npwp=f"{i + 1:02}.{i % 100:03d}.{i % 1000:03d}-091",
            address=f"Jl. Bisnis No. {200 + i}, {name.split()[-1]} Business Park",
            province=provinces[i % len(provinces)],
            city=cities[i % len(cities)],
            phone=f"0{5 + (i % 2)}{4}{1}-{i + 1:04d}{i + 1:02d}",
            phone2=f"08{i + 1:02} {234 + (i % 9):04d} {567 + (i % 6):04d}",
            email=f"sales@{name.lower().replace(' ', '').replace('.', '')}.com" if i < 40 else f"supplier{i}@test.com",
            bank_name=bank_names[i % len(bank_names)],
            bank_account=bank_accounts[i % len(bank_accounts)]
        )
        suppliers.append(s)
    
    for s in suppliers:
        db.add(s)
    await db.flush()
    print(f"[seed] Added {len(suppliers)} suppliers.")


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



# ── Purchase Orders ────────────────────────────────────────────

async def _seed_purchase_orders(db: AsyncSession):
    """Generate 60+ purchase orders (customer + supplier)."""
    print("[seed] Generating 60 purchase orders...")
    
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
    
    pos = []
    # PO Customer - 35 records
    for i in range(35):
        customer = customers[i % len(customers)]
        po_number = f"PO/2026/VI/{100 + i}"
        fuel_price = round(17450 + ((i * 200) % 3000))
        qty = 8000 + (i * 500)
        products = [{
            "name": ["Solar Industri (B35)", "Bio Diesel (B35)"][i % 2],
            "qty": qty, "unit": "Liter", 
            "price": fuel_price, 
            "totalPrice": qty * fuel_price
        }]
        
        status_options = ["created", "under_revision", "po_received", "approved"]
        status = status_options[i % len(status_options)]
        
        po = PurchaseOrder(
            po_number=po_number,
            type="customer",
            customer_id=customer.id,
            date=(datetime(2026, 6, 1) + timedelta(days=i % 30)).strftime("%Y-%m-%d"),
            total=sum(p["totalPrice"] for p in products),
            status=status,
            created_by=marketing_user.id if marketing_user else None,
            details=_po_details(main_company, {
                "id": customer.id, "name": customer.name, "npwp": customer.npwp,
                "address": customer.address, "contactPerson": customer.phone, "email": customer.email
            }, po_number, products),
        )
        pos.append(po)
        db.add(po)
    
    # PO Supplier - 25 records  
    for i in range(25):
        supplier = suppliers[i % len(suppliers)]
        po_number = f"PO-SUP/2026/VI/{200 + i}"
        fuel_price = round(15000 + ((i * 150) % 2000))
        qty = 10000 + (i * 300)
        products = [{
            "name": "Solar Industri (B35)",
            "qty": qty, "unit": "Liter", 
            "price": fuel_price, 
            "totalPrice": qty * fuel_price,
            "ppkb": 0, "pph": 0.005, "ppn": 0.11 * qty * fuel_price
        }]
        
        rilis = i % 3 == 0
        po = PurchaseOrder(
            po_number=po_number,
            type="supplier",
            supplier_id=supplier.id,
            date=(datetime(2026, 6, 1) + timedelta(days=i % 30)).strftime("%Y-%m-%d"),
            total=sum(p["totalPrice"] for p in products),
            status="created",
            created_by=marketing_user.id if marketing_user else None,
            rilis_dana_at=datetime(2026, 6, 3, 9, 0, 0) if rilis else None,
            status_rilis_dana=rilis,
            details=_po_details(main_company, {
                "id": supplier.id, "name": supplier.name, "npwp": "",
                "address": supplier.address or "", "contactPerson": supplier.phone or "", "email": supplier.email or ""
            }, po_number, products),
        )
        pos.append(po)
        db.add(po)
    
    await db.flush()
    
    # Link some POs to OLs
    ols = (await db.execute(select(OfferingLetter))).scalars().all()
    if ols and len(pos) >= 2:
        for i in range(min(10, len(pos))):
            pos[i].id_offering_letters = json.dumps([ols[j].id for j in range(i % min(5, len(ols)))])
        await db.flush()
    
    print(f"[seed] Added {len(pos)} purchase orders ({len([p for p in pos if p.type=="customer"])} customer, {len([p for p in pos if p.type=="supplier"])} supplier)")


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

    print("[seed] Generating 85 delivery orders...")
    
    for i in range(85):
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
    print("[seed] Added 85 delivery orders")


# ── Invoices ───────────────────────────────────────────────────

async def _seed_invoices(db: AsyncSession):
    customers = (await db.execute(select(Customer))).scalars().all()
    pos = (await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.type == "customer")
    )).scalars().all()
    customer_by_id = {c.id: c for c in customers}
    statuses = ["unpaid", "paid", "overdue"]
    deadlines = ["on_time", "overdue", "due_soon"]
    
    print("[seed] Generating 60 invoices...")
    
    for i in range(60):
        # Cycle through POs but add more variety
        po_idx = i % len(pos) if pos else 0
        po = pos[po_idx]
        customer_by_id = {c.id: c for c in customers}
        customer = customer_by_id.get(po.customer_id) or customers[i % len(customers)]
        sub_total = 8000 * 17950
        grand_total = round(sub_total * 1.11)
        products = [
            {"qty": 8000, "unit": "Liter", "name": "Solar Industri (B35)", "price": 17950, "totalPrice": sub_total}
        ]
        do_numbers = [f"DO/2026/MAP-{i+1:03d}"]
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
            invoice_number=f"INV/2026/VI/{i+1:03d}",
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
    print("[seed] Added 60 invoices")


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

    print("[seed] Generating 40 PO transportir...")
    
    receivers = ["PT. Armada Kaltim Sejahtera", "CV. Tiga Putra Transport", "PT. Borneo Distribusi Logistik", 
                 "CV. Sinar Jaya Abadi", "PT. Mitra Logistik Utama"]
    discharge_places = ["Site MHU - Kutai Kartanegara", "Site TDM / Separi - Kutai Kartanegara", 
                       "Pelabuhan Balongan", "Terminal BBM Tenggarong", "Depot SAMARinda"]
    statuses = ["created", "processing", "in_transit", "completed", "cancelled"]
    
    records = []
    for i in range(40):
        po_number = f"{121 + i}/PO-TRANS/MAP/VI/2026"
        po_date = f"2026-{6 + (i//30):02d}-{1 + (i%28):02d}"
        receiver = receivers[i % len(receivers)]
        products = [{
            "name": ["Solar", "Bio Diesel"][i % 2],
            "loadingDate": po_date, 
            "unloadingDate": f"2026-{6 + (i//30):02d}-{1 + (i%28) + 1:02d}",
            "qty": 8000 + (i * 200), 
            "ratePrice": 450 + ((i % 7) * 25), 
            "totalPrice": (8000 + (i * 200)) * (450 + ((i % 7) * 25))
        }]
        discharge = discharge_places[i % len(discharge_places)]
        status = statuses[i % len(statuses)]
        records.append((po_number, po_date, receiver, products, discharge, status))

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
    print("[seed] Generating 100 sales...")
    users_emails = {
        "admin": "admin@mapetroleum.co.id",
        "marketing": "marketing@mapetroleum.co.id", 
        "finance": "finance@mapetroleum.co.id",
        "operations": "ops@mapetroleum.co.id",
        "accounting": "accounting@mapetroleum.co.id"
    }
    roles = list(users_emails.keys())
    statuses = ["paid", "pending", "failed", "refunded"]
    
    sales = []
    for i in range(100):
        role = roles[i % len(roles)]
        sale = Sale(
            date=f"2026-{1 + (i // 12):02d}-{1 + (i % 28):02d}",
            status=statuses[i % len(statuses)],
            email=users_emails[role],
            amount=20000000 + (i * 1000000) % 80000000
        )
        sales.append(sale)
    
    for s in sales:
        db.add(s)
    await db.flush()
    print(f"[seed] Added {len(sales)} sales")


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

    # Generate 70+ journal entries - use the 10 base templates cycled with variation
    base_templates = [
        (kas, piutang, pendapatan, ongkir, beban_operasional, beban_transport, beban_gaji, beban_listrik_air, kas_kecil, bank),
    ]
    descriptions = [
        "Penjualan BBM tunai", "Penjualan BBM kredit", "Pembayaran jasa angkut transportir",
        "Penerimaan pembayaran piutang", "Pembayaran beban operasional", "Pendapatan jasa angkut tunai",
        "Pendapatan jasa angkut dibayar tunai", "Pembayaran beban listrik & air", "Pembayaran gaji karyawan",
        "Penjualan BBM kredit", "Pembayaran beban transport", "PNBP penyimpanan terminal",
    ]
    entry_count = 0
    for i in range(70):
        month = 6 + (i // 15)
        day = 1 + (i % 28)
        try:
            ed = date(2026, month, day)
        except ValueError:
            ed = date(2026, month, 28)
        tpl = i % 10
        acct_a, acct_b = None, None
        if tpl == 0:   acct_a, acct_b = kas, pendapatan
        elif tpl == 1: acct_a, acct_b = piutang, pendapatan
        elif tpl == 2: acct_a, acct_b = beban_transport, kas
        elif tpl == 3: acct_a, acct_b = bank, piutang
        elif tpl == 4: acct_a, acct_b = beban_operasional, kas
        elif tpl == 5: acct_a, acct_b = kas, ongkir
        elif tpl == 6: acct_a, acct_b = kas, ongkir
        elif tpl == 7: acct_a, acct_b = beban_listrik_air, kas_kecil
        elif tpl == 8: acct_a, acct_b = beban_gaji, bank
        else:          acct_a, acct_b = piutang, pendapatan
        amount = 5_000_000 + ((i * 350_000) % 45_000_000)
        entry_number = f"JRM-2026{month:02d}-{i + 1:04d}"
        reference = f"REF-2026/{month:02d}/{i+1:03d}"
        desc = descriptions[i % len(descriptions)]
        entry = JournalEntry(
            entry_number=entry_number,
            entry_date=ed,
            description=desc,
            reference=reference,
            status="posted" if i % 5 != 3 else "draft",
        )
        db.add(entry)
        await db.flush()
        db.add(JournalLine(journal_entry_id=entry.id, account_id=acct_a.id, debit=amount, credit=0))
        db.add(JournalLine(journal_entry_id=entry.id, account_id=acct_b.id, debit=0, credit=amount))
        entry_count += 1
    await db.flush()
    print(f"[seed] Added {entry_count} journal entries")


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


async def _seed_document_uploads(db: AsyncSession):
    """Generate 50+ file upload (PDF/PNG) untuk DO/OL/PO/Invoice untuk
    memperkaya halaman uploads dan riwayat aktivitas upload."""
    print("[seed] Generating 50 document uploads...")
    users = (await db.execute(select(User))).scalars().all()
    admin = users[0] if users else None
    docs = [
        ("delivery_order", "DO"),
        ("ol", "OL"),
        ("po", "PO"),
        ("invoice", "INV"),
    ]
    media_dir = Path(__file__).resolve().parent.parent.parent / "media"
    count = 0
    for i in range(50):
        doc_type, prefix = docs[i % len(docs)]
        folder = doc_type
        folder_dir = media_dir / folder
        folder_dir.mkdir(parents=True, exist_ok=True)
        stored = f"{uuid.uuid4().hex}.pdf"
        content = (
            "%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            "2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            "trailer<</Root 1 0 R>>\n%%EOF"
        ).encode()
        (folder_dir / stored).write_bytes(content)
        db.add(Upload(
            original_filename=f"{prefix}_{i + 1:03d}_document.pdf",
            stored_filename=stored,
            folder=folder,
            mime_type="application/pdf",
            size=len(content),
            url=f"/media/{folder}/{stored}",
            document_type=doc_type,
            document_id=str(uuid.uuid4()),
        ))
        count += 1
    await db.flush()
    print(f"[seed] Added {count} document uploads.")


# ── Verifikasi pola hasil seed (CLI --check) ───────────────────

async def _check_seed(db: AsyncSession) -> bool:
    """Periksa jumlah data dan pola relasi antar dokumen hasil seed."""
    async def count(model) -> int:
        return len((await db.execute(select(model))).scalars().all())

    all_ok = True

    print("[seed] Jumlah data:")
    for name, actual, expected in [
        ("users", await count(User), 5),
        ("customers", await count(Customer), 60),
        ("suppliers", await count(Supplier), 60),
        ("offering_letters", await count(OfferingLetter), 85),
        ("purchase_orders", await count(PurchaseOrder), 60),
        ("delivery_orders", await count(DeliveryOrder), 85),
        ("invoices", await count(Invoice), 60),
        ("po_transportir", await count(PoTransportir), 40),
        ("accounts", await count(Account), 21),
        ("journal_entries", await count(JournalEntry), 70),
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