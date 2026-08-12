from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Supplier(BaseModel):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(100))
    npwp: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    province: Mapped[str] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    phone2: Mapped[str] = mapped_column(String(30), nullable=True, comment="Nomor telepon 2 supplier / PIC")
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    bank_name: Mapped[str] = mapped_column(String(100), nullable=True, comment="Nama bank supplier")
    bank_account: Mapped[str] = mapped_column(String(50), nullable=True, comment="Nomor rekening supplier")
