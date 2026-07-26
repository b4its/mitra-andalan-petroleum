from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Invoice(BaseModel):
    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(50))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    terms_day: Mapped[int] = mapped_column(Integer, default=30)
    grand_total: Mapped[float] = mapped_column(Float, default=0)
    invoice_status: Mapped[str] = mapped_column(String(20), default="unpaid")
    deadline_status: Mapped[str] = mapped_column(String(20), default="on_time")
    details: Mapped[str] = mapped_column(Text, nullable=True, comment="JSON: full form data per schemas.ts")
