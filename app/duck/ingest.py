from __future__ import annotations

from pathlib import Path
import re
from app.duck.engine import get_conn


_VALID_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def safe_ident(name: str) -> str:
    if not _VALID_IDENT.match(name):
        raise ValueError(f"Unsafe identifier: {name!r}")
    return name


def register_csv_as_table(*, csv_path: Path, table_name: str) -> None:
    table = safe_ident(table_name)
    conn = get_conn()
    try:
        _ = conn.execute(
            f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT * FROM read_csv_auto(?, HEADER=TRUE);
            """,
            [str(csv_path)],
        )
    finally:
        conn.close()


def get_schema(table_name: str) -> list[tuple[str, str]]:
    table = safe_ident(table_name)
    conn = get_conn()
    try:
        rows = conn.execute(f"DESCRIBE {table};").fetchall()
        # DESCRIBE returns: column_name, column_type, null, key, default, extra
        return [(r[0], r[1]) for r in rows]
    finally:
        conn.close()
