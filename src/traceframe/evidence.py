from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

ArtifactType = Literal[
    "dataset", "transformation", "metric", "chart", "claim", "sql_result", "check"
]


class EvidenceRecord(BaseModel):
    id: str
    artifact_type: ArtifactType
    name: str
    created_at: str
    run_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    file_hashes: list[str] = Field(default_factory=list)
    row_count_before: int | None = None
    row_count_after: int | None = None
    columns: list[str] = Field(default_factory=list)
    operation: str | None = None
    formula: str | None = None
    sql: str | None = None
    chart_spec_path: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "_" for char in value.strip())
    return "_".join(part for part in slug.split("_") if part)


def artifact_id(prefix: str, name: str) -> str:
    return f"{prefix}_{slugify(name) or 'artifact'}_{uuid4().hex[:8]}"


def record_to_dict(record: EvidenceRecord) -> dict[str, Any]:
    return record.model_dump()
