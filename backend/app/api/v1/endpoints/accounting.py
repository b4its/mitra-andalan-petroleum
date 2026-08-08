import json
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.accounting import Account, JournalEntry, JournalLine
from app.schemas.common import PaginatedResponse
from app.schemas.accounting import (
    AccountResponse,
    AccountCreate,
    AccountUpdate,
    JournalEntryResponse,
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalLineResponse,
    LedgerResponse,
    LedgerRow,
    TrialBalanceResponse,
    TrialBalanceRow,
    IncomeExpenseRow,
    AccountingSummary,
    MessageResponse,
)

router = APIRouter()

# ── Helper ─────────────────────────────────────────────────────

async def _fetch_lines(db: AsyncSession, entry_id: str) -> list[JournalLineResponse]:
    rows = await db.execute(
        select(JournalLine, Account.name, Account.code)
        .join(Account, Account.id == JournalLine.account_id, isouter=True)
        .where(JournalLine.journal_entry_id == entry_id)
        .order_by(JournalLine.created_at)
    )
    result = []
    for line, name, code in rows.all():
        result.append(JournalLineResponse(
            id=line.id,
            journal_entry_id=line.journal_entry_id,
            account_id=line.account_id,
            account_code=code or "",
            account_name=name or "",
            description=line.description,
            debit=line.debit or 0,
            credit=line.credit or 0,
        ))
    return result


