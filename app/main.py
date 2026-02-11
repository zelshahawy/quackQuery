from __future__ import annotations

from nicegui import ui
from app.ui.pages.home import home_page
from app.ui.pages.datasource import datasource_page
from app.ui.pages.ask import ask_page
from app.ui.pages.history import history_page
from app.db.meta import init_meta_db


def main() -> None:
    init_meta_db()

    _ = ui.page("/")(home_page)
    _ = ui.page("/datasources")(datasource_page)
    _ = ui.page("/ask")(ask_page)
    _ = ui.page("/history")(history_page)

    _ = ui.run(  # pyright: ignore[reportUnknownMemberType]
        title="Quack Query",
        reload=True,
        host="127.0.0.1",
        port=8080,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
