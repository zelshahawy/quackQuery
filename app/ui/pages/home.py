from __future__ import annotations

from nicegui import ui
from app.db.meta import list_datasets


def home_page() -> None:
    ui.label("Quick Query").classes("text-3xl font-bold")
    ui.label("Ask your data questions, get safe SQL + charts.").classes("text-gray-600")

    with ui.row().classes("gap-2"):
        ui.button("Data Sources", on_click=lambda: ui.navigate.to("/datasources"))
        ui.button("Ask", on_click=lambda: ui.navigate.to("/ask"))
        ui.button("History", on_click=lambda: ui.navigate.to("/history"))

    ui.separator()

    ds = list_datasets()
    ui.label(f"Datasets ({len(ds)})").classes("text-xl font-semibold mt-2")

    if not ds:
        ui.label("No datasets yet. Upload one in Data Sources.").classes(
            "text-gray-600"
        )
        return

    rows = [
        {
            "name": d.name,
            "table": d.table_name,
            "created_at": d.created_at,
        }
        for d in ds
    ]
    ui.table(
        columns=[
            {"name": "name", "label": "Name", "field": "name"},
            {"name": "table", "label": "DuckDB Table", "field": "table"},
            {"name": "created_at", "label": "Created", "field": "created_at"},
        ],
        rows=rows,
    ).classes("w-full")
