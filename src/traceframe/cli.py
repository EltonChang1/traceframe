from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from traceframe.assistant import LOCAL_PRIVACY_NOTICE, plan_analysis
from traceframe.diagnostics import project_health
from traceframe.lineage import LineageDirection, lineage_graph
from traceframe.profiler import profile_csv
from traceframe.project import (
    TraceFrameProjectError,
    get_traceframe_dir,
    init_project,
    load_project,
)
from traceframe.report import export_report
from traceframe.source_rows import drilldown as drilldown_rows
from traceframe.source_rows import export_source_rows
from traceframe.stale import dataset_status, dataset_statuses
from traceframe.storage import read_json

app = typer.Typer(help="Local-first evidence tracking for data science.")


def _exit_with_error(exc: Exception | str) -> None:
    typer.echo(str(exc))
    raise typer.Exit(1)


@app.command()
def init(
    project_name: str = typer.Option(
        "traceframe", help="Project name to store in metadata."
    )
) -> None:
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
        _exit_with_error(exc)

    datasets = read_json(trace_dir / "data_manifest.json", {"datasets": []}).get(
        "datasets", []
    )
    lineage = read_json(trace_dir / "lineage.json", {"nodes": [], "edges": []})
    metrics = read_json(trace_dir / "metrics.json", {"metrics": []}).get("metrics", [])
    charts = read_json(trace_dir / "charts.json", {"charts": []}).get("charts", [])
    claims = read_json(trace_dir / "claims.json", {"claims": []}).get("claims", [])
    checks = read_json(trace_dir / "checks.json", {"checks": []}).get("checks", [])
    plans = read_json(trace_dir / "assistant_plans.json", {"plans": []}).get(
        "plans", []
    )
    reports = list((trace_dir / "reports").glob("*.html"))
    warnings = sum(1 for item in dataset_statuses() if item["status"] != "ok")
    failed_checks = sum(1 for check in checks if not check.get("passed"))

    typer.echo(f"TraceFrame project: {project.get('project_name', 'traceframe')}")
    typer.echo(f"Datasets: {len(datasets)}")
    typer.echo(
        f"Transformations: {sum(1 for node in lineage.get('nodes', []) if node.get('type') == 'transformation')}"
    )
    typer.echo(f"Metrics: {len(metrics)}")
    typer.echo(f"Charts: {len(charts)}")
    typer.echo(f"Claims: {len(claims)}")
    typer.echo(f"Checks: {len(checks)}")
    typer.echo(f"Failed checks: {failed_checks}")
    typer.echo(f"Assistant plans: {len(plans)}")
    typer.echo(f"Reports: {len(reports)}")
    typer.echo(f"Stale warnings: {warnings}")


@app.command("report")
def report_command(
    path: Path = Path(".traceframe/reports/traceframe_report.html"),
) -> None:
    report_path = export_report(path)
    typer.echo(f"Generated report: {report_path}")


@app.command()
def stale() -> None:
    try:
        statuses = dataset_statuses()
    except TraceFrameProjectError as exc:
        _exit_with_error(exc)

    if not statuses:
        typer.echo("No datasets tracked.")
        return
    for status in statuses:
        typer.echo(f"{status['name']}: {status['status']} - {status['message']}")
        if status["status"] != "ok":
            typer.echo(f"  Path: {status['path']}")
            typer.echo(f"  Stored hash: {status['stored_hash']}")
            typer.echo(f"  Current hash: {status['current_hash'] or 'unavailable'}")


@app.command("source-rows")
def source_rows_command(
    artifact_id: str,
    output: Path | None = typer.Option(None, "--output", "-o"),
    limit: int | None = typer.Option(None, "--limit", min=1),
) -> None:
    try:
        output_path = export_source_rows(artifact_id, path=output, limit=limit)
    except (FileNotFoundError, TraceFrameProjectError) as exc:
        _exit_with_error(exc)
    typer.echo(f"Exported source rows: {output_path}")


