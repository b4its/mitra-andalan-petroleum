from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Sale(BaseModel):
    __tablename__ = "sales"

    date: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100))
    amount: Mapped[float] = mapped_column(Float)
