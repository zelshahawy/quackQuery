from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""

    # Gemini API
    gemini_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    app_host: str = "127.0.0.1"
    app_port: int = 8080
    app_reload: bool = True

    # Paths
    data_dir: Path = Path("data")
    uploads_dir: Path = Path("uploads")
    duckdb_path: Path = Path("data/quick_query.duckdb")
    meta_db_path: Path = Path("data/meta.sqlite3")
    cache_dir: Path = Path("data/cache")
    chroma_dir: Path = Path("data/chroma")

    # Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    storage_secret: str = "your-storage-secret-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
