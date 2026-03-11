from __future__ import annotations

from io import BytesIO

import pandas as pd


def export_csv(df: pd.DataFrame) -> bytes:
    """Export dataframe as CSV bytes."""
    return df.to_csv(index=False).encode()


def export_json(df: pd.DataFrame) -> bytes:
    """Export dataframe as JSON bytes."""
    return df.to_json(orient="records", indent=2).encode()


def export_excel(df: pd.DataFrame) -> bytes:
    """Export dataframe as Excel bytes."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")
    return buffer.getvalue()
