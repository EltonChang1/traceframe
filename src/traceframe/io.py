from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeAlias

import pandas as pd
import polars as pl

from traceframe.evidence import EvidenceRecord, artifact_id, record_to_dict, utc_now
from traceframe.fingerprint import sha256_file
from traceframe.lineage import add_node
from traceframe.profiler import profile_dataframe
from traceframe.project import get_traceframe_dir
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.source_rows import sample_dataframe
from traceframe.storage import append_record, write_json
from traceframe.tracking import register_object


def _dataset_name(path: str | Path, name: str | None) -> str:
    return name or Path(path).stem


TableLike: TypeAlias = pd.DataFrame | pl.DataFrame | pl.LazyFrame


def _register_dataset(df: TableLike, path: str | Path, name: str) -> None:
    trace_dir = get_traceframe_dir()
    dataset_id = artifact_id("ds", name)
    file_hash = sha256_file(path)
    profile = profile_dataframe(df)
    source_rows = sample_dataframe(df, dataset_id)
    record = {
        "id": dataset_id,
        "name": name,
        "path": str(path),
        "file_hash": file_hash,
        "row_count": profile["row_count"],
        "column_count": profile["column_count"],
        "schema": profile["schema"],
        "missing_values": profile["missing_values"],
        "duplicate_rows": profile["duplicate_rows"],
        "created_at": utc_now(),
        "run_id": current_run_id(),
        "source_rows_path": source_rows["path"],
        "source_rows_sample_size": source_rows["sample_size"],
    }
    append_record(trace_dir / "data_manifest.json", "datasets", record)
    add_node(dataset_id, "dataset", name, {**profile, "source_rows": source_rows})
    evidence = EvidenceRecord(
        id=dataset_id,
        artifact_type="dataset",
        name=name,
        created_at=record["created_at"],
        run_id=current_run_id(),
        file_hashes=[file_hash],
        row_count_after=profile["row_count"],
        columns=list(profile["schema"].keys()),
        metadata={
            "path": str(path),
            "source_rows": source_rows,
            **profile,
            **evidence_metadata(),
        },
    )
    write_json(
        trace_dir / "audit_logs" / f"{dataset_id}.json", record_to_dict(evidence)
    )
    register_object(name, df, dataset_id)


def read_csv(
    path: str | Path,
    name: str | None = None,
    engine: Literal["pandas", "polars"] = "pandas",
    lazy: bool = False,
) -> TableLike:
    if engine == "polars":
        df = pl.scan_csv(path) if lazy else pl.read_csv(path)
    else:
        if lazy:
            raise ValueError("lazy=True is only supported with engine='polars'.")
        df = pd.read_csv(path)
    _register_dataset(df, path, _dataset_name(path, name))
    return df


def read_parquet(
    path: str | Path,
    name: str | None = None,
    engine: Literal["pandas", "polars"] = "pandas",
    lazy: bool = False,
) -> TableLike:
    if engine == "polars":
        df = pl.scan_parquet(path) if lazy else pl.read_parquet(path)
    else:
        if lazy:
            raise ValueError("lazy=True is only supported with engine='polars'.")
        df = pd.read_parquet(path)
    _register_dataset(df, path, _dataset_name(path, name))
    return df


def scan_csv(path: str | Path, name: str | None = None) -> pl.LazyFrame:
    result = read_csv(path, name=name, engine="polars", lazy=True)
    if not isinstance(result, pl.LazyFrame):
        raise TypeError("Expected a Polars LazyFrame from scan_csv.")
    return result


def scan_parquet(path: str | Path, name: str | None = None) -> pl.LazyFrame:
    result = read_parquet(path, name=name, engine="polars", lazy=True)
    if not isinstance(result, pl.LazyFrame):
        raise TypeError("Expected a Polars LazyFrame from scan_parquet.")
    return result
