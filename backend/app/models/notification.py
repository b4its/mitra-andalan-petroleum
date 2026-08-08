from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    title: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(30), default="info")
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)
    role: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="Target role (accounting, admin, dll). Null = semua role.")
    to: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)
