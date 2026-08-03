from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    type: str
    description: str | None = None
    is_active: bool = True
    parent_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AccountCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(default="asset", pattern="^(asset|liability|equity|revenue|expense)$")
    description: str | None = None
    is_active: bool = True
    parent_id: str | None = None


class AccountUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    type: str | None = Field(default=None, pattern="^(asset|liability|equity|revenue|expense)$")
    description: str | None = None
    is_active: bool | None = None
    parent_id: str | None = None


class JournalLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    journal_entry_id: str
    account_id: str
    account_code: str = ""
    account_name: str = ""
    description: str | None = None
    debit: float = 0
    credit: float = 0


class JournalEntryResponse(BaseModel):
    id: str
    entry_number: str
    entry_date: date
    description: str
    reference: str | None = None
    status: str = "posted"
    lines: list[JournalLineResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class JournalLineCreate(BaseModel):
    account_id: str
    description: str | None = None
    debit: float = 0
    credit: float = 0


class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str = Field(..., min_length=1)
    reference: str | None = None
    status: str = "posted"
    lines: list[JournalLineCreate] = Field(..., min_length=2)

    @field_validator("lines")
    @classmethod
    def _validate_lines(cls, v: list[JournalLineCreate]):
        total_debit = sum(round(line.debit, 2) for line in v)
        total_credit = sum(round(line.credit, 2) for line in v)
        if total_debit != total_credit:
            raise ValueError(
                f"Jurnal tidak balance: debit {total_debit} != credit {total_credit}"
            )
        if total_debit <= 0:
            raise ValueError("Jurnal harus memiliki nominal lebih dari 0")
        for line in v:
            if line.debit > 0 and line.credit > 0:
                raise ValueError(
                    f"Akun {line.account_id} tidak boleh debit dan credit bersamaan"
                )
            if line.debit == 0 and line.credit == 0:
                raise ValueError("Ada baris jurnal tanpa nominal")
        return v


class JournalEntryUpdate(BaseModel):
    entry_date: date | None = None
    description: str | None = None
    reference: str | None = None
    status: str | None = None
    lines: list[JournalLineCreate] | None = None

    @field_validator("lines")
    @classmethod
    def _validate_lines(cls, v: list[JournalLineCreate] | None):
        if v is None:
            return v
        total_debit = sum(round(line.debit, 2) for line in v)
        total_credit = sum(round(line.credit, 2) for line in v)
        if total_debit != total_credit:
            raise ValueError(
                f"Jurnal tidak balance: debit {total_debit} != credit {total_credit}"
            )
        if total_debit <= 0:
            raise ValueError("Jurnal harus memiliki nominal lebih dari 0")
        for line in v:
            if line.debit > 0 and line.credit > 0:
                raise ValueError(
                    f"Akun {line.account_id} tidak boleh debit dan credit bersamaan"
                )
            if line.debit == 0 and line.credit == 0:
                raise ValueError("Ada baris jurnal tanpa nominal")
        return v


class LedgerRow(BaseModel):
    id: str
    entry_number: str
    entry_date: date
    description: str
    account_code: str
    account_name: str
    debit: float = 0
    credit: float = 0
    balance: float = 0


class LedgerResponse(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    account_type: str
    opening_balance: float = 0
    closing_balance: float = 0
    rows: list[LedgerRow] = []


class TrialBalanceRow(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    account_type: str
    debit: float = 0
    credit: float = 0


class TrialBalanceResponse(BaseModel):
    rows: list[TrialBalanceRow]
    total_debit: float
    total_credit: float


class IncomeExpenseRow(BaseModel):
    id: str
    entry_number: str
    entry_date: date
    description: str
    account_code: str
    account_name: str
    amount: float = 0
    reference: str | None = None


class AccountingSummary(BaseModel):
    total_income: float = 0
    total_expense: float = 0
    net_income: float = 0
    cash_balance: float = 0
    income_count: int = 0
    expense_count: int = 0
    journal_count: int = 0
    account_count: int = 0
    recent_journals: list[JournalEntryResponse] = []


class MessageResponse(BaseModel):
    message: str
    code: int = 200
