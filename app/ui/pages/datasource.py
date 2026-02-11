from __future__ import annotations

import uuid
from pathlib import Path

from nicegui import ui, events

from app.db.meta import add_dataset, list_datasets
from app.duck.ingest import get_schema, register_csv_as_table
from app.storage.files import save_upload_to_disk


def datasource_page() -> None:
    _ = ui.label("Data Sources").classes("text-2xl font-bold")
    _ = ui.button("Back", on_click=lambda: ui.navigate.to("/")).props("outline")

    _ = ui.separator()

    status = ui.label("Upload a CSV to create a dataset.").classes("text-gray-600")

    async def on_upload(e: events.UploadEventArguments) -> None:
        filename: str | None = getattr(e.file, "name", None)
        if not filename:
            status.set_text("Upload failed: missing filename.")
            return

        if not filename.lower().endswith(".csv"):
            status.set_text("Please upload a .csv file.")
            return

        try:
            content: bytes = await e.file.read()
            file_path: Path = save_upload_to_disk(filename, content)

            dataset_id = uuid.uuid4().hex
            table_name = f"t_{dataset_id[:10]}"

            register_csv_as_table(csv_path=file_path, table_name=table_name)

            add_dataset(
                dataset_id=dataset_id,
                name=filename,
                table_name=table_name,
                file_path=str(file_path),
            )

            status.set_text(f"Uploaded: {filename} → DuckDB table: {table_name}")

        except Exception as ex:
            status.set_text(f"Upload failed: {ex}")

    _ = ui.upload(on_upload=on_upload, auto_upload=True).props("accept=.csv")

    _ = ui.separator()
    _ = ui.label("Existing datasets").classes("text-xl font-semibold mt-2")

    ds = list_datasets()
    if not ds:
        _ = ui.label("No datasets yet.").classes("text-gray-600")
        return

    with ui.column().classes("w-full"):
        for d in ds[:10]:
            with ui.card().classes("w-full"):
                _ = ui.label(d.name).classes("font-semibold")
                _ = ui.label(f"Table: {d.table_name}").classes("text-sm text-gray-600")

                schema = get_schema(d.table_name)
                _ = ui.label("Schema (first 10 cols):").classes("text-sm mt-2")
                _ = ui.table(
                    columns=[
                        {"name": "col", "label": "Column", "field": "col"},
                        {"name": "typ", "label": "Type", "field": "typ"},
                    ],
                    rows=[{"col": c, "typ": t} for (c, t) in schema[:10]],
                ).classes("w-full")
