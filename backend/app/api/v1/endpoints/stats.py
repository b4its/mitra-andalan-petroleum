from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.offering_letter import OfferingLetter
from app.models.delivery_order import DeliveryOrder
from app.models.invoice import Invoice
from app.schemas.stats import SingleStat, StatsResponse

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
        SingleStat(title="Penawaran dibuat", icon="i-lucide-file-text", value=total_ol, variation=12.5, to="/marketing/customer"),
        SingleStat(title="Penawaran belum disetujui", icon="i-lucide-clock", value=pending_ol, variation=-5.2, to="/marketing/customer"),
        SingleStat(title="PO dari Customer", icon="i-lucide-shopping-cart", value=po_customer, variation=8.3, to="/marketing/customer"),
        SingleStat(title="PO untuk logistik", icon="i-lucide-truck", value=po_logistik, variation=3.1, to="/marketing/supplier"),
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
        SingleStat(title="Delivery Order Dibuat", icon="i-lucide-file-text", value=total_do, variation=7.8, to="/operations"),
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
        SingleStat(title="DO Diterima", icon="i-lucide-file-check", value=do_diterima, variation=5.4, to="/finance/do"),
        SingleStat(title="Invoice Belum Dibuat", icon="i-lucide-file-minus", value=invoice_belum, variation=-2.1, to="/finance/invoice"),
        SingleStat(title="Invoice Belum Lunas", icon="i-lucide-alert-circle", value=unpaid, variation=11.3, to="/finance/invoice/data-invoice-customer"),
    ])


@router.get(
    "/stats/home",
    response_model=StatsResponse,
    summary="Home dashboard stats",
    description="Statistik halaman utama: total customer, revenue, orders.",
)
async def home_stats(db: AsyncSession = Depends(get_db)):
    total_customers = await _count(db, select(OfferingLetter).distinct(OfferingLetter.customer_id))
    total_revenue_result = await db.execute(select(func.coalesce(func.sum(Invoice.grand_total), 0)))
    total_revenue = total_revenue_result.scalar() or 0
    total_ol = await _count(db, select(OfferingLetter))

    return StatsResponse(stats=[
        SingleStat(title="Customers", icon="i-lucide-users", value=total_customers, variation=3.2, to="/marketing/customer"),
        SingleStat(title="Revenue", icon="i-lucide-trending-up", value=total_revenue, variation=8.1, to="/finance"),
        SingleStat(title="Orders", icon="i-lucide-shopping-bag", value=total_ol, variation=-1.5, to="/operations"),
    ])


async def _count(db, stmt):
    result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    return result.scalar() or 0
