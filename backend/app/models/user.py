from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    demo_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="URL upload tanda tangan user")
    signature_caption: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Caption tanda tangan (penanda siapa yang menandatangani)")
