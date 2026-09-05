from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

MEMORY_CLASSES = {
    "AUTHORITATIVE",
    "PROJECT",
    "WORKING",
    "REVIEW_EVIDENCE",
    "MODEL_PRIVATE",
    "PROTECTED_TRUTH",
}


@dataclass(frozen=True)
class MemoryRecord:
    record_id: str
    memory_class: str
    version: int
    provenance: str
    content: str
    relevant: bool = True
    source_role: str | None = None


def validate_record(record: MemoryRecord) -> None:
    if not record.record_id:
        raise ValueError("memory record_id required")
    if record.memory_class not in MEMORY_CLASSES:
        raise ValueError("invalid memory_class")
    if not isinstance(record.version, int) or record.version < 1:
        raise ValueError("memory version must be positive integer")
    if not record.provenance:
        raise ValueError("memory provenance required")
    if not isinstance(record.content, str):
        raise ValueError("memory content must be text")


def build_reviewer_context(
    records: Iterable[MemoryRecord],
    *,
    reviewer_stage: str,
    allow_prior_review_evidence: bool = False,
    authoritative_version: int | None = None,
) -> tuple[MemoryRecord, ...]:
    if reviewer_stage not in {"R1", "R2", "R3"}:
        raise ValueError("invalid reviewer_stage")

    result: list[MemoryRecord] = []
    seen_ids: set[str] = set()
    for record in records:
        validate_record(record)
        if record.record_id in seen_ids:
            raise ValueError("duplicate memory record_id")
        seen_ids.add(record.record_id)

        if record.memory_class in {"MODEL_PRIVATE", "PROTECTED_TRUTH"}:
            raise ValueError(f"forbidden reviewer memory class: {record.memory_class}")

        if authoritative_version is not None and record.memory_class in {"AUTHORITATIVE", "WORKING"}:
            if record.version != authoritative_version:
                raise ValueError("stale memory version relative to authoritative context")

        if not record.relevant:
            continue

        if record.memory_class == "REVIEW_EVIDENCE":
            if reviewer_stage == "R1":
                continue
            if not allow_prior_review_evidence:
                continue

        result.append(record)

    return tuple(result)


def apply_memory_write(
    current_authoritative: dict[str, MemoryRecord],
    proposed: MemoryRecord,
    *,
    external_authority: bool,
) -> dict[str, MemoryRecord]:
    validate_record(proposed)
    if proposed.memory_class == "AUTHORITATIVE" and not external_authority:
        raise PermissionError("model-generated memory cannot overwrite authoritative memory")
    updated = dict(current_authoritative)
    if proposed.record_id in updated and proposed.version <= updated[proposed.record_id].version:
        raise ValueError("memory write must advance version")
    updated[proposed.record_id] = proposed
    return updated
