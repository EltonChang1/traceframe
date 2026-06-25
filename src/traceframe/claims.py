from __future__ import annotations

from typing import Any

from traceframe.evidence import EvidenceRecord, artifact_id, utc_now
from traceframe.project import get_traceframe_dir
from traceframe.runs import current_run_id, evidence_metadata
from traceframe.storage import append_record
from traceframe.tracking import artifact_for_name, write_evidence


def claim(
    text: str, supports: list[str], confidence: str | None = None
) -> dict[str, Any]:
    claim_id = artifact_id("claim", text[:48])
    created_at = utc_now()
    record: dict[str, Any] = {
        "id": claim_id,
        "text": text,
        "supports": supports,
        "confidence": confidence,
        "created_at": created_at,
        "run_id": current_run_id(),
    }
    append_record(get_traceframe_dir() / "claims.json", "claims", record)
    evidence = EvidenceRecord(
        id=claim_id,
        artifact_type="claim",
        name=claim_id,
        created_at=created_at,
        run_id=current_run_id(),
        source_ids=[artifact_for_name(support) or support for support in supports],
        metadata={"text": text, "confidence": confidence, **evidence_metadata()},
    )
    write_evidence(evidence)
    return record
