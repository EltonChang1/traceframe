from __future__ import annotations

import re

import duckdb
import pandas as pd

from traceframe.evidence import EvidenceRecord, artifact_id, utc_now
from traceframe.lineage import add_edge, add_node
from traceframe.profiler import profile_dataframe
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.tracking import (
    artifact_for_name,
    register_object,
    tracked_objects,
    write_evidence,
)

_connection: duckdb.DuckDBPyConnection | None = None


def get_connection() -> duckdb.DuckDBPyConnection:
    global _connection
    if _connection is None:
        _connection = duckdb.connect(database=":memory:")
    return _connection


def register_table(name: str, df: pd.DataFrame) -> None:
    get_connection().register(name, df)


def _query_sources(query: str) -> list[str]:
    names = re.findall(
        r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", query, flags=re.IGNORECASE
    )
    return list(dict.fromkeys(names))


def sql(query: str, name: str) -> pd.DataFrame:
    conn = get_connection()
    for table_name, obj in tracked_objects().items():
        if isinstance(obj, pd.DataFrame):
            conn.register(table_name, obj)

    result = conn.execute(query).fetchdf()
    result_id = artifact_id("sql", name)
    profile = profile_dataframe(result)
    add_node(result_id, "sql_result", name, profile)

    source_ids: list[str] = []
    for source_name in _query_sources(query):
        source_id = artifact_for_name(source_name)
        if source_id:
            source_ids.append(source_id)
            add_edge(source_id, result_id)

    record = EvidenceRecord(
        id=result_id,
        artifact_type="sql_result",
        name=name,
        created_at=utc_now(),
        run_id=current_run_id(),
        source_ids=source_ids,
        row_count_after=profile["row_count"],
        columns=list(profile["schema"].keys()),
        sql=query,
        metadata={**profile, **evidence_metadata()},
    )
    write_evidence(record)
    register_object(name, result, result_id)
    return result
