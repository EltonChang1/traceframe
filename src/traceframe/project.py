from __future__ import annotations

from pathlib import Path
from typing import Any

from traceframe.evidence import utc_now
from traceframe.storage import read_json, write_json

TRACEFRAME_DIR = ".traceframe"
TRACEFRAME_VERSION = "0.3.0"

DEFAULT_FILES: dict[str, dict[str, Any]] = {
    "data_manifest.json": {"datasets": []},
    "lineage.json": {"nodes": [], "edges": []},
    "metrics.json": {"metrics": []},
    "charts.json": {"charts": []},
    "claims.json": {"claims": []},
    "runs.json": {"runs": []},
    "cell_events.json": {"cells": []},
}

_active_project_root: Path | None = None


class TraceFrameProjectError(RuntimeError):
    pass


def init_project(path: str | Path = ".", project_name: str = "traceframe") -> Path:
    root = Path(path).resolve()
    trace_dir = root / TRACEFRAME_DIR
    trace_dir.mkdir(parents=True, exist_ok=True)
    for dirname in ["runs", "reports", "source_rows", "audit_logs"]:
        (trace_dir / dirname).mkdir(exist_ok=True)

    project_path = trace_dir / "project.json"
    if project_path.exists():
        metadata = read_json(project_path, {})
        metadata["project_name"] = project_name or metadata.get(
            "project_name", "traceframe"
        )
        metadata["traceframe_version"] = TRACEFRAME_VERSION
    else:
        metadata = {
            "project_name": project_name,
            "created_at": utc_now(),
            "traceframe_version": TRACEFRAME_VERSION,
        }
    write_json(project_path, metadata)

    for file_name, default in DEFAULT_FILES.items():
        file_path = trace_dir / file_name
        if not file_path.exists():
            write_json(file_path, default)

    return trace_dir


def start(project_name: str, notebook_name: str | None = None) -> Path:
    from traceframe.runs import start_run

    global _active_project_root
    trace_dir = init_project(".", project_name)
    _active_project_root = trace_dir.parent
    start_run(project_name, notebook_name=notebook_name)
    return trace_dir


def get_project_root(path: str | Path = ".") -> Path:
    global _active_project_root
    if (
        _active_project_root is not None
        and (_active_project_root / TRACEFRAME_DIR).exists()
    ):
        return _active_project_root

    current = Path(path).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / TRACEFRAME_DIR).exists():
            _active_project_root = candidate
            return candidate
    raise TraceFrameProjectError(
        "No .traceframe directory found. Run traceframe init or tf.start(...)."
    )


def get_traceframe_dir(path: str | Path = ".") -> Path:
    return get_project_root(path) / TRACEFRAME_DIR


def load_project(path: str | Path = ".") -> dict[str, Any]:
    return read_json(get_traceframe_dir(path) / "project.json", {})


def write_project_metadata(project_name: str, path: str | Path = ".") -> None:
    trace_dir = get_traceframe_dir(path)
    metadata = read_json(trace_dir / "project.json", {})
    metadata.update(
        {"project_name": project_name, "traceframe_version": TRACEFRAME_VERSION}
    )
    metadata.setdefault("created_at", utc_now())
    write_json(trace_dir / "project.json", metadata)
