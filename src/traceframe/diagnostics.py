from __future__ import annotations

from pathlib import Path
from typing import Any

from traceframe.project import get_traceframe_dir, load_project
from traceframe.stale import dataset_statuses
from traceframe.storage import read_json


def _evidence_records(trace_dir: Path) -> list[dict[str, Any]]:
    collections = [
        ("data_manifest.json", "datasets"),
        ("metrics.json", "metrics"),
        ("charts.json", "charts"),
        ("claims.json", "claims"),
        ("checks.json", "checks"),
        ("assistant_plans.json", "plans"),
    ]
    records: list[dict[str, Any]] = []
    for file_name, key in collections:
        records.extend(read_json(trace_dir / file_name, {key: []}).get(key, []))
    records.extend(
        read_json(trace_dir / "lineage.json", {"nodes": []}).get("nodes", [])
    )
    return records


def project_health() -> dict[str, Any]:
    trace_dir = get_traceframe_dir()
    project = load_project()
    checks = read_json(trace_dir / "checks.json", {"checks": []}).get("checks", [])
    stale = dataset_statuses()

    issues: list[dict[str, str]] = []
    for status in stale:
        if status["status"] != "ok":
            issues.append(
                {
                    "severity": "warning",
                    "type": "stale_dataset",
                    "message": f"{status['name']}: {status['message']}",
                }
            )
    for check in checks:
        if not check.get("passed"):
            issues.append(
                {
                    "severity": check.get("severity", "error"),
                    "type": "failed_check",
                    "message": f"{check['name']} failed",
                }
            )

    missing_evidence = 0
    for record in _evidence_records(trace_dir):
        evidence_id = record.get("evidence_id") or record.get("id")
        if (
            evidence_id
            and not (trace_dir / "audit_logs" / f"{evidence_id}.json").exists()
        ):
            missing_evidence += 1
    if missing_evidence:
        issues.append(
            {
                "severity": "warning",
                "type": "missing_evidence",
                "message": f"{missing_evidence} artifacts are missing evidence files.",
            }
        )

    return {
        "project_name": project.get("project_name", "traceframe"),
        "traceframe_version": project.get("traceframe_version"),
        "status": "ok" if not issues else "warn",
        "issues": issues,
        "issue_count": len(issues),
    }
