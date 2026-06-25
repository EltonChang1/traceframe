from __future__ import annotations

from typing import Any, Iterable, Literal

import pandas as pd

from traceframe.evidence import EvidenceRecord, artifact_id, utc_now
from traceframe.project import get_traceframe_dir
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.source_rows import as_pandas_frame
from traceframe.storage import append_record
from traceframe.tracking import object_artifact_id, object_name, write_evidence

Severity = Literal["info", "warning", "error"]


def _columns(columns: str | Iterable[str]) -> list[str]:
    if isinstance(columns, str):
        return [columns]
    return list(columns)


def _record_check(
    name: str,
    check_type: str,
    passed: bool,
    description: str | None = None,
    severity: Severity = "error",
    source: str | None = None,
    source_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    check_id = artifact_id("check", name)
    created_at = utc_now()
    record = {
        "id": check_id,
        "name": name,
        "check_type": check_type,
        "passed": bool(passed),
        "severity": severity,
        "description": description,
        "source": source,
        "source_id": source_id,
        "details": details or {},
        "created_at": created_at,
        "run_id": current_run_id(),
    }
    append_record(get_traceframe_dir() / "checks.json", "checks", record)
    evidence = EvidenceRecord(
        id=check_id,
        artifact_type="check",
        name=name,
        created_at=created_at,
        run_id=current_run_id(),
        source_ids=[source_id] if source_id else [],
        metadata={**record, **evidence_metadata()},
    )
    write_evidence(evidence)
    return record


def expect(
    name: str,
    passed: bool,
    description: str | None = None,
    severity: Severity = "error",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _record_check(
        name=name,
        check_type="expectation",
        passed=passed,
        description=description,
        severity=severity,
        details=metadata,
    )


def expect_not_null(
    data: Any,
    columns: str | Iterable[str],
    name: str | None = None,
    severity: Severity = "error",
) -> dict[str, Any]:
    frame = as_pandas_frame(data)
    selected = _columns(columns)
    missing = {column: int(frame[column].isna().sum()) for column in selected}
    return _record_check(
        name=name or f"not_null_{'_'.join(selected)}",
        check_type="not_null",
        passed=all(count == 0 for count in missing.values()),
        severity=severity,
        source=object_name(data),
        source_id=object_artifact_id(data),
        details={"columns": selected, "missing_values": missing},
    )


def expect_no_duplicates(
    data: Any,
    subset: str | Iterable[str] | None = None,
    name: str | None = None,
    severity: Severity = "error",
) -> dict[str, Any]:
    frame = as_pandas_frame(data)
    selected = _columns(subset) if subset is not None else None
    duplicate_count = int(frame.duplicated(subset=selected).sum())
    return _record_check(
        name=name or "no_duplicate_rows",
        check_type="no_duplicates",
        passed=duplicate_count == 0,
        severity=severity,
        source=object_name(data),
        source_id=object_artifact_id(data),
        details={"subset": selected, "duplicate_count": duplicate_count},
    )


def expect_unique(
    data: Any,
    columns: str | Iterable[str],
    name: str | None = None,
    severity: Severity = "error",
) -> dict[str, Any]:
    frame = as_pandas_frame(data)
    selected = _columns(columns)
    duplicate_count = int(frame.duplicated(subset=selected).sum())
    return _record_check(
        name=name or f"unique_{'_'.join(selected)}",
        check_type="unique",
        passed=duplicate_count == 0,
        severity=severity,
        source=object_name(data),
        source_id=object_artifact_id(data),
        details={"columns": selected, "duplicate_count": duplicate_count},
    )


def expect_schema(
    data: Any,
    schema: dict[str, str],
    name: str | None = None,
    severity: Severity = "error",
) -> dict[str, Any]:
    frame = as_pandas_frame(data)
    actual = {column: str(dtype) for column, dtype in frame.dtypes.items()}
    mismatches = {
        column: {"expected": expected, "actual": actual.get(column)}
        for column, expected in schema.items()
        if actual.get(column) != expected
    }
    return _record_check(
        name=name or "schema_matches",
        check_type="schema",
        passed=not mismatches,
        severity=severity,
        source=object_name(data),
        source_id=object_artifact_id(data),
        details={
            "expected_schema": schema,
            "actual_schema": actual,
            "mismatches": mismatches,
        },
    )


def expect_column_between(
    data: Any,
    column: str,
    min_value: float | None = None,
    max_value: float | None = None,
    name: str | None = None,
    severity: Severity = "error",
) -> dict[str, Any]:
    frame = as_pandas_frame(data)
    series = pd.to_numeric(frame[column], errors="coerce")
    failures = pd.Series(False, index=series.index)
    if min_value is not None:
        failures = failures | (series < min_value)
    if max_value is not None:
        failures = failures | (series > max_value)
    failure_count = int(failures.sum())
    return _record_check(
        name=name or f"{column}_between",
        check_type="threshold",
        passed=failure_count == 0,
        severity=severity,
        source=object_name(data),
        source_id=object_artifact_id(data),
        details={
            "column": column,
            "min_value": min_value,
            "max_value": max_value,
            "failure_count": failure_count,
        },
    )
