from __future__ import annotations

import sqlglot
from sqlglot import exp


class SQLGuardrailError(ValueError):
    pass


def validate_and_rewrite_select(sql: str, *, max_limit: int = 1000) -> str:
    """
    Enforce:
      - exactly one statement
      - statement is SELECT (or WITH ... SELECT)
      - apply LIMIT if absent
      - cap LIMIT to max_limit
    """
    try:
        parsed = sqlglot.parse(sql, read="duckdb")
    except Exception as e:
        raise SQLGuardrailError(f"SQL parse error: {e}") from e

    if len(parsed) != 1:
        raise SQLGuardrailError("Only one SQL statement is allowed.")

    stmt = parsed[0]

    if isinstance(stmt, exp.With):
        final = stmt.this
        if not isinstance(final, exp.Select):
            raise SQLGuardrailError(
                "Only SELECT queries are allowed (WITH must end in SELECT)."
            )
    elif not isinstance(stmt, exp.Select):
        raise SQLGuardrailError("Only SELECT queries are allowed.")

    limit_expr = stmt.args.get("limit")
    if limit_expr is None:
        stmt.set("limit", exp.Limit(this=exp.Literal.number(min(200, max_limit))))
    else:
        lit = limit_expr.this
        if isinstance(lit, exp.Literal) and lit.is_int:
            n = int(lit.this)
            if n > max_limit:
                limit_expr.set("this", exp.Literal.number(max_limit))

    return stmt.sql(dialect="duckdb")
