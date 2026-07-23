from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PurchaseOrder(BaseModel):
    __tablename__ = "purchase_orders"

    po_number: Mapped[str] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(20))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    date: Mapped[str] = mapped_column(String(20), nullable=True)
    total: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="created")
