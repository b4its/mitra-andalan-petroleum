from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OfferingLetterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    offering_letter_number: str
    customer_id: str
    customer_name: str = ""
    location: str | None = None
    date: str | None = None
    regarding: str | None = None
    receiver: str | None = None
    fuel_total_price: float = 0
    transport_price: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class OfferingLetterCreate(BaseModel):
    offering_letter_number: str
    customer_id: str
    location: str | None = None
    date: str | None = None
    regarding: str | None = None
    receiver: str | None = None
    fuel_total_price: float = 0
    transport_price: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None


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
