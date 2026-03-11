from __future__ import annotations

import uuid

from nicegui import ui

from app.core.cache import cache_result, get_cached_result
from app.core.export import export_csv, export_excel, export_json
from app.core.guardrails import SQLGuardrailError, validate_and_rewrite_select
from app.core.semantic_cache import cache_semantic_result, get_similar_cached_result
from app.core.text2sql import SchemaInfo, generate_sql
from app.core.viz import auto_chart
from app.db.meta import add_query_log, list_datasets
from app.duck.engine import get_conn
from app.duck.ingest import get_schema
from app.ui.middleware import check_auth


def ask_page() -> None:
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
            ui.label("Ask Questions").classes("text-3xl font-black tracking-tight")

    with ui.column().classes("w-full max-w-6xl mx-auto px-8 py-8 gap-6"):
        datasets = list_datasets()
        if not datasets:
            with ui.card().classes("w-full bg-amber-50 border border-amber-300 p-6"):
                ui.label("No datasets available").classes(
                    "text-lg font-semibold text-amber-900"
                )
                ui.label("Upload a CSV first in Data Sources").classes(
                    "text-sm text-amber-700 mt-2"
                )
                ui.button(
                    "Go to Data Sources",
                    on_click=lambda: ui.navigate.to("/datasources"),
                ).classes("mt-4")
            return

        ds_by_id = {d.id: d for d in datasets}
        current_df = None

        # Query builder
        with ui.card().classes("w-full bg-white border border-slate-200 p-6"):
            with ui.row().classes("w-full gap-4 items-end"):
                ds_select = (
                    ui.select(
                        options={d.id: f"{d.name}" for d in datasets},
                        value=datasets[0].id,
                        label="Dataset",
                    )
                    .classes("flex-1")
                    .props("outlined")
                )

                run_btn = ui.button("Run Query").classes(
                    "bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6"
                )

            question = (
                ui.textarea(
                    label="Ask a question",
                    placeholder="e.g., What's the average price? Show me top 10 customers by revenue. How many orders per month?",
                    value="",
                )
                .classes("w-full mt-4")
                .props("rows=3")
            )

        # Results section
        with ui.column().classes("w-full gap-4"):
            status = ui.label("").classes("text-sm text-slate-600")

            sql_box = (
                ui.textarea(label="Generated SQL", value="")
                .props("readonly")
                .classes("w-full font-mono text-xs")
            )
            sql_box.visible = False

            # Export buttons
            export_row = ui.row().classes("gap-2 w-full")
            export_row.visible = False
            with export_row:
                ui.button("Download CSV", on_click=lambda: download_csv()).props(
                    "outline"
                ).classes("text-sm")
                ui.button("Download JSON", on_click=lambda: download_json()).props(
                    "outline"
                ).classes("text-sm")
                ui.button("Download Excel", on_click=lambda: download_excel()).props(
                    "outline"
                ).classes("text-sm")

            result_area = ui.column().classes("w-full")
            chart_area = ui.column().classes("w-full")

        def download_csv() -> None:
            if current_df is not None:
                data = export_csv(current_df)
                ui.download(data, "results.csv")

        def download_json() -> None:
            if current_df is not None:
                data = export_json(current_df)
                ui.download(data, "results.json")

        def download_excel() -> None:
            if current_df is not None:
                data = export_excel(current_df)
                ui.download(data, "results.xlsx")

        def show_results(df, sql, cache_source=""):
            nonlocal current_df
            current_df = df

            with result_area:
                with ui.card().classes(
                    "w-full bg-slate-50 border border-slate-200 p-4"
                ):
                    with ui.row().classes("gap-4 items-center"):
                        ui.label(f"{len(df):,} rows").classes(
                            "font-semibold text-slate-900"
                        )
                        ui.label(f"{df.shape[1]} columns").classes(
                            "font-semibold text-slate-900"
                        )
                        if cache_source:
                            ui.badge(cache_source).classes(
                                "bg-green-100 text-green-900 text-xs px-2 py-1"
                            )

                    ui.table(
                        columns=[
                            {"name": c, "label": c, "field": c} for c in df.columns
                        ],
                        rows=df.head(200).to_dict(orient="records"),
                        pagination=10,
                    ).classes("w-full")

            fig = auto_chart(df)
            if fig is not None:
                with chart_area:
                    with ui.card().classes(
                        "w-full bg-white border border-slate-200 p-4"
                    ):
                        ui.label("Visualization").classes(
                            "text-lg font-semibold text-slate-900 mb-4"
                        )
                        ui.plotly(fig).classes("w-full")

            export_row.visible = True

        def run_query() -> None:
            result_area.clear()
            chart_area.clear()
            status.set_text("")
            sql_box.visible = False
            export_row.visible = False

            selected_id = str(ds_select.value)
            d = ds_by_id[selected_id]

            if not question.value.strip():
                status.set_text("Please ask a question")
                return

            # Check cache first
            cached = get_cached_result(question.value, d.table_name)
            if cached:
                status.set_text("Loaded from exact cache")
                sql_box.value = cached["sql"]
                sql_box.visible = True

                import pandas as pd

                df = pd.read_json(cached["df_json"])
                show_results(df, cached["sql"], "Exact Cache")
                return

            # Check semantic cache for similar questions
            status.set_text("Checking semantic cache...")
            similar = get_similar_cached_result(
                question.value, d.table_name, similarity_threshold=0.80
            )
            if similar:
                status.set_text(
                    f"Found similar question (similarity: {similar['similarity']:.0%})"
                )
                sql_box.value = similar["sql"]
                sql_box.visible = True

                import pandas as pd

                df = pd.read_json(similar["df_json"])
                show_results(
                    df, similar["sql"], f"Semantic Cache ({similar['similarity']:.0%})"
                )
                return

            status.set_text("Generating SQL...")

            schema_pairs = get_schema(d.table_name)
            schema = SchemaInfo(table_name=d.table_name, columns=schema_pairs)

            raw_sql = generate_sql(question.value or "", schema)

            try:
                safe_sql = validate_and_rewrite_select(raw_sql, max_limit=1000)
            except SQLGuardrailError as e:
                sql_box.value = raw_sql
                sql_box.visible = True
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
            sql_box.visible = True
            status.set_text("Executing query...")

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

                # Cache the result (both exact and semantic)
                df_json = df.to_json()
                cache_result(question.value, d.table_name, safe_sql, df_json)
                cache_semantic_result(question.value, d.table_name, safe_sql, df_json)

                status.set_text(f"Success: {len(df):,} rows, {df.shape[1]} columns")
                show_results(df, safe_sql, "Fresh Query")

            except Exception as ex:
                status.set_text(f"Query failed: {str(ex)[:100]}")
                add_query_log(
                    query_id=uuid.uuid4().hex,
                    dataset_id=d.id,
                    question=question.value or "",
                    sql=safe_sql,
                    ok=False,
                    error=str(ex),
                )

        run_btn.on_click(run_query)
