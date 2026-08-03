from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Account(BaseModel):
    __tablename__ = "accounts"

    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(
        String(20), default="asset", comment="asset | liability | equity | revenue | expense"
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)

    journal_lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine", back_populates="account", viewonly=True
    )


class JournalEntry(BaseModel):
    __tablename__ = "journal_entries"

    entry_number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    entry_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(255))
    reference: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(10), default="posted", comment="draft | posted")

    lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
        order_by="JournalLine.id",
    )


class JournalLine(BaseModel):
    __tablename__ = "journal_lines"

    journal_entry_id: Mapped[str] = mapped_column(ForeignKey("journal_entries.id"), index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    debit: Mapped[float] = mapped_column(Float, default=0)
    credit: Mapped[float] = mapped_column(Float, default=0)

    journal_entry: Mapped[JournalEntry] = relationship("JournalEntry", back_populates="lines")
    account: Mapped[Account] = relationship("Account", back_populates="journal_lines", lazy="joined")
