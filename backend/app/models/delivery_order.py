from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class DeliveryOrder(BaseModel):
    __tablename__ = "delivery_orders"

    do_number: Mapped[str] = mapped_column(String(50))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    po_number: Mapped[str] = mapped_column(String(50), nullable=True)
    transport_name: Mapped[str] = mapped_column(String(100), nullable=True)
    fuel_total: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="created")
    details: Mapped[str] = mapped_column(Text, nullable=True, comment="JSON: full form data per schemas.ts")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True, comment="ID user yang membuat dokumen")

    # ── Rilis Dana (diisi oleh Finance) ───────────────────────────
    rilis_dana_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Waktu rilis dana (WITA)")
    status_rilis_dana: Mapped[bool] = mapped_column(Boolean, default=False, comment="True jika dana sudah dirilis")

    # ── Ready Order (diisi oleh Operations setelah rilis dana) ───
    ready_order_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Waktu pengantaran disiapkan (WITA)")
    status_ready_order: Mapped[bool] = mapped_column(Boolean, default=False, comment="True jika pengantaran sudah disiapkan")

    # ── Selesai Dikirim (diisi oleh Operations) ──────────────────
    selesai_dikirim_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Waktu selesai dikirim (WITA)")
    status_selesai_dikirim: Mapped[bool] = mapped_column(Boolean, default=False, comment="True jika pengiriman sudah selesai")

    # ── Lunas Ongkir (diisi oleh Finance setelah selesai dikirim) ──
    lunas_ongkir_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Waktu pelunasan ongkir (WITA)")
    status_lunas_ongkir: Mapped[bool] = mapped_column(Boolean, default=False, comment="True jika ongkir sudah dilunasi")

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        primaryjoin="and_(Upload.document_type == 'do', foreign(Upload.document_id) == DeliveryOrder.id)",
        uselist=True, viewonly=True,
    )
