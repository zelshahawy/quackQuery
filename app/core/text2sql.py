from __future__ import annotations

from dataclasses import dataclass

from google import genai

from app.config import settings


@dataclass(frozen=True)
class SchemaInfo:
    table_name: str
    columns: list[tuple[str, str]]  # (name, type)


def _get_client() -> genai.Client:
    """Get Gemini client with API key from settings."""
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY not set. "
            "Get a free key at https://aistudio.google.com/app/apikeys"
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_sql(question: str, schema: SchemaInfo) -> str:
    """
    Convert natural language question to SQL using Gemini.
    Falls back to safe preview if LLM fails.
    """
    q = question.strip()

    # Allow manual SQL override
    if q.lower().startswith("sql:"):
        return q[4:].strip()

    # If no question, return safe default
    if not q:
        return f"SELECT * FROM {schema.table_name} LIMIT 50"

    try:
        client = _get_client()

        # Build schema description
        schema_desc = "\n".join(f"  - {col}: {typ}" for col, typ in schema.columns)

        prompt = f"""You are a SQL expert. Convert the user's natural language question into a valid DuckDB SQL query.

Table: {schema.table_name}
Columns:
{schema_desc}

Rules:
1. Return ONLY the SQL query, no explanation
2. Use DuckDB syntax
3. The query will be executed read-only, so only SELECT is allowed
4. Do NOT include LIMIT clause (it will be added automatically)
5. If the question is ambiguous, make reasonable assumptions

User question: {q}

Return only the SQL query:"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        sql = response.text.strip()

        # Clean up if model wrapped it in markdown
        if sql.startswith("```"):
            sql = sql.split("```")[1]
            if sql.startswith("sql"):
                sql = sql[3:]
            sql = sql.strip()

        return sql

    except Exception as e:
        # Fallback to safe preview on any error
        print(f"Text-to-SQL error: {e}")
        return f"SELECT * FROM {schema.table_name} LIMIT 50"
