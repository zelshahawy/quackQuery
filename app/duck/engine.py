from __future__ import annotations

import duckdb

from app.config import settings


def get_conn() -> duckdb.DuckDBPyConnection:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(settings.duckdb_path), read_only=False)
    _ = conn.execute("PRAGMA threads=4;")
    return conn
