from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

DISCLOSURE_CLASSES = {
    "AUTHORITATIVE",
    "PROJECT",
    "FROZEN_ARTIFACT",
    "PRIOR_REVIEW_FINAL",
    "PRIOR_CONFIDENCE",
    "PRIOR_VOTE_SIGNAL",
    "MODEL_PRIVATE",
    "PROTECTED_TRUTH",
}


@dataclass(frozen=True)
class DisclosureRecord:
    record_id: str
    disclosure_class: str
    content: str
    provenance: str


def _validate(record: DisclosureRecord) -> None:
    if not record.record_id:
        raise ValueError("record_id required")
    if record.disclosure_class not in DISCLOSURE_CLASSES:
        raise ValueError("invalid disclosure_class")
    if not record.provenance:
        raise ValueError("provenance required")
    if not isinstance(record.content, str):
        raise ValueError("content must be text")


def build_independent_review_context(records: Iterable[DisclosureRecord]) -> tuple[DisclosureRecord, ...]:
    """Return context allowed before the reviewer freezes an independent position."""
    result: list[DisclosureRecord] = []
    seen: set[str] = set()
    for record in records:
        _validate(record)
        if record.record_id in seen:
            raise ValueError("duplicate disclosure record")
        seen.add(record.record_id)
        if record.disclosure_class in {
            "PRIOR_REVIEW_FINAL",
            "PRIOR_CONFIDENCE",
            "PRIOR_VOTE_SIGNAL",
            "MODEL_PRIVATE",
            "PROTECTED_TRUTH",
        }:
            continue
        result.append(record)
    return tuple(result)


def build_adjudication_context(
    records: Iterable[DisclosureRecord],
    *,
    independent_position_hash: str,
) -> tuple[DisclosureRecord, ...]:
    """Allow frozen prior final reviews only after independent position is frozen."""
    if not independent_position_hash:
        raise ValueError("independent_position_hash required before prior review disclosure")

    result: list[DisclosureRecord] = []
    seen: set[str] = set()
    for record in records:
        _validate(record)
        if record.record_id in seen:
            raise ValueError("duplicate disclosure record")
        seen.add(record.record_id)
        if record.disclosure_class in {"MODEL_PRIVATE", "PROTECTED_TRUTH", "PRIOR_CONFIDENCE", "PRIOR_VOTE_SIGNAL"}:
            continue
        result.append(record)
    return tuple(result)
