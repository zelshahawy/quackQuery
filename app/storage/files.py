from __future__ import annotations

from pathlib import Path
import uuid


UPLOAD_DIR = Path("uploads")


def save_upload_to_disk(filename: str, content: bytes) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = filename.replace("/", "_").replace("\\", "_")
    out = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    _ = out.write_bytes(content)
    return out
