from __future__ import annotations

from typing import Any

from app.config import settings
from app.core.auth import verify_token
from app.db.users import get_user_by_id


class Container:
    """Dependency injection container."""

    @staticmethod
    def get_current_user(token: str) -> dict[str, Any] | None:
        """Get current user from token."""
        payload = verify_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        user = get_user_by_id(user_id)
        return (
            {"id": user.id, "username": user.username, "email": user.email}
            if user
            else None
        )

    @staticmethod
    def get_settings() -> Any:
        """Get application settings."""
        return settings


# Global container instance
container = Container()
