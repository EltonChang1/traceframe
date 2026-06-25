from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from traceframe.evidence import artifact_id, utc_now
from traceframe.project import get_traceframe_dir
from traceframe.storage import append_record

_active_run: dict[str, Any] | None = None
_cell_context: dict[str, Any] = {}


def detect_notebook_name() -> str | None:
    for env_name in ["TRACEFRAME_NOTEBOOK_NAME", "JUPYTER_NOTEBOOK_NAME", "IPYNB_PATH"]:
        value = os.environ.get(env_name)
        if value:
            return Path(value).name
    return None


def detect_execution_context(notebook_name: str | None = None) -> dict[str, Any]:
    detected_notebook = notebook_name or detect_notebook_name()
    context = {
        "kind": "script",
        "notebook_name": detected_notebook,
        "script_path": None,
        "execution_count": None,
        "cell_id": _cell_context.get("cell_id"),
        "cell_source_hash": _cell_context.get("source_hash"),
        "cell_tags": _cell_context.get("tags", []),
    }

    main_module = sys.modules.get("__main__")
    script_path = getattr(main_module, "__file__", None)
    if script_path:
        context["script_path"] = str(Path(script_path).resolve())

    try:
        ipython = get_ipython()  # type: ignore[name-defined]
    except NameError:
        ipython = None

    if ipython is not None:
        context["execution_count"] = getattr(ipython, "execution_count", None)
        context["kind"] = "notebook" if detected_notebook else "interactive"
    elif detected_notebook:
        context["kind"] = "notebook"

    return context


def start_run(project_name: str, notebook_name: str | None = None) -> dict[str, Any]:
    global _active_run
    context = detect_execution_context(notebook_name=notebook_name)
    run = {
        "id": artifact_id("run", project_name),
        "project_name": project_name,
        "started_at": utc_now(),
        "context": context,
    }
    append_record(get_traceframe_dir() / "runs.json", "runs", run)
    _active_run = run
    return run


def current_run() -> dict[str, Any] | None:
    return _active_run


def evidence_metadata() -> dict[str, Any]:
    run = current_run()
    if not run:
        return {}
    return {
        "run_id": run["id"],
        "execution_context": run["context"],
    }


def current_run_id() -> str | None:
    run = current_run()
    return run["id"] if run else None


def note_cell(
    cell_id: str | None = None,
    execution_count: int | None = None,
    source_hash: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    _cell_context.clear()
    _cell_context.update(
        {
            "cell_id": cell_id,
            "execution_count": execution_count,
            "source_hash": source_hash,
            "tags": tags or [],
            "recorded_at": utc_now(),
        }
    )
    run = current_run()
    if run:
        _cell_context["run_id"] = run["id"]
        run["context"].update(
            {
                "cell_id": cell_id,
                "execution_count": execution_count,
                "cell_source_hash": source_hash,
                "cell_tags": tags or [],
            }
        )
        append_record(
            get_traceframe_dir() / "cell_events.json", "cells", dict(_cell_context)
        )
    return dict(_cell_context)
