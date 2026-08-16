from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class PoTransportir(BaseModel):
    __tablename__ = "po_transportir"

    po_number: Mapped[str] = mapped_column(String(50))
    date: Mapped[str] = mapped_column(String(20), nullable=True)
    pic_person: Mapped[str] = mapped_column(String(100), nullable=True)
    receiver: Mapped[str] = mapped_column(String(200), nullable=True)
    total: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="created")
    details: Mapped[str] = mapped_column(Text, nullable=True, comment="JSON: full form data per schemas.ts")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True, comment="ID user yang membuat dokumen")