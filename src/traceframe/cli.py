from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from traceframe.profiler import profile_csv
from traceframe.project import TraceFrameProjectError, get_traceframe_dir, init_project, load_project
from traceframe.report import export_report
from traceframe.storage import read_json

app = typer.Typer(help="Local-first evidence tracking for data science.")


@app.command()
def init(project_name: str = typer.Option("traceframe", help="Project name to store in metadata.")) -> None:
    init_project(".", project_name)
    typer.echo("Initialized TraceFrame project in .traceframe/")


@app.command()
def profile(path: Path) -> None:
    info = profile_csv(path)
    missing_columns = sum(1 for count in info["missing_values"].values() if count > 0)
    typer.echo(f"File: {path}")
    typer.echo(f"Rows: {info['row_count']}")
    typer.echo(f"Columns: {info['column_count']}")
    typer.echo(f"Hash: {info['file_hash']}")
    typer.echo(f"Missing values: {missing_columns} columns contain missing values")
    typer.echo(f"Duplicate rows: {info['duplicate_rows']} possible duplicates")


@app.command()
def status() -> None:
    try:
        trace_dir = get_traceframe_dir()
        project = load_project()
    except TraceFrameProjectError as exc:
        raise typer.Exit(str(exc))

    datasets = read_json(trace_dir / "data_manifest.json", {"datasets": []}).get("datasets", [])
    lineage = read_json(trace_dir / "lineage.json", {"nodes": [], "edges": []})
    metrics = read_json(trace_dir / "metrics.json", {"metrics": []}).get("metrics", [])
    charts = read_json(trace_dir / "charts.json", {"charts": []}).get("charts", [])
    claims = read_json(trace_dir / "claims.json", {"claims": []}).get("claims", [])
    reports = list((trace_dir / "reports").glob("*.html"))

    typer.echo(f"TraceFrame project: {project.get('project_name', 'traceframe')}")
    typer.echo(f"Datasets: {len(datasets)}")
    typer.echo(f"Transformations: {sum(1 for node in lineage.get('nodes', []) if node.get('type') == 'transformation')}")
    typer.echo(f"Metrics: {len(metrics)}")
    typer.echo(f"Charts: {len(charts)}")
    typer.echo(f"Claims: {len(claims)}")
    typer.echo(f"Reports: {len(reports)}")


@app.command("report")
def report_command(path: Path = Path(".traceframe/reports/traceframe_report.html")) -> None:
    report_path = export_report(path)
    typer.echo(f"Generated report: {report_path}")


def _records(trace_dir: Path) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    data.extend(read_json(trace_dir / "data_manifest.json", {"datasets": []}).get("datasets", []))
    data.extend(read_json(trace_dir / "metrics.json", {"metrics": []}).get("metrics", []))
    data.extend(read_json(trace_dir / "charts.json", {"charts": []}).get("charts", []))
    data.extend(read_json(trace_dir / "claims.json", {"claims": []}).get("claims", []))
    data.extend(read_json(trace_dir / "lineage.json", {"nodes": []}).get("nodes", []))
    return data


@app.command()
def verify(artifact_id: str) -> None:
    try:
        trace_dir = get_traceframe_dir()
    except TraceFrameProjectError as exc:
        raise typer.Exit(str(exc))

    for record in _records(trace_dir):
        if artifact_id in {record.get("id"), record.get("name"), record.get("title")}:
            typer.echo(f"Artifact: {artifact_id}")
            typer.echo(f"Type: {record.get('type') or record.get('artifact_type') or _record_type(record)}")
            for key in ["source", "formula", "x", "y", "file_hash", "chart_spec_path"]:
                if record.get(key) is not None:
                    typer.echo(f"{key.replace('_', ' ').title()}: {record[key]}")
            evidence_id = record.get("evidence_id") or record.get("id")
            if evidence_id:
                typer.echo(f"Evidence file: {trace_dir / 'audit_logs' / f'{evidence_id}.json'}")
            return
    raise typer.Exit(f"Artifact not found: {artifact_id}")


def _record_type(record: dict[str, Any]) -> str:
    if "formula" in record:
        return "metric"
    if "supports" in record:
        return "claim"
    if "kind" in record:
        return "chart"
    if "file_hash" in record:
        return "dataset"
    return "artifact"

