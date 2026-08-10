from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Price(BaseModel):
    __tablename__ = "prices"

    category: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(30), default="")
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    effective_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
