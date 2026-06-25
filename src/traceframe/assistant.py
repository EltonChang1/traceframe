from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from traceframe.evidence import EvidenceRecord, artifact_id, utc_now
from traceframe.project import TraceFrameProjectError, get_traceframe_dir
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.storage import append_record
from traceframe.tracking import write_evidence

LOCAL_PRIVACY_NOTICE = (
    "TraceFrame assistant planning is local-first. No external API calls are made "
    "unless you explicitly run your own local command."
)


def _heuristic_steps(request: str, data_paths: list[str]) -> list[dict[str, str]]:
    lowered = request.lower()
    steps: list[dict[str, str]] = []
    if data_paths:
        for path in data_paths:
            name = Path(path).stem
            reader = "read_parquet" if path.endswith(".parquet") else "read_csv"
            steps.append(
                {
                    "title": f"Track {path}",
                    "code": f'{name} = tf.{reader}("{path}", name="{name}")',
                }
            )
    else:
        steps.append(
            {
                "title": "Start a TraceFrame project",
                "code": 'tf.start("analysis")',
            }
        )

    if any(word in lowered for word in ["clean", "filter", "exclude", "remove"]):
        steps.append(
            {
                "title": "Track a named filter",
                "code": 'clean = tf.filter_rows(data, "status != \'cancelled\'", name="clean_data")',
            }
        )
    if any(
        word in lowered
        for word in ["quality", "null", "duplicate", "validate", "check"]
    ):
        steps.append(
            {
                "title": "Record data quality checks",
                "code": 'tf.expect_not_null(data, ["id"])\ntf.expect_no_duplicates(data)',
            }
        )
    if any(word in lowered for word in ["metric", "revenue", "sum", "count", "rate"]):
        steps.append(
            {
                "title": "Register metric definitions",
                "code": 'tf.metric("revenue", "SUM(total_price)", source="clean_data")',
            }
        )
    if any(word in lowered for word in ["sql", "group", "monthly", "aggregate"]):
        steps.append(
            {
                "title": "Create a traced SQL result",
                "code": 'monthly = tf.sql("SELECT month, SUM(total_price) AS revenue FROM clean_data GROUP BY 1", name="monthly_revenue")',
            }
        )
    if any(word in lowered for word in ["chart", "plot", "trend", "visual"]):
        steps.append(
            {
                "title": "Create chart evidence",
                "code": 'tf.chart(monthly, x="month", y="revenue", kind="line", name="monthly_revenue_chart")',
            }
        )
    if any(word in lowered for word in ["claim", "conclusion", "explain"]):
        steps.append(
            {
                "title": "Link a conclusion to evidence",
                "code": 'tf.claim("Conclusion text", supports=["monthly_revenue"], confidence="medium")',
            }
        )
    steps.append(
        {
            "title": "Export the local audit report",
            "code": 'tf.export_report("traceframe_report.html")',
        }
    )
    return steps


def _local_llm_steps(
    command: str, request: str, data_paths: list[str]
) -> list[dict[str, str]]:
    prompt = (
        f"{LOCAL_PRIVACY_NOTICE}\n"
        "Return concise TraceFrame Python steps for this local analysis request.\n"
        f"Request: {request}\n"
        f"Data paths: {', '.join(data_paths) if data_paths else 'none'}\n"
    )
    completed = subprocess.run(
        shlex.split(command),
        input=prompt,
        text=True,
        capture_output=True,
        check=True,
        timeout=60,
    )
    output = completed.stdout.strip()
    return [{"title": "Local LLM suggestion", "code": output}]


def plan_analysis(
    request: str,
    data_paths: list[str] | None = None,
    local_llm_command: str | None = None,
    store: bool = True,
) -> dict[str, Any]:
    paths = data_paths or []
    plan_id = artifact_id("assist", request[:48])
    created_at = utc_now()
    mode = "local_llm" if local_llm_command else "heuristic"
    steps = (
        _local_llm_steps(local_llm_command, request, paths)
        if local_llm_command
        else _heuristic_steps(request, paths)
    )
    plan: dict[str, Any] = {
        "id": plan_id,
        "request": request,
        "mode": mode,
        "data_paths": paths,
        "steps": steps,
        "privacy_notice": LOCAL_PRIVACY_NOTICE,
        "created_at": created_at,
        "run_id": current_run_id(),
    }
    if store:
        try:
            append_record(get_traceframe_dir() / "assistant_plans.json", "plans", plan)
            evidence = EvidenceRecord(
                id=plan_id,
                artifact_type="assistant_plan",
                name=plan_id,
                created_at=created_at,
                run_id=current_run_id(),
                metadata={**plan, **evidence_metadata()},
            )
            write_evidence(evidence)
        except TraceFrameProjectError:
            plan["stored"] = False
            return plan
    plan["stored"] = store
    return plan
