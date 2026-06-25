from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from traceframe.project import get_traceframe_dir
from traceframe.storage import read_json, write_json

SOURCE_ROW_LIMIT = 50


def _source_rows_dir() -> Path:
    path = get_traceframe_dir() / "source_rows"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sample_path(artifact_id: str) -> Path:
    return _source_rows_dir() / f"{artifact_id}_sample.json"


def _drilldown_db_path() -> Path:
    return _source_rows_dir() / "chart_drilldown.duckdb"


def _json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def sample_dataframe(
    df: pd.DataFrame, artifact_id: str, limit: int = SOURCE_ROW_LIMIT
) -> dict[str, Any]:
    sample = df.head(limit).copy()
    rows = []
    for index, row in sample.astype(object).to_dict(orient="index").items():
        rows.append(
            {
                "row_index": str(index),
                "values": {key: _json_value(value) for key, value in row.items()},
            }
        )
    payload = {
        "artifact_id": artifact_id,
        "row_count": int(len(df)),
        "sample_size": len(rows),
        "limit": limit,
        "columns": list(df.columns),
        "rows": rows,
    }
    write_json(_sample_path(artifact_id), payload)
    return {"path": str(_sample_path(artifact_id)), **payload}


def find_artifact(artifact_id_or_name: str) -> dict[str, Any] | None:
    trace_dir = get_traceframe_dir()
    collections = [
        ("data_manifest.json", "datasets"),
        ("charts.json", "charts"),
        ("metrics.json", "metrics"),
        ("claims.json", "claims"),
        ("lineage.json", "nodes"),
    ]
    for file_name, key in collections:
        for record in read_json(trace_dir / file_name, {key: []}).get(key, []):
            if artifact_id_or_name in {
                record.get("id"),
                record.get("name"),
                record.get("title"),
                record.get("evidence_id"),
            }:
                return record
    return None


def export_source_rows(
    artifact_id_or_name: str,
    path: str | Path | None = None,
    limit: int | None = None,
) -> Path:
    artifact = find_artifact(artifact_id_or_name)
    artifact_id = artifact.get("id") if artifact else artifact_id_or_name
    source_path = _sample_path(str(artifact_id))
    if not source_path.exists():
        raise FileNotFoundError(
            f"No source-row sample found for {artifact_id_or_name}."
        )

    payload = read_json(source_path, {"rows": []})
    if limit is not None:
        payload["rows"] = payload.get("rows", [])[:limit]
        payload["sample_size"] = len(payload["rows"])

    output_path = (
        Path(path) if path else _source_rows_dir() / f"{artifact_id}_export.json"
    )
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    write_json(output_path, payload)
    return output_path


def _table_name(chart_id: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", chart_id)
    return f"chart_{cleaned}"


def register_chart_drilldown(chart_id: str, data: pd.DataFrame) -> dict[str, str]:
    db_path = _drilldown_db_path()
    table_name = _table_name(chart_id)
    with duckdb.connect(str(db_path)) as conn:
        conn.register("chart_source", data)
        conn.execute(
            f'CREATE OR REPLACE TABLE "{table_name}" AS SELECT * FROM chart_source'
        )
    return {"database_path": str(db_path), "table": table_name}


def drilldown(
    chart_id_or_name: str,
    x: str | None = None,
    value: Any | None = None,
    limit: int = 20,
) -> pd.DataFrame:
    artifact = find_artifact(chart_id_or_name)
    if not artifact or "drilldown" not in artifact:
        raise FileNotFoundError(
            f"No chart drilldown data found for {chart_id_or_name}."
        )

    drilldown_info = artifact["drilldown"]
    table_name = drilldown_info["table"]
    db_path = drilldown_info["database_path"]
    query = f'SELECT * FROM "{table_name}"'
    params: list[Any] = []
    if x is not None and value is not None:
        query += f' WHERE "{x}" = ?'
        params.append(value)
    query += " LIMIT ?"
    params.append(limit)

    with duckdb.connect(db_path, read_only=True) as conn:
        return conn.execute(query, params).fetchdf()
