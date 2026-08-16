from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PoTransportirResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    po_number: str
    date: str | None = None
    pic_person: str | None = None
    receiver: str | None = None
    total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_purchase_order: str | None = None
    customer_id: str | None = None
    customer_name: str = ""
    purchase_order_number: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PoTransportirCreate(BaseModel):
    po_number: str
    date: str | None = None
    pic_person: str | None = None
    receiver: str | None = None
    total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_purchase_order: str | None = None
    customer_id: str | None = None


class PoTransportirUpdate(BaseModel):
    po_number: str | None = None
    date: str | None = None
    pic_person: str | None = None
    receiver: str | None = None
    total: float | None = None
    status: str | None = None
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_purchase_order: str | None = None
    customer_id: str | None = None