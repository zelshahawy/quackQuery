from __future__ import annotations

import uuid
from pathlib import Path

from app.config import settings


def save_upload_to_disk(filename: str, content: bytes) -> Path:
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    safe_name = filename.replace("/", "_").replace("\\", "_")
    out = settings.uploads_dir / f"{uuid.uuid4().hex}_{safe_name}"
    _ = out.write_bytes(content)
    return out
