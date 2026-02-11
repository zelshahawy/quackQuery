from __future__ import annotations

import pandas as pd
import plotly.express as px


def auto_chart(df: pd.DataFrame):
    """
    Minimal heuristic:
    - if >=2 numeric -> scatter
    - if 1 numeric + 1 non-numeric -> bar
    - else: return None
    """
    if df.empty or df.shape[1] < 2:
        return None

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    if len(numeric_cols) >= 2:
        return px.scatter(df, x=numeric_cols[0], y=numeric_cols[1])

    if len(numeric_cols) == 1 and len(non_numeric_cols) >= 1:
        return px.bar(df, x=non_numeric_cols[0], y=numeric_cols[0])

    return None
