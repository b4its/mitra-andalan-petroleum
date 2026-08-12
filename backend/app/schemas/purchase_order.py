from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    po_number: str
    type: str
    customer_id: str | None = None
    supplier_id: str | None = None
    customer_name: str = ""
    supplier_name: str = ""
    date: str | None = None
    total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_offering_letters: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PurchaseOrderCreate(BaseModel):
    po_number: str
    type: str
    customer_id: str | None = None
    supplier_id: str | None = None
    date: str | None = None
    total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_offering_letters: str | None = None


class PurchaseOrderUpdate(BaseModel):
    po_number: str | None = None
    type: str | None = None
    customer_id: str | None = None
    supplier_id: str | None = None
    date: str | None = None
    total: float | None = None
    status: str | None = None
    details: dict[str, Any] | None = None
