from datetime import datetime
from typing import Any

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
    details: dict[str, Any] | None = None
    created_by: str | None = None
    # Rilis dana
    rilis_dana_at: datetime | None = None
    status_rilis_dana: bool = False
    # Ready order (Operations siapkan pengantaran)
    ready_order_at: datetime | None = None
    status_ready_order: bool = False
    # Selesai dikirim (Operations konfirmasi pengiriman)
    selesai_dikirim_at: datetime | None = None
    status_selesai_dikirim: bool = False
    # Lunas ongkir (Finance lunasi setelah selesai dikirim)
    lunas_ongkir_at: datetime | None = None
    status_lunas_ongkir: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DeliveryOrderCreate(BaseModel):
    do_number: str
    customer_id: str
    po_number: str | None = None
    transport_name: str | None = None
    fuel_total: float = 0
    status: str = "created"
    details: dict[str, Any] | None = None
    created_by: str | None = None


class DeliveryOrderUpdate(BaseModel):
    do_number: str | None = None
    customer_id: str | None = None
    po_number: str | None = None
    transport_name: str | None = None
    fuel_total: float | None = None
    status: str | None = None
    details: dict[str, Any] | None = None
    rilis_dana_at: datetime | None = None
    status_rilis_dana: bool | None = None
    ready_order_at: datetime | None = None
    status_ready_order: bool | None = None
    selesai_dikirim_at: datetime | None = None
    status_selesai_dikirim: bool | None = None
    lunas_ongkir_at: datetime | None = None
    status_lunas_ongkir: bool | None = None
