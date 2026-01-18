from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

META_DB_PATH = Path("data/meta.sqlite3")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_meta_db() -> None:
    META_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(META_DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS datasets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                table_name TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS queries (
                id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL,
                question TEXT NOT NULL,
                sql TEXT NOT NULL,
                ok INTEGER NOT NULL,
                error TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(dataset_id) REFERENCES datasets(id)
            );
            """
        )


@dataclass(frozen=True)
class Dataset:
    id: str
    name: str
    table_name: str
    file_path: str
    created_at: str


@dataclass(frozen=True)
class QueryLog:
    id: str
    dataset_id: str
    question: str
    sql: str
    ok: int
    error: str | None
    created_at: str


def add_dataset(*, dataset_id: str, name: str, table_name: str, file_path: str) -> None:
    with sqlite3.connect(META_DB_PATH) as conn:
        _ = conn.execute(
            "INSERT INTO datasets (id, name, table_name, file_path, created_at) VALUES (?, ?, ?, ?, ?)",
            (dataset_id, name, table_name, file_path, _utcnow_iso()),
        )


def list_datasets() -> list[Dataset]:
    with sqlite3.connect(META_DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, name, table_name, file_path, created_at FROM datasets ORDER BY created_at DESC"
        ).fetchall()
    return [Dataset(*row) for row in rows]


def get_dataset(dataset_id: str) -> Dataset | None:
    with sqlite3.connect(META_DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, name, table_name, file_path, created_at FROM datasets WHERE id = ?",
            (dataset_id,),
        ).fetchone()
    return Dataset(*row) if row else None


def add_query_log(
    *,
    query_id: str,
    dataset_id: str,
    question: str,
    sql: str,
    ok: bool,
    error: str | None,
) -> None:
    with sqlite3.connect(META_DB_PATH) as conn:
        conn.execute(
            "INSERT INTO queries (id, dataset_id, question, sql, ok, error, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (query_id, dataset_id, question, sql, 1 if ok else 0, error, _utcnow_iso()),
        )


def list_query_logs(limit: int = 50) -> list[QueryLog]:
    with sqlite3.connect(META_DB_PATH) as conn:
        rows: list[tuple[Any, ...]] = conn.execute(
            """
            SELECT id, dataset_id, question, sql, ok, error, created_at
            FROM queries
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [QueryLog(*row) for row in rows]
