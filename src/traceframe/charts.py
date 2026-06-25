from __future__ import annotations

from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import polars as pl

from traceframe.evidence import EvidenceRecord, artifact_id, utc_now
from traceframe.project import get_traceframe_dir
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.source_rows import register_chart_drilldown, sample_dataframe
from traceframe.source_rows import as_pandas_frame
from traceframe.storage import append_record, write_json
from traceframe.tracking import object_artifact_id, object_name, write_evidence


def _mark(chart_obj: alt.Chart, kind: str) -> alt.Chart:
    if kind == "line":
        return chart_obj.mark_line()
    if kind == "bar":
        return chart_obj.mark_bar()
    if kind == "scatter":
        return chart_obj.mark_circle()
    raise ValueError("Unsupported chart kind. Use one of: line, bar, scatter.")


def chart(
    data: pd.DataFrame | pl.DataFrame | pl.LazyFrame,
    x: str,
    y: str,
    kind: str,
    title: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    chart_name = name or title or f"{y}_by_{x}"
    chart_id = artifact_id("chart", chart_name)
    trace_dir = get_traceframe_dir()
    source_name = object_name(data)
    source_id = object_artifact_id(data)
    chart_data = as_pandas_frame(data)

    chart_obj = _mark(alt.Chart(chart_data), kind).encode(x=x, y=y)
    if title:
        chart_obj = chart_obj.properties(title=title)
    spec = chart_obj.to_dict()
    spec_path = trace_dir / "audit_logs" / f"{chart_id}_vegalite.json"
    write_json(spec_path, spec)
    source_rows = sample_dataframe(chart_data, chart_id)
    drilldown = register_chart_drilldown(chart_id, chart_data)

    record = {
        "id": chart_id,
        "title": title or chart_name,
        "name": chart_name,
        "kind": kind,
        "x": x,
        "y": y,
        "source": source_name,
        "source_id": source_id,
        "evidence_id": chart_id,
        "chart_spec_path": str(Path(spec_path)),
        "created_at": utc_now(),
        "run_id": current_run_id(),
        "source_rows_path": source_rows["path"],
        "drilldown": drilldown,
    }
    append_record(trace_dir / "charts.json", "charts", record)
    evidence = EvidenceRecord(
        id=chart_id,
        artifact_type="chart",
        name=chart_name,
        created_at=record["created_at"],
        run_id=current_run_id(),
        source_ids=[source_id] if source_id else [],
        chart_spec_path=str(Path(spec_path)),
        metadata={
            "kind": kind,
            "x": x,
            "y": y,
            "title": title,
            "source": source_name,
            "source_rows": source_rows,
            "drilldown": drilldown,
            **evidence_metadata(),
        },
    )
    write_evidence(evidence)
    return spec
