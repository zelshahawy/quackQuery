from __future__ import annotations

from nicegui import app as nicegui_app
from nicegui import ui

from app.core.auth import verify_token


def check_auth() -> str | None:
    """Check if user is authenticated. Returns username if authenticated, None otherwise."""
    # Get token from server-side general storage
    token = nicegui_app.storage.general.get("token")

    if not token:
        return None

    payload = verify_token(token)
    if not payload:
        return None

    return payload.get("sub")


def require_auth() -> None:
    """Redirect to login if not authenticated."""
    if not check_auth():
        ui.navigate.to("/login")
