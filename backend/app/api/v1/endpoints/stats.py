from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.offering_letter import OfferingLetter
from app.models.delivery_order import DeliveryOrder
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.notification import Notification
from app.models.purchase_order import PurchaseOrder
from app.models.sale import Sale
from app.models.supplier import Supplier
from app.models.upload import Upload
from app.models.user import User
from app.schemas.stats import (
    AdminActivity,
    AdminBreakdown,
    AdminDrilldownItem,
    AdminDrilldownResponse,
    AdminMetric,
    AdminStatsResponse,
    AdminTrend,
    RevenuePoint,
    RevenueResponse,
    SingleStat,
    StatsResponse,
)

router = APIRouter()


@router.get(
    "/stats/marketing",
    response_model=StatsResponse,
    summary="Marketing dashboard stats",
    description="Statistik untuk dashboard marketing: total penawaran, pending, PO customer, PO logistik.",
)
async def marketing_stats(db: AsyncSession = Depends(get_db)):
    total_ol = await _count(db, select(OfferingLetter))
    pending_ol = await _count(db, select(OfferingLetter).where(OfferingLetter.status == "created"))
    po_customer = await _count(db, select(OfferingLetter).where(OfferingLetter.status == "po_received"))
    po_logistik = await _count(db, select(OfferingLetter).where(OfferingLetter.status == "under_revision"))

    return StatsResponse(stats=[
        SingleStat(title="Penawaran dibuat", icon="i-lucide-file-text", value=total_ol, variation=await _variation(db, OfferingLetter), to="/marketing/customer"),
        SingleStat(title="Penawaran belum disetujui", icon="i-lucide-clock", value=pending_ol, variation=await _variation(db, OfferingLetter, OfferingLetter.status == "created"), to="/marketing/customer"),
        SingleStat(title="PO dari Customer", icon="i-lucide-shopping-cart", value=po_customer, variation=await _variation(db, OfferingLetter, OfferingLetter.status == "po_received"), to="/marketing/customer"),
        SingleStat(title="PO untuk logistik", icon="i-lucide-truck", value=po_logistik, variation=await _variation(db, OfferingLetter, OfferingLetter.status == "under_revision"), to="/marketing/supplier"),
    ])


@router.get(
    "/stats/operations",
    response_model=StatsResponse,
    summary="Operations dashboard stats",
    description="Statistik untuk dashboard operations: total DO.",
)
async def operations_stats(db: AsyncSession = Depends(get_db)):
    total_do = await _count(db, select(DeliveryOrder))

    return StatsResponse(stats=[
        SingleStat(title="Delivery Order Dibuat", icon="i-lucide-file-text", value=total_do, variation=await _variation(db, DeliveryOrder), to="/operations"),
    ])


@router.get(
    "/stats/finance",
    response_model=StatsResponse,
    summary="Finance dashboard stats",
    description="Statistik untuk dashboard finance: DO diterima, invoice belum dibuat, invoice belum lunas.",
)
async def finance_stats(db: AsyncSession = Depends(get_db)):
    do_diterima = await _count(db, select(DeliveryOrder))
    unpaid = await _count(db, select(Invoice).where(Invoice.invoice_status == "unpaid"))
    total_invoice = await _count(db, select(Invoice))
    invoice_belum = total_invoice - unpaid

    return StatsResponse(stats=[
        SingleStat(title="DO Diterima", icon="i-lucide-file-check", value=do_diterima, variation=await _variation(db, DeliveryOrder), to="/finance/do"),
        SingleStat(title="Invoice Belum Dibuat", icon="i-lucide-file-minus", value=invoice_belum, variation=await _variation(db, Invoice, Invoice.invoice_status != "unpaid"), to="/finance/invoice"),
        SingleStat(title="Invoice Belum Lunas", icon="i-lucide-alert-circle", value=unpaid, variation=await _variation(db, Invoice, Invoice.invoice_status == "unpaid"), to="/finance/invoice/data-invoice-customer"),
    ])


@router.get(
    "/stats/home",
    response_model=StatsResponse,
    summary="Home dashboard stats",
    description="Statistik halaman utama: total customer, revenue, orders.",
)
async def home_stats(db: AsyncSession = Depends(get_db)):
    # Hitung customer unik dari offering letter tanpa DISTINCT ON (yang hanya
    # didukung PostgreSQL) agar konsisten di MySQL/SQLite.
    total_customers_result = await db.execute(
        select(func.count(func.distinct(OfferingLetter.customer_id)))
    )
    total_customers = total_customers_result.scalar() or 0
    total_revenue_result = await db.execute(select(func.coalesce(func.sum(Invoice.grand_total), 0)))
    total_revenue = total_revenue_result.scalar() or 0
    total_ol = await _count(db, select(OfferingLetter))

    return StatsResponse(stats=[
        SingleStat(title="Customers", icon="i-lucide-users", value=total_customers, variation=await _variation(db, OfferingLetter, None, func.count(func.distinct(OfferingLetter.customer_id))), to="/marketing/customer"),
        SingleStat(title="Revenue", icon="i-lucide-trending-up", value=total_revenue, variation=await _variation(db, Invoice, None, func.sum(Invoice.grand_total)), to="/finance"),
        SingleStat(title="Orders", icon="i-lucide-shopping-bag", value=total_ol, variation=await _variation(db, OfferingLetter), to="/operations"),
    ])


