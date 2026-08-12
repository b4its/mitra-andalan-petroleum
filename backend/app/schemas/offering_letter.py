from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.purchase_order import PurchaseOrderResponse
from app.schemas.delivery_order import DeliveryOrderResponse


class OfferingLetterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    offering_letter_number: str
    customer_id: str | None = None
    customer_name: str | None = None
    location: str | None = None
    date: str | None = None
    regarding: str | None = None
    receiver: str | None = None
    fuel_total_price: float = 0
    transport_price: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OfferingLetterCreate(BaseModel):
    offering_letter_number: str
    customer_id: str | None = None
    location: str | None = None
    date: str | None = None
    regarding: str | None = None
    receiver: str | None = None
    fuel_total_price: float = 0
    transport_price: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None


class OfferingLetterUpdate(BaseModel):
    offering_letter_number: str | None = None
    customer_id: str | None = None
    location: str | None = None
    date: str | None = None
    regarding: str | None = None
    receiver: str | None = None
    fuel_total_price: float | None = None
    transport_price: float | None = None
    status: str | None = None
    details: dict[str, Any] | None = None


class OfferingLetterPurchaseOrderItem(PurchaseOrderResponse):
    """Purchase order terkait offering letter beserta delivery order-nya."""

    delivery_orders: list[DeliveryOrderResponse] = []


class OfferingLetterPurchaseOrdersResponse(BaseModel):
    items: list[OfferingLetterPurchaseOrderItem] = []
