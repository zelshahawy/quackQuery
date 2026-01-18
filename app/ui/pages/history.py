from __future__ import annotations

from nicegui import ui
from app.db.meta import list_query_logs, get_dataset


def history_page() -> None:
    ui.label("History").classes("text-2xl font-bold")
    ui.button("Back", on_click=lambda: ui.navigate.to("/")).props("outline")
    ui.separator()

    logs = list_query_logs(limit=100)
    if not logs:
        ui.label("No queries yet.").classes("text-gray-600")
        return

    rows = []
    for q in logs:
        ds = get_dataset(q.dataset_id)
        rows.append(
            {
                "when": q.created_at,
                "dataset": ds.name if ds else q.dataset_id,
                "ok": "yes" if q.ok else "no",
                "question": q.question,
                "sql": q.sql,
                "error": q.error or "",
            }
        )

    ui.table(
        columns=[
            {"name": "when", "label": "When", "field": "when"},
            {"name": "dataset", "label": "Dataset", "field": "dataset"},
            {"name": "ok", "label": "OK", "field": "ok"},
            {"name": "question", "label": "Question", "field": "question"},
            {"name": "sql", "label": "SQL", "field": "sql"},
            {"name": "error", "label": "Error", "field": "error"},
        ],
        rows=rows,
        pagination=10,
    ).classes("w-full")
