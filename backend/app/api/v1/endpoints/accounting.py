from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.utils.activity_logger import log_activity, actor_from_request, model_to_dict
from app.models.accounting import Account, JournalEntry, JournalLine
from app.schemas.common import PaginatedResponse
from app.schemas.accounting import (
    AccountResponse,
    AccountCreate,
    AccountUpdate,
    AccountDetailResponse,
    AccountJournalLine,
    JournalEntryResponse,
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalLineResponse,
    LedgerResponse,
    LedgerListResponse,
    LedgerRow,
    TrialBalanceResponse,
    TrialBalanceRow,
    IncomeExpenseRow,
    AccountingSummary,
    MessageResponse,
    BalanceSheetResponse,
    BalanceSheetSection,
    BalanceSheetAccount,
    CashflowResponse,
    CashflowSection,
    CashflowItem,
    CostRecapResponse,
    CostRecapGroup,
    CostRecapRow,
    MonitoringResponse,
    MonitoringRow,
    DailyCashResponse,
    DailyCashRow,
    BankInterestResponse,
    BankInterestRow,
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


def _journal_to_dict(entry: JournalEntry, lines) -> dict:
    return {
        "entry_number": entry.entry_number,
        "entry_date": str(entry.entry_date),
        "description": entry.description,
        "reference": entry.reference,
        "status": entry.status,
        "lines": [
            {
                "account_id": l.get("account_id") if isinstance(l, dict) else l.account_id,
                "description": l.get("description") if isinstance(l, dict) else l.description,
                "debit": l.get("debit") if isinstance(l, dict) else l.debit,
                "credit": l.get("credit") if isinstance(l, dict) else l.credit,
            }
            for l in lines
        ],
    }


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
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return account


@router.post(
    "/accounting/accounts",
    response_model=AccountResponse,
    status_code=201,
    summary="Buat akun baru",
)
async def create_account(request: Request, body: AccountCreate, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(select(Account).where(Account.code == body.code))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Kode akun {body.code} sudah digunakan")
    account = Account(**body.model_dump())
    db.add(account)
    await db.flush()
    await db.refresh(account)
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="account",
        resource_id=account.id,
        resource_name=account.name,
        old_data=None,
        new_data=model_to_dict(account),
        details=f"Akun {account.code} - {account.name} ({account.type}) berhasil dibuat"
    )
    return account


@router.put(
    "/accounting/accounts/{id}",
    response_model=AccountResponse,
    summary="Update akun",
)
async def update_account(request: Request, id: str, body: AccountUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_data = model_to_dict(account)
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
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="account",
        resource_id=account.id,
        resource_name=account.name,
        old_data=old_data,
        new_data=model_to_dict(account),
        details=f"Akun {account.code} berhasil diperbarui"
    )
    return account


@router.delete(
    "/accounting/accounts/{id}",
    response_model=MessageResponse,
    summary="Hapus akun",
)
async def delete_account(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    lines = await db.execute(select(JournalLine).where(JournalLine.account_id == id))
    if lines.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Akun tidak dapat dihapus karena sudah dipakai di jurnal. Nonaktifkan saja.",
        )
    a_name = account.name
    old_data = model_to_dict(account)
    await db.delete(account)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="account",
        resource_id=id,
        resource_name=a_name,
        old_data=old_data,
        new_data=None,
        details=f"Akun {a_name} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)


@router.get(
    "/accounting/accounts/{id}/detail",
    response_model=AccountDetailResponse,
    summary="Detail lengkap akun dengan mutasi jurnal",
)
async def get_account_detail(id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")

    # Total debit/credit
    agg = await db.execute(
        select(
            func.coalesce(func.sum(JournalLine.debit), 0.0),
            func.coalesce(func.sum(JournalLine.credit), 0.0),
            func.count(JournalLine.id),
        ).where(JournalLine.account_id == id)
    )
    total_debit, total_credit, journal_count = agg.one()
    total_debit = round(total_debit or 0, 2)
    total_credit = round(total_credit or 0, 2)

    # Balance
    if account.type in DEBIT_TYPES:
        balance = total_debit - total_credit
    else:
        balance = total_credit - total_debit

    # Recent journals
    recent_stmt = (
        select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date, JournalEntry.description)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .where(JournalLine.account_id == id)
        .order_by(JournalEntry.entry_date.desc(), JournalLine.created_at.desc())
        .limit(20)
    )
    recent_result = await db.execute(recent_stmt)
    recent = [
        AccountJournalLine(
            id=line.id,
            entry_number=entry_number,
            entry_date=entry_date,
            description=description,
            debit=round(line.debit or 0, 2),
            credit=round(line.credit or 0, 2),
        )
        for line, entry_number, entry_date, description in recent_result.all()
    ]

    return AccountDetailResponse(
        id=account.id,
        code=account.code,
        name=account.name,
        type=account.type,
        description=account.description,
        is_active=account.is_active,
        total_debit=total_debit,
        total_credit=total_credit,
        balance=round(balance, 2),
        journal_count=journal_count,
        recent_journals=recent,
    )


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
    account_ids: list[str] | None = Query(default=None),
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
    if account_ids:
        base = base.where(
            JournalEntry.id.in_(
                select(JournalLine.journal_entry_id).where(JournalLine.account_id.in_(account_ids))
            )
        )
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
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return _entry_to_response(entry, await _fetch_lines(db, id))


async def _assert_accounts_exist(db: AsyncSession, lines) -> None:
    """Pastikan setiap account_id pada lines benar-benar ada di tabel accounts.

    Mencegah IntegrityError FK (journal_lines.account_id -> accounts.id) di
    MySQL/PostgreSQL yang akan mengembalikan 500, serta data korup (account
    tidak ada) di SQLite yang tidak menegakkan FK.
    """
    ids = {line.account_id for line in lines if line.account_id}
    if not ids:
        return
    result = await db.execute(select(Account.id).where(Account.id.in_(ids)))
    found = set(result.scalars().all())
    missing = ids - found
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Akun tidak ditemukan: {', '.join(sorted(missing))}",
        )


