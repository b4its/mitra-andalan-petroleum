from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Upload(BaseModel):
    __tablename__ = "uploads"

    original_filename: Mapped[str] = mapped_column(String(255))
    stored_filename: Mapped[str] = mapped_column(String(255))
    folder: Mapped[str] = mapped_column(String(50), default="general")
    mime_type: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(500))
    document_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
