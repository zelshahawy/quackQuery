from __future__ import annotations

import uuid
from pathlib import Path

from nicegui import events, ui

from app.core.schema_embeddings import index_schema
from app.db.meta import add_dataset, list_datasets
from app.duck.ingest import get_schema, register_csv_as_table
from app.storage.files import save_upload_to_disk
from app.ui.middleware import check_auth


def datasource_page() -> None:
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
            ui.label("Data Sources").classes("text-3xl font-black tracking-tight")

    with ui.column().classes("w-full max-w-4xl mx-auto px-8 py-8 gap-8"):
        # Upload section
        with ui.card().classes(
            "w-full bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-dashed border-blue-300 p-8"
        ):
            ui.label("Upload CSV").classes("text-xl font-bold text-blue-900")
            ui.label("Drag and drop or click to select").classes(
                "text-sm text-blue-700 mt-2"
            )

            status = ui.label("").classes("text-sm text-blue-600 mt-4 font-semibold")

            async def on_upload(e: events.UploadEventArguments) -> None:
                filename: str | None = getattr(e.file, "name", None)
                if not filename:
                    status.set_text("Upload failed: missing filename")
                    return

                if not filename.lower().endswith(".csv"):
                    status.set_text("Please upload a .csv file")
                    return

                try:
                    status.set_text("Uploading...")
                    content: bytes = await e.file.read()
                    file_path: Path = save_upload_to_disk(filename, content)

                    dataset_id = uuid.uuid4().hex
                    table_name = f"t_{dataset_id[:10]}"

                    status.set_text("Processing...")
                    register_csv_as_table(csv_path=file_path, table_name=table_name)

                    # Get schema and index it for semantic search
                    schema = get_schema(table_name)
                    index_schema(table_name, schema)

                    add_dataset(
                        dataset_id=dataset_id,
                        name=filename,
                        table_name=table_name,
                        file_path=str(file_path),
                    )

                    status.set_text(f"Uploaded: {filename}")
                    ui.timer(2, lambda: ui.navigate.to("/"))

                except Exception as ex:
                    status.set_text(f"Error: {str(ex)[:60]}")

            _ = (
                ui.upload(on_upload=on_upload, auto_upload=True)
                .props("accept=.csv")
                .classes("w-full")
            )

        # Existing datasets
        ds = list_datasets()

        with ui.column().classes("gap-4"):
            with ui.row().classes("items-center gap-2"):
                ui.label("Your Datasets").classes("text-2xl font-bold text-slate-900")
                if ds:
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
            else:
                with ui.column().classes("gap-3 w-full"):
                    for d in ds:
                        with ui.card().classes(
                            "w-full bg-white border border-slate-200 hover:border-slate-400 hover:shadow-md transition-all"
                        ):
                            with ui.row().classes("w-full items-start justify-between"):
                                with ui.column().classes("gap-3 flex-1"):
                                    ui.label(d.name).classes(
                                        "font-semibold text-slate-900 text-lg"
                                    )
                                    ui.label(f"Table: {d.table_name}").classes(
                                        "text-xs font-mono bg-slate-100 text-slate-700 px-2 py-1 rounded w-fit"
                                    )

                                    schema = get_schema(d.table_name)
                                    ui.label(f"Columns: {len(schema)}").classes(
                                        "text-xs text-slate-600"
                                    )

                                    with ui.row().classes("gap-2 flex-wrap"):
                                        for col, typ in schema[:5]:
                                            ui.chip(f"{col}: {typ}").classes(
                                                "text-xs bg-slate-100 text-slate-700"
                                            )
                                        if len(schema) > 5:
                                            ui.chip(f"+{len(schema) - 5} more").classes(
                                                "text-xs bg-slate-100 text-slate-700"
                                            )

                                ui.button(
                                    "Query", on_click=lambda: ui.navigate.to("/ask")
                                ).props("flat").classes(
                                    "text-blue-600 hover:text-blue-800"
                                )
