from __future__ import annotations

from pathlib import Path
import duckdb

DUCK_DB_PATH = Path("data/quick_query.duckdb")


def get_conn() -> duckdb.DuckDBPyConnection:
    DUCK_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DUCK_DB_PATH), read_only=False)
    _ = conn.execute("PRAGMA threads=4;")
    return conn