@router.post(
    "/accounting/journal",
    response_model=JournalEntryResponse,
    status_code=201,
    summary="Buat jurnal umum",
    description="Membuat jurnal dengan minimal 2 baris. Total debit harus sama dengan total credit.",
)
async def create_journal(request: Request, body: JournalEntryCreate, db: AsyncSession = Depends(get_db)):
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
    await _assert_accounts_exist(db, body.lines)
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
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="create",
        resource_type="journal_entry",
        resource_id=entry.id,
        resource_name=entry.entry_number,
        old_data=None,
        new_data=_journal_to_dict(entry, body.lines),
        details=f"Jurnal {entry.entry_number} ({len(body.lines)} baris) berhasil dibuat"
    )
    return _entry_to_response(entry, await _fetch_lines(db, entry.id))


@router.put(
    "/accounting/journal/{id}",
    response_model=JournalEntryResponse,
    summary="Update jurnal umum",
)
async def update_journal(request: Request, id: str, body: JournalEntryUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")

    old_lines = await _fetch_lines(db, id)
    old_data = _journal_to_dict(entry, [
        {
            "account_id": l.account_id,
            "description": l.description,
            "debit": l.debit,
            "credit": l.credit,
        }
        for l in old_lines
    ])

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
        await _assert_accounts_exist(db, lines_data)
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
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="update",
        resource_type="journal_entry",
        resource_id=entry.id,
        resource_name=entry.entry_number,
        old_data=old_data,
        new_data=_journal_to_dict(entry, lines_data) if lines_data is not None else None,
        details=f"Jurnal {entry.entry_number} berhasil diperbarui"
    )
    return _entry_to_response(entry, await _fetch_lines(db, id))


