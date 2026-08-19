"""
Admin Stats API with Translated Labels
Returns complete system analytics with Indonesian status labels
"""
from datetime import datetime, timedelta, timezone
from collections import Counter
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.user import User
from app.models.offering_letter import OfferingLetter
from app.models.purchase_order import PurchaseOrder
from app.models.delivery_order import DeliveryOrder
from app.models.invoice import Invoice
from app.models.sale import Sale
from app.models.notification import Notification
from app.models.upload import Upload
from app.schemas.stats import AdminStatsResponse, AdminMetric, AdminTrend, AdminActivity, AdminBreakdown, RevenuePoint, RevenueResponse
from app.utils.status_translations import translate_status, translate_breakdown_item

router = APIRouter()

async def _count(db, stmt):
    result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    return result.scalar() or 0

def _breakdown_with_translation(records, attribute: str) -> list[dict]:
    """Get breakdown counts with translated Indonesian labels"""
    counts = Counter((getattr(record, attribute, None) or "unknown") for record in records)
    return [
        translate_breakdown_item(str(key), label_key, value)
        for key, label_key in counts.items()
    ]

@router.get(
    "/stats/admin",
    response_model=AdminStatsResponse,
    summary="Complete admin system analytics with translations",
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
    
    # Calculate paid/unpaid values
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
        AdminMetric(key="paid_value", title="Nilai Terbayar", value=sum(record.grand_total or 0 for record in paid), unit="currency", icon="i-lucide-circle-check", description="Akumulasi invoice berstatus Lunas."),
        AdminMetric(key="outstanding_value", title="Piutang Berjalan", value=sum(record.grand_total or 0 for record in outstanding), unit="currency", icon="i-lucide-clock-3", description="Akumulasi invoice Belum Lunas dan Jatuh Tempo."),
        AdminMetric(key="overdue_value", title="Piutang Overdue", value=sum(record.grand_total or 0 for record in overdue), unit="currency", icon="i-lucide-alert-triangle", description="Akumulasi invoice atau deadline berstatus Jatuh Tempo."),
        AdminMetric(key="sales_value", title="Nilai Sales", value=sum(record.amount or 0 for record in sales), unit="currency", icon="i-lucide-chart-no-axes-combined", description="Akumulasi amount transaksi sales."),
        AdminMetric(key="unread_notifications", title="Notifikasi Belum Dibaca", value=sum(not record.is_read for record in notifications), icon="i-lucide-bell", description="Notification is_read=false dalam periode aktif."),
        AdminMetric(key="uploads", title="Upload", value=len(uploads), icon="i-lucide-paperclip", description="File upload dibuat dalam periode aktif."),
    ]
    
    # Trends with translated labels
    cursor = start.replace(hour=0, minute=0, second=0, microsecond=0)
    trends = []
    while cursor <= end:
        next_cursor = cursor + timedelta(days=7)
        label = f"{cursor.strftime('%d %b')}"
        bucket = lambda records: [item for item in records if cursor <= item.created_at.replace(tzinfo=timezone.utc) < next_cursor]
        trends.append({
            "key": cursor.date().isoformat(), 
            "label": label,
            "offering_letters": len(bucket(ols)),
            "purchase_orders": len(bucket(pos)),
            "delivery_orders": len(bucket(dos)),
            "invoices": len(bucket(invoices)),
            "sales_amount": sum(item.amount or 0 for item in bucket(sales))
        })
        cursor = next_cursor
    
    # Distributions WITH TRANSLATED INDONESIAN LABELS ✅
    distributions = {
        "offering_letters": _breakdown_with_translation(ols, "status"),
        "purchase_orders": _breakdown_with_translation(pos, "type"),
        "delivery_orders": _breakdown_with_translation(dos, "status"),
        "invoices": _breakdown_with_translation(invoices, "invoice_status"),
        "invoice_deadlines": _breakdown_with_translation(invoices, "deadline_status"),
        "users": _breakdown_with_translation(users, "role"),
        "notifications": _breakdown_with_translation(notifications, "type"),
        "uploads": _breakdown_with_translation(uploads, "document_type")
    }
    
    return AdminStatsResponse(
        date_from=start, date_to=end, metrics=metrics, trends=trends,
        distributions=distributions
    )

def _created_between(model, start, end):
    return select(model).where(model.created_at >= start, model.created_at <= end)

async def _records(db: AsyncSession, model, start, end):
    return list((await db.execute(_created_between(model, start, end))).scalars().all())

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