def _entry_to_response(entry: JournalEntry, lines: list[JournalLineResponse]) -> JournalEntryResponse:
    return JournalEntryResponse(
        id=entry.id,
        entry_number=entry.entry_number,
        entry_date=entry.entry_date,
        description=entry.description,
        reference=entry.reference,
        status=entry.status,
        lines=lines,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


async def _next_entry_number(db: AsyncSession, entry_date: date) -> str:
    month = f"{entry_date.year:04d}{entry_date.month:02d}"
    prefix = f"JRM-{month}"
    result = await db.execute(
        select(func.count()).select_from(JournalEntry).where(
            JournalEntry.entry_number.like(f"{prefix}-%")
        )
    )
    count = result.scalar() or 0
    return f"{prefix}-{count + 1:04d}"


# ── Accounts (Chart of Accounts) ───────────────────────────────

@router.get(
    "/accounting/accounts",
    response_model=list[AccountResponse],
    summary="Daftar akun (chart of accounts)",
)
async def list_accounts(
    search: str | None = Query(default=None),
    type: str | None = Query(default=None),
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Account)
    if search:
        stmt = stmt.where(or_(
            Account.name.ilike(f"%{search}%"),
            Account.code.ilike(f"%{search}%"),
        ))
    if type:
        stmt = stmt.where(Account.type == type)
    if not include_inactive:
        stmt = stmt.where(Account.is_active == True)  # noqa: E712
    stmt = stmt.order_by(Account.code)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/accounting/accounts/{id}",
    response_model=AccountResponse,
    summary="Detail akun",
)
async def get_account(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Not found")
    return account


@router.post(
    "/accounting/accounts",
    response_model=AccountResponse,
    status_code=201,
    summary="Buat akun baru",
)
async def create_account(body: AccountCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(Account).where(Account.code == body.code))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Kode akun {body.code} sudah digunakan")
    account = Account(**body.model_dump())
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


@router.put(
    "/accounting/accounts/{id}",
    response_model=AccountResponse,
    summary="Update akun",
)
async def update_account(id: str, body: AccountUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Not found")
    data = body.model_dump(exclude_unset=True)
    if "code" in data and data["code"] != account.code:
        exists = await db.execute(
            select(Account).where(Account.code == data["code"], Account.id != id)
        )
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Kode akun {data['code']} sudah digunakan")
    for key, val in data.items():
        setattr(account, key, val)
    await db.flush()
    await db.refresh(account)
    return account


@router.delete(
    "/accounting/accounts/{id}",
    response_model=MessageResponse,
    summary="Hapus akun",
)
async def delete_account(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Not found")
    lines = await db.execute(select(JournalLine).where(JournalLine.account_id == id))
    if lines.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Akun tidak dapat dihapus karena sudah dipakai di jurnal. Nonaktifkan saja.",
        )
    await db.delete(account)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)


# ── Journal Entries ────────────────────────────────────────────

@router.get(
    "/accounting/journal",
    response_model=PaginatedResponse[JournalEntryResponse],
    summary="Daftar jurnal umum",
)
async def list_journals(
    page: int = 1,
    page_size: int = 20,
    search: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    base = select(JournalEntry)
    if search:
        base = base.where(or_(
            JournalEntry.entry_number.ilike(f"%{search}%"),
            JournalEntry.description.ilike(f"%{search}%"),
            JournalEntry.reference.ilike(f"%{search}%"),
        ))
    if date_from:
        base = base.where(JournalEntry.entry_date >= date_from)
    if date_to:
        base = base.where(JournalEntry.entry_date <= date_to)
    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = base.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    entries = result.scalars().all()

    items = []
    for entry in entries:
        items.append(_entry_to_response(entry, await _fetch_lines(db, entry.id)))
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/accounting/journal/{id}",
    response_model=JournalEntryResponse,
    summary="Detail jurnal",
)
async def get_journal(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    return _entry_to_response(entry, await _fetch_lines(db, id))


@router.post(
    "/accounting/journal",
    response_model=JournalEntryResponse,
    status_code=201,
    summary="Buat jurnal umum",
    description="Membuat jurnal dengan minimal 2 baris. Total debit harus sama dengan total credit.",
)
async def create_journal(body: JournalEntryCreate, db: AsyncSession = Depends(get_db)):
    entry_number = await _next_entry_number(db, body.entry_date)
    entry = JournalEntry(
        entry_number=entry_number,
        entry_date=body.entry_date,
        description=body.description,
        reference=body.reference,
        status=body.status,
    )
    db.add(entry)
    await db.flush()
    for line in body.lines:
        db.add(JournalLine(
            journal_entry_id=entry.id,
            account_id=line.account_id,
            description=line.description,
            debit=line.debit,
            credit=line.credit,
        ))
    await db.flush()
    await db.refresh(entry)
    return _entry_to_response(entry, await _fetch_lines(db, entry.id))


@router.put(
    "/accounting/journal/{id}",
    response_model=JournalEntryResponse,
    summary="Update jurnal umum",
)
async def update_journal(id: str, body: JournalEntryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")

    data = body.model_dump(exclude_unset=True)
    lines_data = body.lines
    if "lines" in data:
        del data["lines"]

    for key, val in data.items():
        setattr(entry, key, val)

    if lines_data is not None:
        existing = await db.execute(
            select(JournalLine).where(JournalLine.journal_entry_id == id)
        )
        for old in existing.scalars().all():
            await db.delete(old)
        await db.flush()
        for line in lines_data:
            db.add(JournalLine(
                journal_entry_id=id,
                account_id=line.account_id,
                description=line.description,
                debit=line.debit,
                credit=line.credit,
            ))

    await db.flush()
    await db.refresh(entry)
    return _entry_to_response(entry, await _fetch_lines(db, id))


@router.delete(
    "/accounting/journal/{id}",
    response_model=MessageResponse,
    summary="Hapus jurnal umum",
)
async def delete_journal(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(entry)
    await db.flush()
    return MessageResponse(message="Deleted", code=200)


# ── Buku Besar (General Ledger) ────────────────────────────────

DEBIT_TYPES = {"asset", "expense"}
CREDIT_TYPES = {"liability", "equity", "revenue"}


async def _account_balance(db: AsyncSession, account_id: str) -> float:
    result = await db.execute(
        select(
            func.coalesce(func.sum(JournalLine.debit), 0.0),
            func.coalesce(func.sum(JournalLine.credit), 0.0),
        ).where(JournalLine.account_id == account_id)
    )
    debit, credit = result.one()
    account = (await db.execute(select(Account).where(Account.id == account_id))).scalar_one()
    if account.type in DEBIT_TYPES:
        return round((debit or 0) - (credit or 0), 2)
    return round((credit or 0) - (debit or 0), 2)


@router.get(
    "/accounting/ledger",
    response_model=LedgerResponse,
    summary="Buku besar",
    description="Riwayat mutasi per akun dengan saldo berjalan (running balance).",
)
async def get_ledger(
    account_id: str = Query(...),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    account = (await db.execute(select(Account).where(Account.id == account_id))).scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Not found")

    conditions = [JournalLine.account_id == account_id]
    if date_from:
        conditions.append(JournalEntry.entry_date >= date_from)
    if date_to:
        conditions.append(JournalEntry.entry_date <= date_to)

    stmt = (
        select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date, JournalEntry.description)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .where(and_(*conditions))
        .order_by(JournalEntry.entry_date, JournalLine.created_at)
    )
    result = await db.execute(stmt)
    rows_data = result.all()

    # Saldo awal: mutasi sebelum date_from (kalau ada filter)
    opening_balance = 0.0
    if date_from:
        pre_conditions = [JournalLine.account_id == account_id, JournalEntry.entry_date < date_from]
        pre = await db.execute(
            select(
                func.coalesce(func.sum(JournalLine.debit), 0.0),
                func.coalesce(func.sum(JournalLine.credit), 0.0),
            )
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .where(and_(*pre_conditions))
        )
        pre_debit, pre_credit = pre.one()
        if account.type in DEBIT_TYPES:
            opening_balance = round((pre_debit or 0) - (pre_credit or 0), 2)
        else:
            opening_balance = round((pre_credit or 0) - (pre_debit or 0), 2)

    balance = opening_balance
    ledger_rows = []
    for line, entry_number, entry_date, description in rows_data:
        if account.type in DEBIT_TYPES:
            balance = round(balance + (line.debit or 0) - (line.credit or 0), 2)
        else:
            balance = round(balance + (line.credit or 0) - (line.debit or 0), 2)
        ledger_rows.append(LedgerRow(
            id=line.id,
            entry_number=entry_number,
            entry_date=entry_date,
            description=description,
            account_code=account.code,
            account_name=account.name,
            debit=line.debit or 0,
            credit=line.credit or 0,
            balance=balance,
        ))

    return LedgerResponse(
        account_id=account.id,
        account_code=account.code,
        account_name=account.name,
        account_type=account.type,
        opening_balance=opening_balance,
        closing_balance=balance,
        rows=ledger_rows,
    )


# ── Neraca Saldo (Trial Balance) ───────────────────────────────

@router.get(
    "/accounting/trial-balance",
    response_model=TrialBalanceResponse,
    summary="Neraca saldo",
    description="Saldo debit/credit seluruh akun aktif.",
)
async def get_trial_balance(db: AsyncSession = Depends(get_db)):
    accounts = (await db.execute(select(Account).order_by(Account.code))).scalars().all()
    rows = []
    total_debit = 0.0
    total_credit = 0.0
    for account in accounts:
        result = await db.execute(
            select(
                func.coalesce(func.sum(JournalLine.debit), 0.0),
                func.coalesce(func.sum(JournalLine.credit), 0.0),
            ).where(JournalLine.account_id == account.id)
        )
        debit, credit = result.one()
        if account.type in DEBIT_TYPES:
            saldo = round((debit or 0) - (credit or 0), 2)
            rows.append(TrialBalanceRow(
                account_id=account.id, account_code=account.code, account_name=account.name,
                account_type=account.type, debit=saldo, credit=0,
            ))
            total_debit += saldo
        else:
            saldo = round((credit or 0) - (debit or 0), 2)
            rows.append(TrialBalanceRow(
                account_id=account.id, account_code=account.code, account_name=account.name,
                account_type=account.type, debit=0, credit=saldo,
            ))
            total_credit += saldo
    rows = [r for r in rows if r.debit > 0 or r.credit > 0]
    return TrialBalanceResponse(
        rows=rows,
        total_debit=round(total_debit, 2),
        total_credit=round(total_credit, 2),
    )


# ── Pemasukan & Pengeluaran ────────────────────────────────────

async def _income_expense_rows(
    db: AsyncSession, account_type: str, amount_side: str,
    page: int, page_size: int, date_from: date | None, date_to: date | None,
):
    base = (
        select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date,
               JournalEntry.description, JournalEntry.reference, Account.code, Account.name)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(Account.type == account_type)
    )
    if date_from:
        base = base.where(JournalEntry.entry_date >= date_from)
    if date_to:
        base = base.where(JournalEntry.entry_date <= date_to)

    total_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = total_result.scalar() or 0

    stmt = base.order_by(JournalEntry.entry_date.desc(), JournalLine.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)

    items = []
    for line, entry_number, entry_date, description, reference, code, name in result.all():
        amount = (line.credit if amount_side == "credit" else line.debit) or 0
        items.append(IncomeExpenseRow(
            id=line.id,
            entry_number=entry_number,
            entry_date=entry_date,
            description=description,
            account_code=code,
            account_name=name,
            amount=amount,
            reference=reference,
        ))
    return items, total


@router.get(
    "/accounting/income",
    response_model=PaginatedResponse[IncomeExpenseRow],
    summary="Pemasukan",
    description="Pemasukan = mutasi kredit pada akun pendapatan (revenue).",
)
async def list_income(
    page: int = 1, page_size: int = 20,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await _income_expense_rows(
        db, "revenue", "credit", page, page_size, date_from, date_to
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/accounting/expenses",
    response_model=PaginatedResponse[IncomeExpenseRow],
    summary="Pengeluaran",
    description="Pengeluaran = mutasi debit pada akun beban (expense).",
)
async def list_expenses(
    page: int = 1, page_size: int = 20,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await _income_expense_rows(
        db, "expense", "debit", page, page_size, date_from, date_to
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


# ── Summary / Dashboard ────────────────────────────────────────

@router.get(
    "/accounting/summary",
    response_model=AccountingSummary,
    summary="Ringkasan akuntansi",
    description="Total pemasukan, pengeluaran, laba bersih, saldo kas/bank, dan jurnal terbaru.",
)
async def get_summary(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    def _date_cond(column, side: str):
        if side == "from" and date_from:
            return column >= date_from
        if side == "to" and date_to:
            return column <= date_to
        return None

    conditions = []
    c1 = _date_cond(JournalEntry.entry_date, "from")
    c2 = _date_cond(JournalEntry.entry_date, "to")
    if c1:
        conditions.append(c1)
    if c2:
        conditions.append(c2)

    # Total pemasukan (credit revenue)
    income_stmt = (
        select(func.coalesce(func.sum(JournalLine.credit), 0.0))
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(Account.type == "revenue")
    )
    for cond in conditions:
        income_stmt = income_stmt.where(cond)
    total_income = round((await db.execute(income_stmt)).scalar() or 0, 2)

    # Total pengeluaran (debit expense)
    expense_stmt = (
        select(func.coalesce(func.sum(JournalLine.debit), 0.0))
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(Account.type == "expense")
    )
    for cond in conditions:
        expense_stmt = expense_stmt.where(cond)
    total_expense = round((await db.execute(expense_stmt)).scalar() or 0, 2)

    # Saldo kas/bank (asset dengan nama Kas/Bank)
    cash_stmt = (
        select(func.coalesce(func.sum(JournalLine.debit), 0.0), func.coalesce(func.sum(JournalLine.credit), 0.0))
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(Account.type == "asset", or_(Account.name.ilike("Kas%"), Account.name.ilike("Bank%")))
    )
    for cond in conditions:
        cash_stmt = cash_stmt.where(cond)
    cash_debit, cash_credit = (await db.execute(cash_stmt)).one()
    cash_balance = round((cash_debit or 0) - (cash_credit or 0), 2)

    # Counts
    jc = await db.execute(select(func.count()).select_from(JournalEntry))
    journal_count = jc.scalar() or 0
    ac = await db.execute(select(func.count()).select_from(Account))
    account_count = ac.scalar() or 0
    ic = await db.execute(select(func.count()).select_from(income_stmt.subquery()))
    income_count = ic.scalar() or 0
    ec = await db.execute(select(func.count()).select_from(expense_stmt.subquery()))
    expense_count = ec.scalar() or 0

    # Recent journals
    recent = []
    recent_stmt = select(JournalEntry).order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc()).limit(5)
    recent_entries = (await db.execute(recent_stmt)).scalars().all()
    for entry in recent_entries:
        recent.append(_entry_to_response(entry, await _fetch_lines(db, entry.id)))

    return AccountingSummary(
        total_income=total_income,
        total_expense=total_expense,
        net_income=round(total_income - total_expense, 2),
        cash_balance=cash_balance,
        income_count=income_count,
        expense_count=expense_count,
        journal_count=journal_count,
        account_count=account_count,
        recent_journals=recent,
    )