@router.delete(
    "/accounting/journal/{id}",
    response_model=MessageResponse,
    summary="Hapus jurnal umum",
)
async def delete_journal(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    old_lines = await _fetch_lines(db, id)
    old_data = _journal_to_dict(entry, [
        {
            "account_id": l.account_id,
            "description": l.description,
            "debit": l.debit,
            "credit": l.credit,
        }
        for l in old_lines
    ])
    entry_number = entry.entry_number
    await db.delete(entry)
    await db.flush()
    actor = actor_from_request(request)
    await log_activity(
        db=db,
        request=request,
        user_id=actor["user_id"],
        actor_name=actor["actor_name"],
        actor_role=actor["actor_role"],
        action="delete",
        resource_type="journal_entry",
        resource_id=id,
        resource_name=entry_number,
        old_data=old_data,
        new_data=None,
        details=f"Jurnal {entry_number} berhasil dihapus"
    )
    return MessageResponse(message="Dihapus", code=200)


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


async def _ledger_for_account(
    db: AsyncSession, account: Account,
    date_from: date | None, date_to: date | None,
) -> LedgerResponse:
    conditions = [JournalLine.account_id == account.id]
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
        pre_conditions = [JournalLine.account_id == account.id, JournalEntry.entry_date < date_from]
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
        raise HTTPException(status_code=404, detail="Tidak ditemukan")
    return await _ledger_for_account(db, account, date_from, date_to)


@router.get(
    "/accounting/ledger-all",
    response_model=LedgerListResponse,
    summary="Buku besar semua akun",
    description="Buku besar untuk SELURUH akun sekaligus (saldo awal, mutasi, saldo akhir) dalam satu respons. Filter dengan range tanggal.",
)
async def get_ledger_all(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    accounts = (await db.execute(select(Account).order_by(Account.code))).scalars().all()
    items = []
    for account in accounts:
        ledger = await _ledger_for_account(db, account, date_from, date_to)
        if ledger.opening_balance != 0 or ledger.closing_balance != 0 or ledger.rows:
            items.append(ledger)
    return LedgerListResponse(items=items)


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
    search: str | None = None, account_ids: list[str] | None = None,
):
    base = (
        select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date,
               JournalEntry.description, JournalEntry.reference, Account.code, Account.name)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(Account.type == account_type)
    )
    if search:
        base = base.where(or_(
            JournalEntry.description.ilike(f"%{search}%"),
            JournalEntry.entry_number.ilike(f"%{search}%"),
            Account.name.ilike(f"%{search}%"),
            Account.code.ilike(f"%{search}%"),
        ))
    if account_ids:
        base = base.where(JournalLine.account_id.in_(account_ids))
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
    search: str | None = Query(default=None),
    account_ids: list[str] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await _income_expense_rows(
        db, "revenue", "credit", page, page_size, date_from, date_to, search, account_ids
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
    search: str | None = Query(default=None),
    account_ids: list[str] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await _income_expense_rows(
        db, "expense", "debit", page, page_size, date_from, date_to, search, account_ids
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

    # Counts — hitung baris jurnal aktual (bukan COUNT atas subquery SUM
    # yang selalu mengembalikan satu baris dan karenanya selalu = 1).
    jc = await db.execute(select(func.count()).select_from(JournalEntry))
    journal_count = jc.scalar() or 0
    ac = await db.execute(select(func.count()).select_from(Account))
    account_count = ac.scalar() or 0

    async def _count_type(count_type: str) -> int:
        q = (
            select(func.count(JournalLine.id))
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.type == count_type)
        )
        for cond in conditions:
            q = q.where(cond)
        return (await db.execute(q)).scalar() or 0

    income_count = await _count_type("revenue")
    expense_count = await _count_type("expense")

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


# ── Neraca (Balance Sheet) ─────────────────────────────────────

@router.get(
    "/accounting/balance-sheet",
    response_model=BalanceSheetResponse,
    summary="Neraca (Balance Sheet)",
    description="Laporan posisi keuangan: Aset, Kewajiban, dan Ekuitas.",
)
async def get_balance_sheet(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if date_from:
        conditions.append(JournalEntry.entry_date >= date_from)
    if date_to:
        conditions.append(JournalEntry.entry_date <= date_to)

    async def _section_balance(acc_type: str) -> tuple[list[BalanceSheetAccount], float]:
        stmt = select(Account).where(Account.type == acc_type, Account.is_active == True).order_by(Account.code)
        accounts = (await db.execute(stmt)).scalars().all()
        items = []
        total = 0.0
        for acc in accounts:
            q = (
                select(
                    func.coalesce(func.sum(JournalLine.debit), 0.0),
                    func.coalesce(func.sum(JournalLine.credit), 0.0),
                )
                .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
                .where(JournalLine.account_id == acc.id)
            )
            for cond in conditions:
                q = q.where(cond)
            debit, credit = (await db.execute(q)).one()
            if acc.type in DEBIT_TYPES:
                saldo = round((debit or 0) - (credit or 0), 2)
            else:
                saldo = round((credit or 0) - (debit or 0), 2)
            if saldo != 0:
                items.append(BalanceSheetAccount(
                    account_id=acc.id, account_code=acc.code,
                    account_name=acc.name, balance=saldo,
                ))
                total += saldo
        return items, round(total, 2)

    asset_items, total_assets = await _section_balance("asset")
    liability_items, total_liabilities = await _section_balance("liability")
    equity_items, total_equity = await _section_balance("equity")

    return BalanceSheetResponse(
        assets=BalanceSheetSection(section="Aset", accounts=asset_items, total=total_assets),
        liabilities=BalanceSheetSection(section="Kewajiban", accounts=liability_items, total=total_liabilities),
        equity=BalanceSheetSection(section="Ekuitas", accounts=equity_items, total=total_equity),
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_equity=total_equity,
    )


# ── Rekap Cashflow ─────────────────────────────────────────────

@router.get(
    "/accounting/cashflow",
    response_model=CashflowResponse,
    summary="Rekap Arus Kas (Cashflow)",
    description="Laporan arus kas: operasi, investasi, dan pendanaan.",
)
async def get_cashflow(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    conditions = []
    if date_from:
        conditions.append(JournalEntry.entry_date >= date_from)
    if date_to:
        conditions.append(JournalEntry.entry_date <= date_to)

    # Saldo awal kas/bank
    opening_balance = 0.0
    if date_from:
        pre_cond = [JournalEntry.entry_date < date_from]
        kas_stmt = (
            select(
                func.coalesce(func.sum(JournalLine.debit), 0.0),
                func.coalesce(func.sum(JournalLine.credit), 0.0),
            )
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.type == "asset", or_(Account.name.ilike("Kas%"), Account.name.ilike("Bank%")))
        )
        for pc in pre_cond:
            kas_stmt = kas_stmt.where(pc)
        kas_debit, kas_credit = (await db.execute(kas_stmt)).one()
        opening_balance = round((kas_debit or 0) - (kas_credit or 0), 2)

    async def _cashflow_section(
        section_name: str,
        account_type: str,
        is_inflow: bool,
    ) -> CashflowSection:
        side = "credit" if is_inflow else "debit"
        stmt = (
            select(JournalLine, JournalEntry.description, JournalEntry.entry_date, Account.name, Account.code)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.type == account_type)
        )
        for cond in conditions:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(JournalEntry.entry_date)
        result = await db.execute(stmt)
        items = []
        total = 0.0
        for line, desc, _, acc_name, acc_code in result.all():
            amount = (line.credit if side == "credit" else line.debit) or 0
            if amount > 0:
                items.append(CashflowItem(
                    description=desc,
                    amount=amount,
                    category=acc_name,
                    account_code=acc_code or "",
                    account_name=acc_name or "",
                ))
                total += amount
        return CashflowSection(section=section_name, items=items, total=round(total, 2))

    operating = await _cashflow_section("Arus Kas Operasi", "revenue", True)
    operating_expense = await _cashflow_section("Arus Kas Operasi", "expense", False)
    operating.total = round(operating.total - operating_expense.total, 2)
    operating.items.extend(operating_expense.items)

    investing = CashflowSection(section="Arus Kas Investasi", items=[], total=0)
    financing = CashflowSection(section="Arus Kas Pendanaan", items=[], total=0)

    net_cashflow = round(operating.total + investing.total + financing.total, 2)

    # Saldo akhir
    all_conditions = conditions.copy()
    kas_stmt_end = (
        select(
            func.coalesce(func.sum(JournalLine.debit), 0.0),
            func.coalesce(func.sum(JournalLine.credit), 0.0),
        )
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(Account.type == "asset", or_(Account.name.ilike("Kas%"), Account.name.ilike("Bank%")))
    )
    for cond in all_conditions:
        kas_stmt_end = kas_stmt_end.where(cond)
    kas_debit_end, kas_credit_end = (await db.execute(kas_stmt_end)).one()
    closing_balance = round((kas_debit_end or 0) - (kas_credit_end or 0), 2)

    return CashflowResponse(
        operating=operating,
        investing=investing,
        financing=financing,
        net_cashflow=net_cashflow,
        opening_balance=opening_balance,
        closing_balance=closing_balance,
    )


# ── Rekap Biaya (Cost Recap) ───────────────────────────────────

@router.get(
    "/accounting/cost-recap",
    response_model=CostRecapResponse,
    summary="Rekap Biaya",
    description="Rekap seluruh biaya (expense) yang dikelompokkan per akun.",
)
async def get_cost_recap(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    conditions = [Account.type == "expense"]
    if date_from:
        conditions.append(JournalEntry.entry_date >= date_from)
    if date_to:
        conditions.append(JournalEntry.entry_date <= date_to)

    stmt = (
        select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date,
               JournalEntry.description, JournalEntry.reference, Account.code, Account.name)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(and_(*conditions))
        .order_by(Account.code, JournalEntry.entry_date)
    )
    result = await db.execute(stmt)
    rows_data = result.all()

    groups_map: dict[str, dict] = {}
    total_cost = 0.0
    for line, entry_number, entry_date, desc, ref, code, name in rows_data:
        amount = (line.debit or 0) - (line.credit or 0)
        if amount <= 0:
            continue
        if code not in groups_map:
            groups_map[code] = {"code": code, "name": name, "total": 0.0, "items": []}
        groups_map[code]["items"].append(CostRecapRow(
            id=line.id, entry_date=entry_date, description=desc,
            account_code=code, account_name=name, amount=round(amount, 2), reference=ref,
        ))
        groups_map[code]["total"] = round(groups_map[code]["total"] + amount, 2)
        total_cost += amount

    groups = [
        CostRecapGroup(account_code=g["code"], account_name=g["name"], total=g["total"], items=g["items"])
        for g in groups_map.values()
    ]

    return CostRecapResponse(total_cost=round(total_cost, 2), groups=groups)


# ── Rekap Monitoring ───────────────────────────────────────────

@router.get(
    "/accounting/monitoring",
    response_model=MonitoringResponse,
    summary="Rekap Monitoring Bulanan",
    description="Rekap monitoring pendapatan, biaya, dan margin per bulan. Filter memakai range tanggal `date_from`/`date_to` (default: tahun berjalan).",
)
async def get_monitoring(
    date_from: date | None = Query(default=None, description="Awal periode (default: 1 Januari tahun berjalan)"),
    date_to: date | None = Query(default=None, description="Akhir periode (default: 31 Desember tahun berjalan)"),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    start_date = date_from or date(today.year, 1, 1)
    end_date = date_to or date(today.year, 12, 31)

    bulan_names = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ]

    rows = []
    totals = {"invoice": 0, "modal": 0, "oat": 0, "gm": 0, "penghasilan": 0, "operasional": 0, "fee": 0}

    # Iterasi per bulan dalam rentang
    current = date(start_date.year, start_date.month, 1)
    while current <= end_date:
        bulan = current.month
        month_end = date(current.year if bulan < 12 else current.year + 1, bulan + 1 if bulan < 12 else 1, 1)
        month_start = current
        actual_start = max(month_start, start_date)
        actual_end = min(month_end, date(end_date.year + 1, 1, 1))

        # Pendapatan (revenue credit)
        rev_stmt = (
            select(func.coalesce(func.sum(JournalLine.credit), 0.0))
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.type == "revenue", JournalEntry.entry_date >= actual_start, JournalEntry.entry_date < actual_end)
        )
        penghasilan = round((await db.execute(rev_stmt)).scalar() or 0, 2)

        # Expense (expense debit)
        exp_stmt = (
            select(func.coalesce(func.sum(JournalLine.debit), 0.0))
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.type == "expense", JournalEntry.entry_date >= actual_start, JournalEntry.entry_date < actual_end)
        )
        operasional = round((await db.execute(exp_stmt)).scalar() or 0, 2)

        # Invoice (total revenue transactions)
        inv_count_stmt = (
            select(func.count(JournalLine.id))
            .select_from(JournalLine)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.type == "revenue", JournalLine.credit > 0,
                   JournalEntry.entry_date >= actual_start, JournalEntry.entry_date < actual_end)
        )
        invoice_count = (await db.execute(inv_count_stmt)).scalar() or 0

        # Fee manajemen (4% of revenue)
        fee_manajemen = round(penghasilan * 0.04, 2)

        # OAT = revenue from "Pendapatan Jasa Angkut" (4-1100)
        oat_stmt = (
            select(func.coalesce(func.sum(JournalLine.credit), 0.0))
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalLine.account_id == Account.id)
            .where(Account.code == "4-1100",
                   JournalEntry.entry_date >= actual_start, JournalEntry.entry_date < actual_end)
        )
        oat = round((await db.execute(oat_stmt)).scalar() or 0, 2)

        # Modal Elnusa (estimated as 60% of revenue)
        modal_elnusa = round(penghasilan * 0.6, 2)

        gross_margin = round(penghasilan - operasional, 2)

        rows.append(MonitoringRow(
            bulan=bulan_names[bulan],
            invoice=invoice_count,
            modal_elnusa=modal_elnusa,
            oat=oat,
            gross_margin=gross_margin,
            penghasilan=penghasilan,
            operasional=operasional,
            fee_manajemen=fee_manajemen,
        ))
        totals["invoice"] += invoice_count
        totals["modal"] += modal_elnusa
        totals["oat"] += oat
        totals["gm"] += gross_margin
        totals["penghasilan"] += penghasilan
        totals["operasional"] += operasional
        totals["fee"] += fee_manajemen

        # Next month
        current = month_end

    return MonitoringResponse(
        rows=rows,
        total_invoice=totals["invoice"],
        total_modal=round(totals["modal"], 2),
        total_oat=round(totals["oat"], 2),
        total_gross_margin=round(totals["gm"], 2),
        total_penghasilan=round(totals["penghasilan"], 2),
        total_operasional=round(totals["operasional"], 2),
        total_fee_manajemen=round(totals["fee"], 2),
    )


