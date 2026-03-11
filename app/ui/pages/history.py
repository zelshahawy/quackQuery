from __future__ import annotations

from nicegui import ui

from app.db.meta import get_dataset, list_query_logs
from app.ui.middleware import check_auth


def history_page() -> None:
    # Check auth
    username = check_auth()
    if not username:
        ui.navigate.to("/login")
        return

    # Header
    with ui.header().classes(
        "bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-lg"
    ):
        with ui.row().classes("w-full items-center gap-4 px-8 py-6"):
            ui.button("←", on_click=lambda: ui.navigate.to("/")).props("flat").classes(
                "text-2xl text-white"
            )
            ui.label("Query History").classes("text-3xl font-black tracking-tight")

    with ui.column().classes("w-full max-w-6xl mx-auto px-8 py-8 gap-6"):
        logs = list_query_logs(limit=100)

        if not logs:
            with ui.card().classes(
                "w-full bg-slate-50 border border-dashed border-slate-300 p-8 text-center"
            ):
                ui.label("No queries yet").classes(
                    "text-lg font-semibold text-slate-600"
                )
                ui.label("Start by asking questions in the Ask section").classes(
                    "text-sm text-slate-500 mt-2"
                )
                ui.button("Go to Ask", on_click=lambda: ui.navigate.to("/ask")).classes(
                    "mt-4"
                )
            return

        # Stats
        successful = sum(1 for q in logs if q.ok)
        failed = len(logs) - successful

        with ui.row().classes("gap-4 w-full"):
            with ui.card().classes(
                "flex-1 bg-gradient-to-br from-green-50 to-green-100 border-0 p-4"
            ):
                ui.label(str(successful)).classes("text-3xl font-bold text-green-900")
                ui.label("Successful").classes("text-sm text-green-700")

            with ui.card().classes(
                "flex-1 bg-gradient-to-br from-red-50 to-red-100 border-0 p-4"
            ):
                ui.label(str(failed)).classes("text-3xl font-bold text-red-900")
                ui.label("Failed").classes("text-sm text-red-700")

            with ui.card().classes(
                "flex-1 bg-gradient-to-br from-blue-50 to-blue-100 border-0 p-4"
            ):
                ui.label(str(len(logs))).classes("text-3xl font-bold text-blue-900")
                ui.label("Total").classes("text-sm text-blue-700")

        # Query list
        with ui.column().classes("gap-3 w-full mt-4"):
            for q in logs:
                ds = get_dataset(q.dataset_id)
                status_color = (
                    "bg-green-100 text-green-900" if q.ok else "bg-red-100 text-red-900"
                )
                status_text = "Success" if q.ok else "Failed"

                with ui.card().classes(
                    "w-full bg-white border border-slate-200 hover:border-slate-400 hover:shadow-md transition-all p-4"
                ):
                    with ui.row().classes("w-full items-start justify-between gap-4"):
                        with ui.column().classes("gap-2 flex-1"):
                            with ui.row().classes("items-center gap-2"):
                                ui.badge(status_text).classes(
                                    f"{status_color} text-lg px-2 py-1"
                                )
                                ui.label(q.question or "(no question)").classes(
                                    "font-semibold text-slate-900 flex-1"
                                )

                            with ui.row().classes(
                                "gap-2 items-center text-xs text-slate-600"
                            ):
                                ui.label(f"{ds.name if ds else 'Unknown'}").classes(
                                    "font-mono bg-slate-100 px-2 py-1 rounded"
                                )
                                ui.label(f"{q.created_at[:19]}").classes(
                                    "text-slate-500"
                                )

                            with ui.expansion("SQL", icon="code").classes("w-full"):
                                ui.code(q.sql).classes("w-full text-xs")

                            if q.error:
                                with ui.expansion("Error", icon="error").classes(
                                    "w-full"
                                ):
                                    ui.label(q.error).classes(
                                        "text-xs text-red-700 font-mono"
                                    )
