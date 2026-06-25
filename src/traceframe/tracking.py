from __future__ import annotations

from typing import Any

import pandas as pd
import polars as pl

from traceframe.evidence import EvidenceRecord, artifact_id, record_to_dict, utc_now
from traceframe.lineage import add_edge, add_node
from traceframe.profiler import profile_dataframe
from traceframe.project import get_traceframe_dir
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.source_rows import sample_dataframe
from traceframe.storage import read_json, write_json

_tracked_objects: dict[str, Any] = {}
_artifact_ids: dict[str, str] = {}
_object_names: dict[int, str] = {}


def tracked_objects() -> dict[str, Any]:
    return dict(_tracked_objects)


def artifact_for_name(name: str) -> str | None:
    return _artifact_ids.get(name)


def object_name(obj: Any) -> str | None:
    if hasattr(obj, "attrs"):
        return obj.attrs.get("traceframe_name")
    return _object_names.get(id(obj))


def object_artifact_id(obj: Any) -> str | None:
    if hasattr(obj, "attrs"):
        return obj.attrs.get("traceframe_id")
    name = _object_names.get(id(obj))
    return _artifact_ids.get(name) if name else None


def register_object(name: str, obj: Any, artifact_id_value: str) -> None:
    _tracked_objects[name] = obj
    _artifact_ids[name] = artifact_id_value
    _object_names[id(obj)] = name
    if hasattr(obj, "attrs"):
        obj.attrs["traceframe_name"] = name
        obj.attrs["traceframe_id"] = artifact_id_value


def dataframe_metadata(obj: Any) -> dict[str, Any]:
    if isinstance(obj, (pd.DataFrame, pl.DataFrame, pl.LazyFrame)):
        return profile_dataframe(obj)
    columns = list(getattr(obj, "columns", []))
    return {
        "row_count": len(obj) if hasattr(obj, "__len__") else None,
        "column_count": len(columns),
        "schema": {},
        "missing_values": {},
        "duplicate_rows": None,
    }


def _source_rows_metadata(obj: Any, artifact_id_value: str) -> dict[str, Any] | None:
    if isinstance(obj, (pd.DataFrame, pl.DataFrame, pl.LazyFrame)):
        return sample_dataframe(obj, artifact_id_value)
    return None


def write_evidence(record: EvidenceRecord) -> None:
    trace_dir = get_traceframe_dir()
    write_json(trace_dir / "audit_logs" / f"{record.id}.json", record_to_dict(record))


def track(
    obj: Any, name: str, source: str | None = None, operation: str | None = None
) -> Any:
    metadata = dataframe_metadata(obj)
    tracked_id = artifact_id("tf", name)
    source_rows = _source_rows_metadata(obj, tracked_id)
    source_id = artifact_for_name(source) if source else None
    source_ids = [source_id or source] if source else []

    add_node(
        tracked_id, "transformation", name, {**metadata, "source_rows": source_rows}
    )
    if source_id:
        add_edge(source_id, tracked_id)

    record = EvidenceRecord(
        id=tracked_id,
        artifact_type="transformation",
        name=name,
        created_at=utc_now(),
        run_id=current_run_id(),
        source_ids=source_ids,
        row_count_after=metadata.get("row_count"),
        columns=list(metadata.get("schema", {}).keys()),
        operation=operation,
        metadata={
            **metadata,
            "source_rows": source_rows,
            "filter_condition": None,
            **evidence_metadata(),
        },
    )
    write_evidence(record)
    register_object(name, obj, tracked_id)
    return obj


def filter_rows(
    df: pd.DataFrame | pl.DataFrame | pl.LazyFrame,
    condition: str,
    name: str | None = None,
    source: str | None = None,
) -> pd.DataFrame | pl.DataFrame | pl.LazyFrame:
    if isinstance(df, pd.DataFrame):
        filtered = df.query(condition)
    elif isinstance(df, pl.LazyFrame):
        filtered = df.filter(pl.sql_expr(condition))
    else:
        filtered = df.filter(pl.sql_expr(condition))
    source_name = source or object_name(df)
    filter_name = name or f"{source_name or 'data'}_filtered"
    result = track(
        filtered,
        name=filter_name,
        source=source_name,
        operation=f"filter({condition})",
    )

    artifact_id_value = object_artifact_id(result)
    if artifact_id_value:
        trace_dir = get_traceframe_dir()
        evidence_path = trace_dir / "audit_logs" / f"{artifact_id_value}.json"
        evidence = read_json(evidence_path, {})
        evidence.setdefault("metadata", {})["filter_condition"] = condition
        write_json(evidence_path, evidence)
    return result
