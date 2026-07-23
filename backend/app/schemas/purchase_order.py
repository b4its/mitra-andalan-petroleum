from datetime import datetime

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
    created_at: datetime
    updated_at: datetime


class PurchaseOrderCreate(BaseModel):
    po_number: str
    type: str
    customer_id: str | None = None
    supplier_id: str | None = None
    date: str | None = None
    total: float = 0
    status: str = "created"


class PurchaseOrderUpdate(BaseModel):
    po_number: str | None = None
    type: str | None = None
    customer_id: str | None = None
    supplier_id: str | None = None
    date: str | None = None
    total: float | None = None
    status: str | None = None
