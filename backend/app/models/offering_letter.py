from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class OfferingLetter(BaseModel):
    __tablename__ = "offering_letters"

    offering_letter_number: Mapped[str] = mapped_column(String(50))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    date: Mapped[str] = mapped_column(String(20), nullable=True)
    regarding: Mapped[str] = mapped_column(String(200), nullable=True)
    receiver: Mapped[str] = mapped_column(String(100), nullable=True)
    fuel_total_price: Mapped[float] = mapped_column(Float, default=0)
    transport_price: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="created")
    details: Mapped[str] = mapped_column(Text, nullable=True, comment="JSON: full form data per schemas.ts")

    uploads: Mapped[list["Upload"]] = relationship(
        "Upload",
        primaryjoin="and_(Upload.document_type == 'ol', foreign(Upload.document_id) == OfferingLetter.id)",
        uselist=True, viewonly=True,
    )
