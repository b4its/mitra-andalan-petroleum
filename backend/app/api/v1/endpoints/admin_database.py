from datetime import date, datetime
from io import BytesIO

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select, text

from app.core.database import Base, engine
import app.models  # noqa: F401 - ensure all tables are registered in metadata

router = APIRouter(prefix="/admin/database")

MAX_SQL_SIZE = 50 * 1024 * 1024


def _quote_identifier(value: str) -> str:
    return f"`{value.replace('`', '``')}`"


def _literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (datetime, date)):
        value = value.isoformat(sep=" ", timespec="seconds") if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, bytes):
        return f"X'{value.hex()}'"

    escaped = str(value).replace("\\", "\\\\").replace("'", "''").replace("\x00", "")
    return f"'{escaped}'"


def _split_sql(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escape = False
    line_comment = False
    block_comment = False
    i = 0

    while i < len(sql):
        char = sql[i]
        next_char = sql[i + 1] if i + 1 < len(sql) else ""

        if line_comment:
            current.append(char)
            if char == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment:
            current.append(char)
            if char == "*" and next_char == "/":
                current.append(next_char)
                block_comment = False
                i += 2
                continue
            i += 1
            continue

        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            i += 1
            continue

        if char in {"'", '"', "`"}:
            quote = char
            current.append(char)
        elif char == "-" and next_char == "-":
            line_comment = True
            current.append(char)
        elif char == "#":
            line_comment = True
            current.append(char)
        elif char == "/" and next_char == "*":
            block_comment = True
            current.append(char)
        elif char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)
        i += 1

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return statements


@router.get(
    "/export",
    summary="Export data SQL",
    description="Export seluruh data database sebagai SQL data-only berisi DELETE dan INSERT.",
)
async def export_database():
    tables = Base.metadata.sorted_tables
    lines = [
        "-- Mandalan data export",
        f"-- Generated at {datetime.utcnow().isoformat(timespec='seconds')}Z",
        "SET FOREIGN_KEY_CHECKS=0;",
        "",
    ]

    async with engine.connect() as conn:
        for table in reversed(tables):
            lines.append(f"DELETE FROM {_quote_identifier(table.name)};")
        lines.append("")

        for table in tables:
            result = await conn.execute(select(table))
            rows = result.mappings().all()
            if not rows:
                continue

            columns = list(table.columns)
            column_names = ", ".join(_quote_identifier(column.name) for column in columns)
            lines.append(f"-- Data for {table.name}")
            for row in rows:
                values = ", ".join(_literal(row[column.name]) for column in columns)
                lines.append(f"INSERT INTO {_quote_identifier(table.name)} ({column_names}) VALUES ({values});")
            lines.append("")

    lines.append("SET FOREIGN_KEY_CHECKS=1;")
    content = "\n".join(lines).encode("utf-8")
    filename = f"mandalan-data-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.sql"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(BytesIO(content), media_type="application/sql", headers=headers)


@router.post(
    "/import",
    summary="Import data SQL",
    description="Import file .sql dan jalankan statement SQL secara berurutan.",
)
async def import_database(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".sql"):
        raise HTTPException(status_code=400, detail="File harus berformat .sql")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File SQL tidak boleh kosong")
    if len(content) > MAX_SQL_SIZE:
        raise HTTPException(status_code=400, detail="File SQL terlalu besar (max 50MB)")

    sql = content.decode("utf-8-sig", errors="strict")
    statements = _split_sql(sql)
    if not statements:
        raise HTTPException(status_code=400, detail="Tidak ada statement SQL yang dapat dijalankan")

    async with engine.begin() as conn:
        try:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            for statement in statements:
                await conn.execute(text(statement))
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        except Exception as exc:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            raise HTTPException(status_code=400, detail=f"Import SQL gagal: {exc}") from exc

    return {"message": "Import SQL berhasil", "statements": len(statements)}


@router.post(
    "/clear",
    summary="Bersihkan database",
    description="Hapus seluruh data dari semua tabel aplikasi.",
)
async def clear_database():
    tables = list(Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            for table in reversed(tables):
                await conn.execute(text(f"DELETE FROM {_quote_identifier(table.name)}"))
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        except Exception as exc:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            raise HTTPException(status_code=400, detail=f"Bersihkan database gagal: {exc}") from exc

    return {"message": "Database berhasil dibersihkan", "tables": len(tables)}
