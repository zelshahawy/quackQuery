from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchemaInfo:
    table_name: str
    columns: list[tuple[str, str]]  # (name, type)


def generate_sql(question: str, schema: SchemaInfo) -> str:
    """
    MVP stub:
    - If the user writes: "sql: <QUERY>" -> use it directly
    - Otherwise: default to a safe preview query
    """
    q = question.strip()
    if q.lower().startswith("sql:"):
        return q[4:].strip()

    # Default: preview data; later you’ll replace this with an LLM call
    return f"SELECT * FROM {schema.table_name} LIMIT 50"
