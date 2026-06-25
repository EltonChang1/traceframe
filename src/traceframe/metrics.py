from __future__ import annotations

from traceframe.evidence import EvidenceRecord, artifact_id, utc_now
from traceframe.project import get_traceframe_dir
from traceframe.storage import append_record
from traceframe.tracking import artifact_for_name, write_evidence


def metric(name: str, formula: str, source: str, description: str | None = None) -> dict[str, str | None]:
    metric_id = artifact_id("metric", name)
    record = {
        "id": metric_id,
        "name": name,
        "formula": formula,
        "source": source,
        "description": description,
        "created_at": utc_now(),
    }
    append_record(get_traceframe_dir() / "metrics.json", "metrics", record)
    evidence = EvidenceRecord(
        id=metric_id,
        artifact_type="metric",
        name=name,
        created_at=record["created_at"],
        source_ids=[artifact_for_name(source) or source],
        formula=formula,
        metadata={"description": description, "source": source},
    )
    write_evidence(evidence)
    return record

