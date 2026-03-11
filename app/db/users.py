from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.config import settings
from app.core.auth import hash_password, verify_password


@dataclass(frozen=True)
class User:
    id: str
    username: str
    email: str
    hashed_password: str


def init_users_db() -> None:
    """Initialize users table."""
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.meta_db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def create_user(user_id: str, username: str, email: str, password: str) -> User:
    """Create a new user."""
    hashed_password = hash_password(password)

    with sqlite3.connect(settings.meta_db_path) as conn:
        conn.execute(
            """
            INSERT INTO users (id, username, email, hashed_password, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (user_id, username, email, hashed_password),
        )

    return User(
        id=user_id, username=username, email=email, hashed_password=hashed_password
    )


def get_user_by_username(username: str) -> User | None:
    """Get user by username."""
    with sqlite3.connect(settings.meta_db_path) as conn:
        row = conn.execute(
            "SELECT id, username, email, hashed_password FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    return User(*row) if row else None


def get_user_by_id(user_id: str) -> User | None:
    """Get user by ID."""
    with sqlite3.connect(settings.meta_db_path) as conn:
        row = conn.execute(
            "SELECT id, username, email, hashed_password FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    return User(*row) if row else None


def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate user with username and password."""
    user = get_user_by_username(username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
