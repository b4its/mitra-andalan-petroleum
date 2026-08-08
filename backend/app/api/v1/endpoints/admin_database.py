from datetime import date, datetime, timezone
from io import BytesIO

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select, text

from app.core.database import Base, engine
import app.models  # noqa: F401 - ensure all tables are registered in metadata

router = APIRouter(prefix="/admin/database")

MAX_SQL_SIZE = 50 * 1024 * 1024


def _is_mysql() -> bool:
    return (engine.dialect.name or "").lower() == "mysql"


def _is_sqlite() -> bool:
    return (engine.dialect.name or "").lower() == "sqlite"


def _fk_checks_sql(enable: bool) -> str | None:
    """Statement untuk mematikan/menyalakan foreign key checks sesuai dialect DB."""
    if _is_mysql():
        return f"SET FOREIGN_KEY_CHECKS={1 if enable else 0}"
    if _is_sqlite():
        return f"PRAGMA foreign_keys={'ON' if enable else 'OFF'}"
    return None


def _quote_identifier(value: str) -> str:
    return f"`{value.replace('`', '``')}`"


async def _schema_statements(conn) -> list[str]:
    """Ambil statement CREATE TABLE dari database aktual.

    - MySQL  : pakai SHOW CREATE TABLE (mencakup semua kolom, termasuk
               kolom hasil ALTER TABLE yang mungkin tidak ada di model)
    - SQLite : pakai sqlite_master
    """
    statements: list[str] = []
    if _is_mysql():
        result = await conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result.all()]
        for table in sorted(tables):
            create = (
                await conn.execute(
                    text(f"SHOW CREATE TABLE {_quote_identifier(table)}")
                )
            ).first()
            if create:
                # MySQL mengembalikan (table_name, create_statement)
                stmt = create[1]
                statements.append(f"{stmt};")
    elif _is_sqlite():
        result = await conn.execute(
            text(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        )
        for name, sql in result.all():
            if sql:
                statements.append(f"{sql};")
    return statements


def _literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        # Hilangkan timezone offset agar format 'YYYY-MM-DD HH:MM:SS'
        # diterima oleh MySQL DATETIME (offset '+00:00' ditolak MySQL).
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        value = value.isoformat(sep=" ", timespec="seconds")
    elif isinstance(value, date):
        value = value.isoformat()
    if isinstance(value, bytes):
        return f"X'{value.hex()}'"

    escaped = str(value).replace("\\", "\\\\").replace("'", "''").replace("\x00", "")
    return f"'{escaped}'"


def _split_sql(sql: str) -> list[str]:
    """Pisahkan file SQL menjadi statement per ';'.

    Komentar (--, #, /* */) diabaikan dan statement yang hanya berisi
    komentar tidak dimasukkan ke hasil.
    """
    statements: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escape = False
    line_comment = False
    block_comment = False
    i = 0

    def _flush():
        statement = "".join(current).strip()
        if statement:
            statements.append(statement)
        current.clear()

    while i < len(sql):
        char = sql[i]
        next_char = sql[i + 1] if i + 1 < len(sql) else ""

        # Di dalam string literal ('...', "...", `...`)
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

        # Komentar satu baris (-- atau #) — lewati sampai akhir baris
        if line_comment:
            if char == "\n":
                line_comment = False
                current.append(" ")
            i += 1
            continue

        # Komentar blok (/* ... */) — lewati seluruhnya
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                i += 2
            else:
                i += 1
            continue

        if char in {"'", '"', "`"}:
            quote = char
            current.append(char)
            i += 1
        elif char == "-" and next_char == "-":
            line_comment = True
            i += 2
        elif char == "#":
            line_comment = True
            i += 1
        elif char == "/" and next_char == "*":
            block_comment = True
            i += 2
        elif char == ";":
            _flush()
            i += 1
        else:
            current.append(char)
            i += 1

    _flush()
    return statements


@router.get(
    "/export",
    summary="Export data SQL",
    description="Export lengkap database: struktur tabel (CREATE TABLE) + data (DELETE dan INSERT).",
)
async def export_database():
    tables = Base.metadata.sorted_tables
    lines = [
        "-- Mandalan full database export",
        f"-- Generated at {datetime.utcnow().isoformat(timespec='seconds')}Z",
    ]
    fk_off = _fk_checks_sql(False)
    fk_on = _fk_checks_sql(True)
    if fk_off:
        lines.append(f"{fk_off};")
    lines.append("")

    async with engine.connect() as conn:
        # 1. Struktur tabel: DROP (urutan terbalik utk FK) lalu CREATE
        lines.append("-- ============================================")
        lines.append("-- STRUKTUR TABEL")
        lines.append("-- ============================================")
        for table in reversed(tables):
            lines.append(f"DROP TABLE IF EXISTS {_quote_identifier(table.name)};")
        lines.append("")
        schema = await _schema_statements(conn)
        if not schema:
            # Fallback: bangun CREATE TABLE dari metadata model
            from sqlalchemy.schema import CreateTable
            for table in tables:
                ddl = str(CreateTable(table).compile(dialect=engine.dialect))
                lines.append(f"{ddl};")
        else:
            for stmt in schema:
                lines.append(stmt)
        lines.append("")

        # 2. Data (INSERT)
        lines.append("-- ============================================")
        lines.append("-- DATA")
        lines.append("-- ============================================")
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

    if fk_on:
        lines.append(f"{fk_on};")
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

    fk_off = _fk_checks_sql(False)
    fk_on = _fk_checks_sql(True)

    async with engine.begin() as conn:
        try:
            if fk_off:
                await conn.execute(text(fk_off))
            for statement in statements:
                await conn.execute(text(statement))
            if fk_on:
                await conn.execute(text(fk_on))
        except Exception as exc:
            if fk_on:
                await conn.execute(text(fk_on))
            raise HTTPException(status_code=400, detail=f"Import SQL gagal: {exc}") from exc

    return {"message": "Import SQL berhasil", "statements": len(statements)}


@router.post(
    "/clear",
    summary="Bersihkan database",
    description="Hapus seluruh data dari semua tabel aplikasi.",
)
async def clear_database():
    tables = list(Base.metadata.sorted_tables)
    fk_off = _fk_checks_sql(False)
    fk_on = _fk_checks_sql(True)
    async with engine.begin() as conn:
        try:
            if fk_off:
                await conn.execute(text(fk_off))
            for table in reversed(tables):
                await conn.execute(text(f"DELETE FROM {_quote_identifier(table.name)}"))
            if fk_on:
                await conn.execute(text(fk_on))
        except Exception as exc:
            if fk_on:
                await conn.execute(text(fk_on))
            raise HTTPException(status_code=400, detail=f"Bersihkan database gagal: {exc}") from exc

    return {"message": "Database berhasil dibersihkan", "tables": len(tables)}