# ── Kas Harian (Daily Cash) ────────────────────────────────────

@router.get(
    "/accounting/daily-cash",
    response_model=DailyCashResponse,
    summary="Kas Harian",
    description="Mutasi kas/bank harian dengan saldo berjalan.",
)
async def get_daily_cash(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    account_ids: list[str] | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    # Cari akun Kas/Bank
    kas_stmt = select(Account).where(
        Account.type == "asset",
        or_(Account.name.ilike("Kas%"), Account.name.ilike("Bank%")),
        Account.is_active == True,
    ).order_by(Account.code)
    kas_accounts = (await db.execute(kas_stmt)).scalars().all()
    kas_ids = [a.id for a in kas_accounts]

    if not kas_ids:
        return DailyCashResponse(opening_balance=0, closing_balance=0, total_debit=0, total_credit=0, rows=[])

    conditions = [JournalLine.account_id.in_(kas_ids)]
    if account_ids:
        conditions = [JournalLine.account_id.in_(account_ids)]
    if date_from:
        conditions.append(JournalEntry.entry_date >= date_from)
    if date_to:
        conditions.append(JournalEntry.entry_date <= date_to)

    # Saldo awal
    opening_balance = 0.0
    if date_from:
        pre_cond = [JournalLine.account_id.in_(kas_ids), JournalEntry.entry_date < date_from]
        pre_stmt = (
            select(
                func.coalesce(func.sum(JournalLine.debit), 0.0),
                func.coalesce(func.sum(JournalLine.credit), 0.0),
            )
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .where(and_(*pre_cond))
        )
        pre_debit, pre_credit = (await db.execute(pre_stmt)).one()
        opening_balance = round((pre_debit or 0) - (pre_credit or 0), 2)

    stmt = (
        select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date,
               JournalEntry.description, JournalEntry.reference, Account.code, Account.name)
        .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
        .join(Account, JournalLine.account_id == Account.id)
        .where(and_(*conditions))
        .order_by(JournalEntry.entry_date, JournalLine.created_at)
    )
    result = await db.execute(stmt)
    rows_data = result.all()

    balance = opening_balance
    total_debit = 0.0
    total_credit = 0.0
    daily_rows = []
    for line, entry_number, entry_date, desc, ref, code, name in rows_data:
        debit = line.debit or 0
        credit = line.credit or 0
        balance = round(balance + debit - credit, 2)
        total_debit += debit
        total_credit += credit
        daily_rows.append(DailyCashRow(
            id=line.id, entry_date=entry_date, description=desc,
            account_code=code, account_name=name,
            debit=debit, credit=credit, balance=balance,
            reference=ref,
        ))

    return DailyCashResponse(
        opening_balance=opening_balance,
        closing_balance=balance,
        total_debit=round(total_debit, 2),
        total_credit=round(total_credit, 2),
        rows=daily_rows,
    )


