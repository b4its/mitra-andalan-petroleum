from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    customers,
    suppliers,
    offering_letters,
    purchase_orders,
    delivery_orders,
    invoices,
    sales,
    notifications,
    stats,
    profiles,
    uploads,
    accounting,
    admin_database,
    prices,
)

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth.router, tags=["auth"])
v1_router.include_router(customers.router, tags=["customers"])
v1_router.include_router(suppliers.router, tags=["suppliers"])
v1_router.include_router(offering_letters.router, tags=["offering-letters"])
v1_router.include_router(purchase_orders.router, tags=["purchase-orders"])
v1_router.include_router(delivery_orders.router, tags=["delivery-orders"])
v1_router.include_router(invoices.router, tags=["invoices"])
v1_router.include_router(sales.router, tags=["sales"])
v1_router.include_router(notifications.router, tags=["notifications"])
v1_router.include_router(stats.router, tags=["stats"])
v1_router.include_router(profiles.router, tags=["profiles"])
v1_router.include_router(uploads.router, tags=["uploads"])
v1_router.include_router(accounting.router, tags=["accounting"])
v1_router.include_router(admin_database.router, tags=["admin-database"])
v1_router.include_router(prices.router, tags=["prices"])
