from __future__ import annotations

from nicegui import ui

from app.db.meta import list_datasets
from app.ui.middleware import check_auth


def logout() -> None:
    """Logout user."""
    from nicegui import app as nicegui_app

    if "token" in nicegui_app.storage.general:
        del nicegui_app.storage.general["token"]
    ui.navigate.to("/login")


def home_page() -> None:
    # Check auth
    username = check_auth()
    if not username:
        ui.navigate.to("/login")
        return

    # Header
    with ui.header().classes(
        "bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-lg"
    ):
        with ui.row().classes("w-full items-center justify-between px-8 py-6"):
            with ui.column().classes("gap-1"):
                ui.label("Quack Query").classes("text-4xl font-black tracking-tight")
                ui.label("AI-powered data exploration").classes(
                    "text-sm text-slate-300"
                )

            with ui.row().classes("gap-2 items-center"):
                ui.label(f"Welcome, {username}").classes("text-white")
                ui.button("Logout", on_click=logout).props("flat").classes(
                    "text-white hover:text-slate-200"
                )

    with ui.column().classes("w-full max-w-6xl mx-auto px-8 py-8 gap-8"):
        # Navigation cards
        with ui.row().classes("gap-4 w-full"):
            with ui.card().classes(
                "flex-1 bg-gradient-to-br from-blue-50 to-blue-100 border-0 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            ):
                ui.button(
                    "Ask Questions", on_click=lambda: ui.navigate.to("/ask")
                ).props("flat").classes("w-full text-lg font-semibold text-blue-900")
                ui.label("Convert natural language to SQL").classes(
                    "text-sm text-blue-700 px-6 pb-4"
                )

            with ui.card().classes(
                "flex-1 bg-gradient-to-br from-purple-50 to-purple-100 border-0 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            ):
                ui.button(
                    "Data Sources", on_click=lambda: ui.navigate.to("/datasources")
                ).props("flat").classes("w-full text-lg font-semibold text-purple-900")
                ui.label("Upload and manage datasets").classes(
                    "text-sm text-purple-700 px-6 pb-4"
                )

            with ui.card().classes(
                "flex-1 bg-gradient-to-br from-amber-50 to-amber-100 border-0 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            ):
                ui.button("History", on_click=lambda: ui.navigate.to("/history")).props(
                    "flat"
                ).classes("w-full text-lg font-semibold text-amber-900")
                ui.label("View past queries").classes(
                    "text-sm text-amber-700 px-6 pb-4"
                )

        # Datasets section
        ds = list_datasets()

        with ui.column().classes("gap-4"):
            with ui.row().classes("items-center gap-2"):
                ui.label("Datasets").classes("text-2xl font-bold text-slate-900")
                ui.badge(str(len(ds))).classes(
                    "bg-slate-200 text-slate-900 text-lg px-3 py-1"
                )

            if not ds:
                with ui.card().classes(
                    "w-full bg-slate-50 border border-dashed border-slate-300 p-8 text-center"
                ):
                    ui.label("No datasets yet").classes(
                        "text-lg font-semibold text-slate-600"
                    )
                    ui.label("Upload a CSV to get started").classes(
                        "text-sm text-slate-500 mt-2"
                    )
                    ui.button(
                        "Upload Dataset",
                        on_click=lambda: ui.navigate.to("/datasources"),
                    ).props("outline").classes("mt-4")
            else:
                with ui.column().classes("gap-3 w-full"):
                    for d in ds[:10]:
                        with ui.card().classes(
                            "w-full bg-white border border-slate-200 hover:border-slate-400 hover:shadow-md transition-all"
                        ):
                            with ui.row().classes("w-full items-start justify-between"):
                                with ui.column().classes("gap-2 flex-1"):
                                    ui.label(d.name).classes(
                                        "font-semibold text-slate-900 text-lg"
                                    )
                                    ui.label(f"Table: {d.table_name}").classes(
                                        "text-xs font-mono bg-slate-100 text-slate-700 px-2 py-1 rounded w-fit"
                                    )
                                    ui.label(f"Created: {d.created_at[:10]}").classes(
                                        "text-xs text-slate-500"
                                    )
                                ui.button(
                                    "Query", on_click=lambda: ui.navigate.to("/ask")
                                ).props("flat").classes(
                                    "text-blue-600 hover:text-blue-800"
                                )
