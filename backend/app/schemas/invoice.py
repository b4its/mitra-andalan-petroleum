from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    invoice_number: str
    customer_id: str
    customer_name: str = ""
    terms_day: int = 30
    grand_total: float = 0
    invoice_status: str = "unpaid"
    deadline_status: str = "on_time"
    details: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class InvoiceCreate(BaseModel):
    invoice_number: str
    customer_id: str
    terms_day: int = 30
    grand_total: float = 0
    invoice_status: str = "unpaid"
    deadline_status: str = "on_time"
    details: dict[str, Any] | None = None


class InvoiceUpdate(BaseModel):
    invoice_number: str | None = None
    customer_id: str | None = None
    terms_day: int | None = None
    grand_total: float | None = None
    invoice_status: str | None = None
    deadline_status: str | None = None
    details: dict[str, Any] | None = None
