from __future__ import annotations

from nicegui import ui

from app.config import settings
from app.db.meta import init_meta_db
from app.db.users import init_users_db
from app.ui.pages.ask import ask_page
from app.ui.pages.datasource import datasource_page
from app.ui.pages.history import history_page
from app.ui.pages.home import home_page
from app.ui.pages.login import login_page


def main() -> None:
    init_meta_db()
    init_users_db()

    # Global styling - must be before page registration
    _ = ui.add_head_html(
        """
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        body {
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            min-height: 100vh;
        }
        .nicegui-card {
            border-radius: 12px;
        }
        .nicegui-button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .nicegui-button:hover {
            transform: translateY(-2px);
        }
    </style>
    """,
        shared=True,
    )

    # Register pages
    _ = ui.page("/")(home_page)
    _ = ui.page("/datasources")(datasource_page)
    _ = ui.page("/ask")(ask_page)
    _ = ui.page("/history")(history_page)
    _ = ui.page("/login")(login_page)

    _ = ui.run(
        title="Quack Query",
        reload=settings.app_reload,
        host=settings.app_host,
        port=settings.app_port,
        storage_secret=settings.storage_secret,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