@app.command()
def drilldown(
    chart_id: str,
    x: str | None = typer.Option(None, "--x", help="Chart x field to filter."),
    value: str | None = typer.Option(
        None, "--value", help="Value to match in the x field."
    ),
    limit: int = typer.Option(20, "--limit", min=1),
) -> None:
    try:
        rows = drilldown_rows(chart_id, x=x, value=value, limit=limit)
    except (FileNotFoundError, TraceFrameProjectError) as exc:
        _exit_with_error(exc)
    typer.echo(rows.to_string(index=False))


@app.command("checks")
def checks_command(failed_only: bool = typer.Option(False, "--failed-only")) -> None:
    try:
        trace_dir = get_traceframe_dir()
    except TraceFrameProjectError as exc:
        _exit_with_error(exc)
    checks = read_json(trace_dir / "checks.json", {"checks": []}).get("checks", [])
    if failed_only:
        checks = [check for check in checks if not check.get("passed")]
    if not checks:
        typer.echo("No checks recorded.")
        return
    for check in checks:
        status = "pass" if check.get("passed") else "fail"
        typer.echo(
            f"{check['name']}: {status} ({check['check_type']}, {check['severity']})"
        )
        if check.get("source"):
            typer.echo(f"  Source: {check['source']}")


def _compact_lineage_graph(graph: dict[str, Any]) -> dict[str, Any]:
    def compact_node(node: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": node.get("id"),
            "name": node.get("name"),
            "type": node.get("type"),
        }

    return {
        "artifact": graph["artifact"],
        "direction": graph["direction"],
        "max_depth": graph["max_depth"],
        "center_ids": graph["center_ids"],
        "nodes": [compact_node(node) for node in graph["nodes"]],
        "upstream": [compact_node(node) for node in graph["upstream"]],
        "downstream": [compact_node(node) for node in graph["downstream"]],
        "edges": graph["edges"],
        "edge_rows": graph["edge_rows"],
    }


@app.command("lineage")
def lineage_command(
    artifact_id: str,
    direction: LineageDirection = typer.Option(
        "both", "--direction", help="Show upstream, downstream, or both."
    ),
    depth: int | None = typer.Option(
        None, "--depth", min=1, help="Limit traversal depth from the artifact."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Print the lineage graph as JSON."
    ),
    include_metadata: bool = typer.Option(
        False, "--include-metadata", help="Include node metadata in JSON output."
    ),
) -> None:
    try:
        graph = lineage_graph(artifact_id, direction=direction, max_depth=depth)
    except KeyError as exc:
        _exit_with_error(exc.args[0] if exc.args else exc)
    except (ValueError, TraceFrameProjectError) as exc:
        _exit_with_error(exc)

    if json_output:
        output_graph = graph if include_metadata else _compact_lineage_graph(graph)
        typer.echo(json.dumps(output_graph, indent=2, sort_keys=True))
        return

    typer.echo(f"Artifact: {artifact_id}")
    typer.echo(f"Direction: {graph['direction']}")
    typer.echo(f"Nodes: {len(graph['nodes'])}")
    for node in graph["nodes"]:
        marker = "*" if node["id"] in graph["center_ids"] else "-"
        typer.echo(f"{marker} {node['name']} [{node['type']}] {node['id']}")

    typer.echo(f"Upstream: {len(graph['upstream'])}")
    for node in graph["upstream"]:
        typer.echo(f"  {node['name']} [{node['type']}] {node['id']}")

    typer.echo(f"Downstream: {len(graph['downstream'])}")
    for node in graph["downstream"]:
        typer.echo(f"  {node['name']} [{node['type']}] {node['id']}")

    typer.echo(f"Edges: {len(graph['edges'])}")
    for edge in graph["edge_rows"]:
        from_label = f"{edge['from_name']} [{edge['from_type']}]"
        to_label = f"{edge['to_name']} [{edge['to_type']}]"
        typer.echo(
            f"  {from_label} {edge['from']} -> {to_label} {edge['to']} ({edge['type']})"
        )