@router.get(
    "/stats/revenue",
    response_model=RevenueResponse,
    summary="Revenue time series",
    description="Revenue (jumlah grand total invoice) per periode: daily, weekly, atau monthly.",
)
async def revenue_stats(
    period: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    start, end = _range(date_from, date_to)
    invoices = await _records(db, Invoice, start, end)

    def _bucket_key(created_at):
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if period == "monthly":
            return created_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if period == "weekly":
            # datetime.weekday() 0-6 (Senin=0); isocalendar().weekday() 1-7
            # (Senin=1) salah dipakai sebelumnya sehingga bucket jatuh di Minggu.
            first_weekday = created_at - timedelta(days=created_at.weekday())
            return first_weekday.replace(hour=0, minute=0, second=0, microsecond=0)
        return created_at.replace(hour=0, minute=0, second=0, microsecond=0)

    totals: dict[datetime, float] = {}
    for invoice in invoices:
        key = _bucket_key(invoice.created_at)
        totals[key] = totals.get(key, 0.0) + (invoice.grand_total or 0)

    step = {"daily": timedelta(days=1), "weekly": timedelta(days=7), "monthly": None}[period]
    points = []
    cursor = _bucket_key(start)
    while cursor <= end:
        amount = totals.get(cursor, 0.0)
        if period == "monthly":
            next_cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
            label = cursor.strftime("%b %Y")
        else:
            next_cursor = cursor + step
            label = cursor.strftime("%d %b")
        points.append(RevenuePoint(date=cursor.date().isoformat(), label=label, amount=amount))
        cursor = next_cursor

    return RevenueResponse(period=period, start=start, end=end, points=points)


async def _count(db, stmt):
    result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    return result.scalar() or 0


async def _variation(db, model, where=None, aggregate=None):
    now = datetime.now(timezone.utc)
    cur_start = now - timedelta(days=30)
    prev_start = now - timedelta(days=60)

    async def _measure(start, end):
        # Bangun query agregat langsung dari tabel model (bukan subquery)
        # agar tidak terjadi cartesian product antara subquery anon_1 dan
        # tabel model (aggregate mereferensikan kolom model langsung).
        if aggregate is None:
            stmt = select(func.count()).select_from(model)
        else:
            stmt = select(aggregate)
        stmt = stmt.where(model.created_at >= start, model.created_at < end)
        if where is not None:
            stmt = stmt.where(where)
        result = await db.execute(stmt)
        return result.scalar() or 0

    current = await _measure(cur_start, now)
    previous = await _measure(prev_start, cur_start)
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 1)


def _range(date_from: datetime | None, date_to: datetime | None):
    now = datetime.now(timezone.utc)
    start = date_from or now - timedelta(days=30)
    end = date_to or now
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    if start > end:
        start, end = end, start
    return start, end


def _created_between(model, start, end):
    return select(model).where(model.created_at >= start, model.created_at <= end)


async def _records(db: AsyncSession, model, start, end):
    return list((await db.execute(_created_between(model, start, end))).scalars().all())


def _breakdown(records, attribute: str):
    counts = Counter((getattr(record, attribute, None) or "unknown") for record in records)
    return [
        AdminBreakdown(key=str(key), label=str(key).replace("_", " ").title(), value=value)
        for key, value in sorted(counts.items())
    ]


def _activity(domain: str, title: str, subtitle: str, created_at, to: str | None = None):
    return AdminActivity(domain=domain, title=title, subtitle=subtitle, created_at=created_at, to=to)


