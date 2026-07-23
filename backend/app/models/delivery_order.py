from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class DeliveryOrder(BaseModel):
    __tablename__ = "delivery_orders"

    do_number: Mapped[str] = mapped_column(String(50))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    po_number: Mapped[str] = mapped_column(String(50), nullable=True)
    transport_name: Mapped[str] = mapped_column(String(100), nullable=True)
    fuel_total: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="created")