@app.command()
def assist(
    request: str,
    data: list[str] | None = typer.Option(
        None, "--data", help="Local data path to mention."
    ),
    local_llm_command: str | None = typer.Option(
        None,
        "--local-llm-command",
        help="Optional local command to run. No command is used by default.",
    ),
) -> None:
    try:
        plan = plan_analysis(
            request,
            data_paths=data or [],
            local_llm_command=local_llm_command,
        )
    except Exception as exc:
        _exit_with_error(exc)

    typer.echo(LOCAL_PRIVACY_NOTICE)
    typer.echo(f"Plan: {plan['id']} ({plan['mode']})")
    for index, step in enumerate(plan["steps"], start=1):
        typer.echo(f"{index}. {step['title']}")
        typer.echo(step["code"])


@app.command()
def doctor() -> None:
    try:
        health = project_health()
    except TraceFrameProjectError as exc:
        _exit_with_error(exc)

    typer.echo(f"TraceFrame project: {health['project_name']}")
    typer.echo(f"Version: {health['traceframe_version']}")
    typer.echo(f"Status: {health['status']}")
    if not health["issues"]:
        typer.echo("No issues found.")
        return
    for issue in health["issues"]:
        typer.echo(f"{issue['severity']}: {issue['type']} - {issue['message']}")


def _records(trace_dir: Path) -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []
    data.extend(
        read_json(trace_dir / "data_manifest.json", {"datasets": []}).get(
            "datasets", []
        )
    )
    data.extend(
        read_json(trace_dir / "metrics.json", {"metrics": []}).get("metrics", [])
    )
    data.extend(read_json(trace_dir / "charts.json", {"charts": []}).get("charts", []))
    data.extend(read_json(trace_dir / "claims.json", {"claims": []}).get("claims", []))
    data.extend(read_json(trace_dir / "checks.json", {"checks": []}).get("checks", []))
    data.extend(
        read_json(trace_dir / "assistant_plans.json", {"plans": []}).get("plans", [])
    )
    data.extend(read_json(trace_dir / "lineage.json", {"nodes": []}).get("nodes", []))
    return data


@app.command()
def verify(artifact_id: str) -> None:
    try:
        trace_dir = get_traceframe_dir()
    except TraceFrameProjectError as exc:
        _exit_with_error(exc)

    for record in _records(trace_dir):
        if artifact_id in {record.get("id"), record.get("name"), record.get("title")}:
            typer.echo(f"Artifact: {artifact_id}")
            typer.echo(
                f"Type: {record.get('type') or record.get('artifact_type') or _record_type(record)}"
            )
            for key in ["source", "formula", "x", "y", "file_hash", "chart_spec_path"]:
                if record.get(key) is not None:
                    typer.echo(f"{key.replace('_', ' ').title()}: {record[key]}")
            if record.get("source_rows_path"):
                typer.echo(f"Source Rows: {record['source_rows_path']}")
            if record.get("drilldown"):
                typer.echo(
                    f"Drilldown: {record['drilldown']['database_path']}::{record['drilldown']['table']}"
                )
            if record.get("file_hash"):
                status = dataset_status(record)
                typer.echo(f"Stale Status: {status['status']}")
                if status["status"] != "ok":
                    typer.echo(f"Warning: {status['message']}")
            if record.get("run_id"):
                typer.echo(f"Run ID: {record['run_id']}")
            evidence_id = record.get("evidence_id") or record.get("id")
            if evidence_id:
                typer.echo(
                    f"Evidence file: {trace_dir / 'audit_logs' / f'{evidence_id}.json'}"
                )
            return
    _exit_with_error(f"Artifact not found: {artifact_id}")


def _record_type(record: dict[str, Any]) -> str:
    if "formula" in record:
        return "metric"
    if "supports" in record:
        return "claim"
    if "kind" in record:
        return "chart"
    if "check_type" in record:
        return "check"
    if "privacy_notice" in record:
        return "assistant_plan"
    if "file_hash" in record:
        return "dataset"
    return "artifact"