@router.get(
    "/stats/admin",
    response_model=AdminStatsResponse,
    summary="Complete admin system analytics",
)
async def admin_stats(
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    start, end = _range(date_from, date_to)
    customers = await _records(db, Customer, start, end)
    suppliers = await _records(db, Supplier, start, end)
    users = await _records(db, User, start, end)
    ols = await _records(db, OfferingLetter, start, end)
    pos = await _records(db, PurchaseOrder, start, end)
    dos = await _records(db, DeliveryOrder, start, end)
    invoices = await _records(db, Invoice, start, end)
    sales = await _records(db, Sale, start, end)
    notifications = await _records(db, Notification, start, end)
    uploads = await _records(db, Upload, start, end)
    customer_pos = [record for record in pos if record.type == "customer"]
    supplier_pos = [record for record in pos if record.type == "supplier"]
    paid = [record for record in invoices if record.invoice_status == "paid"]
    outstanding = [record for record in invoices if record.invoice_status in {"unpaid", "overdue"}]
    overdue = [record for record in invoices if record.invoice_status == "overdue" or record.deadline_status == "overdue"]
    metrics = [
        AdminMetric(key="customers", title="Customer", value=len(customers), icon="i-lucide-users", description="Customer dibuat dalam periode aktif."),
        AdminMetric(key="suppliers", title="Supplier", value=len(suppliers), icon="i-lucide-building-2", description="Supplier dibuat dalam periode aktif."),
        AdminMetric(key="users", title="User", value=len(users), icon="i-lucide-user-round", description="Profile user dibuat dalam periode aktif."),
        AdminMetric(key="offering_letters", title="Surat Penawaran", value=len(ols), icon="i-lucide-file-text", description="Total offering letter dibuat dalam periode aktif."),
        AdminMetric(key="customer_purchase_orders", title="PO Customer", value=len(customer_pos), icon="i-lucide-shopping-cart", description="Purchase order dengan type customer."),
        AdminMetric(key="supplier_purchase_orders", title="PO Supplier", value=len(supplier_pos), icon="i-lucide-truck", description="Purchase order dengan type supplier."),
        AdminMetric(key="delivery_orders", title="Delivery Order", value=len(dos), icon="i-lucide-package-check", description="Delivery order dibuat dalam periode aktif."),
        AdminMetric(key="fuel_volume", title="Volume DO", value=sum(record.fuel_total or 0 for record in dos), unit="volume", icon="i-lucide-fuel", description="Akumulasi fuel_total dari semua delivery order."),
        AdminMetric(key="invoice_value", title="Nilai Tagihan", value=sum(record.grand_total or 0 for record in invoices), unit="currency", icon="i-lucide-receipt-text", description="Akumulasi grand total seluruh invoice."),
        AdminMetric(key="paid_value", title="Nilai Terbayar", value=sum(record.grand_total or 0 for record in paid), unit="currency", icon="i-lucide-circle-check", description="Akumulasi invoice berstatus paid."),
        AdminMetric(key="outstanding_value", title="Piutang Berjalan", value=sum(record.grand_total or 0 for record in outstanding), unit="currency", icon="i-lucide-clock-3", description="Akumulasi invoice unpaid dan overdue."),
        AdminMetric(key="overdue_value", title="Piutang Overdue", value=sum(record.grand_total or 0 for record in overdue), unit="currency", icon="i-lucide-alert-triangle", description="Akumulasi invoice atau deadline berstatus overdue."),
        AdminMetric(key="sales_value", title="Nilai Sales", value=sum(record.amount or 0 for record in sales), unit="currency", icon="i-lucide-chart-no-axes-combined", description="Akumulasi amount transaksi sales."),
        AdminMetric(key="unread_notifications", title="Notifikasi Belum Dibaca", value=sum(not record.is_read for record in notifications), icon="i-lucide-bell", description="Notification is_read=false dalam periode aktif."),
        AdminMetric(key="uploads", title="Upload", value=len(uploads), icon="i-lucide-paperclip", description="File upload dibuat dalam periode aktif."),
    ]
    cursor = start.replace(hour=0, minute=0, second=0, microsecond=0)
    trends = []
    while cursor <= end:
        next_cursor = cursor + timedelta(days=7)
        label = f"{cursor.strftime('%d %b')}"
        bucket = lambda records: [item for item in records if cursor <= item.created_at.replace(tzinfo=timezone.utc) < next_cursor]
        trends.append(AdminTrend(
            key=cursor.date().isoformat(), label=label,
            offering_letters=len(bucket(ols)), purchase_orders=len(bucket(pos)),
            delivery_orders=len(bucket(dos)), invoices=len(bucket(invoices)),
            sales_amount=sum(item.amount or 0 for item in bucket(sales)),
        ))
        cursor = next_cursor
    activities = []
    for domain, records, number, route in [
        ("OL", ols, "offering_letter_number", "/admin/marketing"),
        ("PO", pos, "po_number", "/admin/marketing"),
        ("DO", dos, "do_number", "/admin/operations"),
        ("Invoice", invoices, "invoice_number", "/admin/finance"),
    ]:
        for record in records:
            activities.append(_activity(domain, getattr(record, number), getattr(record, "status", None) or getattr(record, "invoice_status", "created"), record.created_at, route))
    activities.sort(key=lambda item: item.created_at or start, reverse=True)
    return AdminStatsResponse(
        date_from=start, date_to=end, metrics=metrics, trends=trends,
        distributions={
            "offering_letters": _breakdown(ols, "status"),
            "purchase_orders": _breakdown(pos, "type"),
            "delivery_orders": _breakdown(dos, "status"),
            "invoices": _breakdown(invoices, "invoice_status"),
            "invoice_deadlines": _breakdown(invoices, "deadline_status"),
            "users": _breakdown(users, "role"),
            "notifications": _breakdown(notifications, "type"),
            "uploads": _breakdown(uploads, "document_type"),
        },
        notifications=[_activity("Notification", item.title, item.message, item.created_at, item.to) for item in sorted(notifications, key=lambda item: item.created_at, reverse=True)[:10]],
        activities=activities[:12],
    )


@router.get("/stats/admin/drilldown", response_model=AdminDrilldownResponse)
async def admin_drilldown(
    metric: str,
    status: str | None = None,
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    start, end = _range(date_from, date_to)
    sources = {
        "customers": (Customer, "name", None, "/admin/marketing"), "suppliers": (Supplier, "name", None, "/admin/marketing"),
        "users": (User, "name", "role", "/admin/master-data"), "offering_letters": (OfferingLetter, "offering_letter_number", "status", "/admin/marketing"),
        "customer_purchase_orders": (PurchaseOrder, "po_number", "type", "/admin/marketing"), "supplier_purchase_orders": (PurchaseOrder, "po_number", "type", "/admin/marketing"),
        "delivery_orders": (DeliveryOrder, "do_number", "status", "/admin/operations"), "fuel_volume": (DeliveryOrder, "do_number", "status", "/admin/operations"),
        "invoice_value": (Invoice, "invoice_number", "invoice_status", "/admin/finance"), "paid_value": (Invoice, "invoice_number", "invoice_status", "/admin/finance"),
        "outstanding_value": (Invoice, "invoice_number", "invoice_status", "/admin/finance"), "overdue_value": (Invoice, "invoice_number", "invoice_status", "/admin/finance"),
        "sales_value": (Sale, "email", "status", "/admin/finance"), "unread_notifications": (Notification, "title", "type", "/admin/master-data"),
        "uploads": (Upload, "original_filename", "document_type", "/admin/master-data"),
    }
    if metric not in sources:
        return AdminDrilldownResponse(metric=metric, title="Data tidak tersedia", description="Metric tidak dikenali.", total=0, total_value=0, page=page, page_size=page_size, items=[])
    model, title_field, status_field, route = sources[metric]
    records = await _records(db, model, start, end)
    if metric == "customer_purchase_orders": records = [record for record in records if record.type == "customer"]
    if metric == "supplier_purchase_orders": records = [record for record in records if record.type == "supplier"]
    if metric == "paid_value": records = [record for record in records if record.invoice_status == "paid"]
    if metric == "outstanding_value": records = [record for record in records if record.invoice_status in {"unpaid", "overdue"}]
    if metric == "overdue_value": records = [record for record in records if record.invoice_status == "overdue" or record.deadline_status == "overdue"]
    if metric == "unread_notifications": records = [record for record in records if not record.is_read]
    if status and status_field: records = [record for record in records if str(getattr(record, status_field, "")) == status]
    value_fields = ("grand_total", "total", "fuel_total", "amount", "size")
    # total_value harus menjumlahkan field yang sama persis dengan yang dipakai
    # per-item `value` (field pertama yang ada pada record), bukan hardcode
    # grand_total saja (yang bernilai 0 untuk Sale/Upload/Notification/PO).
    total_value = sum(
        next(
            (float(getattr(record, field)) for field in value_fields
             if hasattr(record, field) and getattr(record, field) is not None),
            0,
        )
        for record in records
    )
    items = [AdminDrilldownItem(id=record.id, title=str(getattr(record, title_field)), subtitle=str(getattr(record, status_field, "") if status_field else ""), status=str(getattr(record, status_field, "")) if status_field else None, value=next((float(getattr(record, field)) for field in value_fields if hasattr(record, field) and getattr(record, field) is not None), None), created_at=record.created_at, to=route) for record in sorted(records, key=lambda item: item.created_at, reverse=True)]
    offset = (page - 1) * page_size
    return AdminDrilldownResponse(metric=metric, title=metric.replace("_", " ").title(), description="Record penyusun nilai pada periode dan filter aktif.", total=len(items), total_value=total_value, page=page, page_size=page_size, items=items[offset:offset + page_size])
