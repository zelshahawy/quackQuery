from __future__ import annotations

import uuid
from nicegui import ui

from app.core.guardrails import SQLGuardrailError, validate_and_rewrite_select
from app.core.text2sql import SchemaInfo, generate_sql
from app.core.viz import auto_chart
from app.db.meta import add_query_log, list_datasets
from app.duck.engine import get_conn
from app.duck.ingest import get_schema


def ask_page() -> None:
    _ = ui.label("Ask").classes("text-2xl font-bold")
    _ = ui.button("Back", on_click=lambda: ui.navigate.to("/")).props("outline")
    _ = ui.separator()

    datasets = list_datasets()
    if not datasets:
        _ = ui.label("No datasets yet. Upload a CSV first in Data Sources.").classes(
            "text-gray-600"
        )
        return

    ds_by_id = {d.id: d for d in datasets}

    ds_select = ui.select(
        options={d.id: f"{d.name} ({d.table_name})" for d in datasets},
        value=datasets[0].id,
        label="Dataset",
    ).classes("w-full")

    question = ui.textarea(
        label="Question (or write: sql: SELECT ...)",
        placeholder="e.g., total rows? top categories? trend over time?",
    ).classes("w-full")

    run_btn = ui.button("Run").classes("mt-2")

    _ = ui.separator()

    sql_box = (
        ui.textarea(label="SQL (generated + guarded)", value="")
        .props("readonly")
        .classes("w-full")
    )
    result_area = ui.column().classes("w-full")
    chart_area = ui.column().classes("w-full")
    status = ui.label("").classes("text-gray-600")

    def run_query() -> None:
        result_area.clear()
        chart_area.clear()
        status.set_text("")

        selected_id = str(ds_select.value)
        d = ds_by_id[selected_id]

        schema_pairs = get_schema(d.table_name)
        schema = SchemaInfo(table_name=d.table_name, columns=schema_pairs)

        raw_sql = generate_sql(question.value or "", schema)

        try:
            safe_sql = validate_and_rewrite_select(raw_sql, max_limit=1000)
        except SQLGuardrailError as e:
            sql_box.value = raw_sql
            status.set_text(f"Blocked by guardrails: {e}")
            add_query_log(
                query_id=uuid.uuid4().hex,
                dataset_id=d.id,
                question=question.value or "",
                sql=raw_sql,
                ok=False,
                error=str(e),
            )
            return

        sql_box.value = safe_sql

        try:
            conn = get_conn()
            try:
                df = conn.execute(safe_sql).df()
            finally:
                conn.close()

            add_query_log(
                query_id=uuid.uuid4().hex,
                dataset_id=d.id,
                question=question.value or "",
                sql=safe_sql,
                ok=True,
                error=None,
            )

            with result_area:
                ui.label(f"Rows: {len(df):,}  Cols: {df.shape[1]}").classes(
                    "font-semibold"
                )
                ui.table(
                    columns=[{"name": c, "label": c, "field": c} for c in df.columns],
                    rows=df.head(200).to_dict(orient="records"),
                    pagination=10,
                ).classes("w-full")

            fig = auto_chart(df)
            if fig is not None:
                with chart_area:
                    ui.label("Chart").classes("text-xl font-semibold mt-2")
                    ui.plotly(fig).classes("w-full")

        except Exception as ex:
            status.set_text(f"Query failed: {ex}")
            add_query_log(
                query_id=uuid.uuid4().hex,
                dataset_id=d.id,
                question=question.value or "",
                sql=safe_sql,
                ok=False,
                error=str(ex),
            )

    run_btn.on_click(run_query)
