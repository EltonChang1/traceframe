from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import polars as pl

from traceframe.fingerprint import sha256_file


def infer_schema(df: pd.DataFrame | pl.DataFrame | pl.LazyFrame) -> dict[str, str]:
    if isinstance(df, pd.DataFrame):
        return {column: str(dtype) for column, dtype in df.dtypes.items()}
    if isinstance(df, pl.LazyFrame):
        return {column: str(dtype) for column, dtype in df.collect_schema().items()}
    return {column: str(dtype) for column, dtype in df.schema.items()}


def profile_dataframe(df: pd.DataFrame | pl.DataFrame | pl.LazyFrame) -> dict[str, Any]:
    if isinstance(df, pl.LazyFrame):
        schema = infer_schema(df)
        return {
            "row_count": None,
            "column_count": len(schema),
            "schema": schema,
            "missing_values": {},
            "duplicate_rows": None,
            "engine": "polars_lazy",
        }
    if isinstance(df, pl.DataFrame):
        missing = df.null_count().to_dicts()[0] if df.width else {}
        return {
            "row_count": int(df.height),
            "column_count": int(df.width),
            "schema": infer_schema(df),
            "missing_values": {column: int(count) for column, count in missing.items()},
            "duplicate_rows": int(df.is_duplicated().sum()),
            "engine": "polars",
        }
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "schema": infer_schema(df),
        "missing_values": {
            column: int(count) for column, count in df.isna().sum().items()
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "engine": "pandas",
    }


def profile_csv(path: str | Path) -> dict[str, Any]:
    csv_path = Path(path)
    df = pd.read_csv(csv_path)
    profile = profile_dataframe(df)
    profile["path"] = str(csv_path)
    profile["file_hash"] = sha256_file(csv_path)
    return profile
