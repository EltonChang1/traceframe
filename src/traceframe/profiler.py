from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from traceframe.fingerprint import sha256_file


def infer_schema(df: pd.DataFrame) -> dict[str, str]:
    return {column: str(dtype) for column, dtype in df.dtypes.items()}


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "schema": infer_schema(df),
        "missing_values": {column: int(count) for column, count in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
    }


def profile_csv(path: str | Path) -> dict[str, Any]:
    csv_path = Path(path)
    df = pd.read_csv(csv_path)
    profile = profile_dataframe(df)
    profile["path"] = str(csv_path)
    profile["file_hash"] = sha256_file(csv_path)
    return profile

