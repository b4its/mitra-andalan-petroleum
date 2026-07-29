from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class DeliveryOrder(BaseModel):
    __tablename__ = "delivery_orders"

    do_number: Mapped[str] = mapped_column(String(50))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    po_number: Mapped[str] = mapped_column(String(50), nullable=True)
    transport_name: Mapped[str] = mapped_column(String(100), nullable=True)
    fuel_total: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="created")
    details: Mapped[str] = mapped_column(Text, nullable=True, comment="JSON: full form data per schemas.ts")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True, comment="ID user yang membuat dokumen")

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        primaryjoin="and_(Upload.document_type == 'do', foreign(Upload.document_id) == DeliveryOrder.id)",
        uselist=True, viewonly=True,
    )
