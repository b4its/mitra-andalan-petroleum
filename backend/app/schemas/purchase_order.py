from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.common import ForeignKeyId


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    po_number: str
    type: str
    customer_id: ForeignKeyId = None
    supplier_id: ForeignKeyId = None
    customer_name: str = ""
    supplier_name: str = ""
    date: str | None = None
    total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_offering_letters: ForeignKeyId = None
    rilis_dana_at: datetime | None = None
    status_rilis_dana: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PurchaseOrderCreate(BaseModel):
    po_number: str
    type: str
    customer_id: ForeignKeyId = None
    supplier_id: ForeignKeyId = None
    date: str | None = None
    total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None
    id_offering_letters: ForeignKeyId = None


class PurchaseOrderUpdate(BaseModel):
    po_number: str | None = None
    type: str | None = None
    customer_id: ForeignKeyId = None
    supplier_id: ForeignKeyId = None
    date: str | None = None
    total: float | None = None
    status: str | None = None
    details: dict[str, Any] | None = None