# ── Rekap Bunga Bank ───────────────────────────────────────────

@router.get(
    "/accounting/bank-interest",
    response_model=BankInterestResponse,
    summary="Rekap Bunga Bank",
    description="Rekap bunga bank: pinjaman, pembayaran, dan kalkulasi bunga.",
)
async def get_bank_interest(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    # Cari akun pinjaman (liability) dan beban bunga (expense)
    loan_stmt = select(Account).where(
        Account.type == "liability",
        Account.name.ilike("%pinjaman%"),
        Account.is_active == True,
    )
    loan_accounts = (await db.execute(loan_stmt)).scalars().all()

    interest_stmt = select(Account).where(
        Account.type == "expense",
        Account.name.ilike("%bunga%"),
        Account.is_active == True,
    )
    interest_accounts = (await db.execute(interest_stmt)).scalars().all()

    loan_ids = [a.id for a in loan_accounts]
    interest_ids = [a.id for a in interest_accounts]

    conditions = []
    if date_from:
        conditions.append(JournalEntry.entry_date >= date_from)
    if date_to:
        conditions.append(JournalEntry.entry_date <= date_to)

    rows = []
    total_principal = 0.0
    total_interest = 0.0
    total_paid = 0.0

    # Data pinjaman (credit liability)
    loan_code_name = {a.id: (a.code, a.name) for a in loan_accounts}
    interest_code_name = {a.id: (a.code, a.name) for a in interest_accounts}

    if loan_ids:
        stmt = (
            select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date,
                   JournalEntry.description, JournalEntry.reference)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .where(JournalLine.account_id.in_(loan_ids), JournalLine.credit > 0)
        )
        for cond in conditions:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(JournalEntry.entry_date)
        result = await db.execute(stmt)
        for line, entry_number, entry_date, desc, ref in result.all():
            amount = line.credit or 0
            total_principal += amount
            interest_val = round(amount * 0.06 / 12, 2)  # estimasi 6% p.a / 12 bulan
            code, name = loan_code_name.get(line.account_id, ("", ""))
            rows.append(BankInterestRow(
                id=line.id, entry_date=entry_date, description=desc,
                account_code=code, account_name=name,
                amount=amount, interest_rate=6.0, days=30,
                interest_amount=interest_val, reference=ref,
            ))
            total_interest += interest_val

    # Pembayaran bunga (debit expense)
    if interest_ids:
        stmt = (
            select(JournalLine, JournalEntry.entry_number, JournalEntry.entry_date,
                   JournalEntry.description, JournalEntry.reference)
            .join(JournalEntry, JournalLine.journal_entry_id == JournalEntry.id)
            .where(JournalLine.account_id.in_(interest_ids), JournalLine.debit > 0)
        )
        for cond in conditions:
            stmt = stmt.where(cond)
        stmt = stmt.order_by(JournalEntry.entry_date)
        result = await db.execute(stmt)
        for line, entry_number, entry_date, desc, ref in result.all():
            amount = line.debit or 0
            total_paid += amount
            code, name = interest_code_name.get(line.account_id, ("", ""))
            rows.append(BankInterestRow(
                id=line.id, entry_date=entry_date, description=desc,
                account_code=code, account_name=name,
                amount=amount, interest_rate=6.0, days=30,
                interest_amount=0.0, reference=ref,
            ))

    return BankInterestResponse(
        total_principal=round(total_principal, 2),
        total_interest=round(total_interest, 2),
        total_paid=round(total_paid, 2),
        rows=rows,
    )
