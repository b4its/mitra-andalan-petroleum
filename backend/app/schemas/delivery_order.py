from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeliveryOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    do_number: str
    customer_id: str
    customer_name: str = ""
    po_number: str | None = None
    transport_name: str | None = None
    fuel_total: float = 0
    status: str = "created"
    created_at: datetime
    updated_at: datetime


class DeliveryOrderCreate(BaseModel):
    do_number: str
    customer_id: str
    po_number: str | None = None
    transport_name: str | None = None
    fuel_total: float = 0
    status: str = "created"


class DeliveryOrderUpdate(BaseModel):
    do_number: str | None = None
    customer_id: str | None = None
    po_number: str | None = None
    transport_name: str | None = None
    fuel_total: float | None = None
    status: str | None = None
