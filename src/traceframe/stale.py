from __future__ import annotations

from pathlib import Path
from typing import Any

from traceframe.fingerprint import sha256_file
from traceframe.project import get_project_root, get_traceframe_dir
from traceframe.storage import read_json


def dataset_status(
    dataset: dict[str, Any], project_root: Path | None = None
) -> dict[str, Any]:
    root = project_root or get_project_root()
    stored_path = Path(dataset.get("path", ""))
    data_path = stored_path if stored_path.is_absolute() else root / stored_path
    result = {
        "id": dataset.get("id"),
        "name": dataset.get("name"),
        "path": str(stored_path),
        "status": "ok",
        "stored_hash": dataset.get("file_hash"),
        "current_hash": None,
        "message": "Current file matches tracked hash.",
    }
    if not data_path.exists():
        result["status"] = "missing"
        result["message"] = "Tracked source file is missing."
        return result

    current_hash = sha256_file(data_path)
    result["current_hash"] = current_hash
    if current_hash != dataset.get("file_hash"):
        result["status"] = "stale"
        result["message"] = "Tracked source file has changed since it was recorded."
    return result


def dataset_statuses() -> list[dict[str, Any]]:
    trace_dir = get_traceframe_dir()
    root = get_project_root()
    datasets = read_json(trace_dir / "data_manifest.json", {"datasets": []}).get(
        "datasets", []
    )
    return [dataset_status(dataset, project_root=root) for dataset in datasets]


def stale_datasets() -> list[dict[str, Any]]:
    return [status for status in dataset_statuses() if status["status"] != "ok"]
