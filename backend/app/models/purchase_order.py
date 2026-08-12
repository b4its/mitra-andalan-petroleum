from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    details: Mapped[str] = mapped_column(Text, nullable=True, comment="JSON: full form data per schemas.ts")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True, comment="ID user yang membuat dokumen")
    rilis_dana_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="Waktu rilis dana (WITA)")
    status_rilis_dana: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"), comment="True jika dana sudah dirilis")

    # ── Relasi ke dokumen terkait ─────────────────────────────────
    id_offering_letters: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON array: ID offering letter terkait")

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        primaryjoin="and_(Upload.document_type == 'po', foreign(Upload.document_id) == PurchaseOrder.id)",
        uselist=True, viewonly=True,
    )
