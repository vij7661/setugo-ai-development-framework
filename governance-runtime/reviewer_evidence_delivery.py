"""Reviewer evidence-delivery completeness and finding-remediation helpers."""
from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence


ADJUDICATION_STATES = frozenset({
    "ACCEPTED_AS_PROPOSED",
    "ACCEPTED_NARROWED",
    "ACCEPTED_WITH_ALTERNATIVE_SOLUTION",
    "REJECTED_NOT_REPRODUCED",
    "REJECTED_UNSAFE_OR_OUT_OF_SCOPE",
    "DEFERRED_REQUIRES_EVIDENCE",
})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_whole_delivery(*, declared_sha256: str, declared_bytes: int, delivered: bytes) -> bool:
    if not isinstance(declared_sha256, str) or len(declared_sha256) != 64:
        return False
    if not isinstance(declared_bytes, int) or declared_bytes < 0:
        return False
    return len(delivered) == declared_bytes and sha256_bytes(delivered) == declared_sha256


def verify_chunked_delivery(
    *,
    declared_sha256: str,
    declared_bytes: int,
    chunks: Sequence[Mapping[str, Any]],
) -> bool:
    if not isinstance(chunks, Sequence) or isinstance(chunks, (str, bytes, bytearray)):
        return False
    if not chunks:
        return False

    normalized: list[tuple[int, bytes, str]] = []
    declared_count = None
    for row in chunks:
        if not isinstance(row, Mapping):
            return False
        index = row.get("index")
        count = row.get("count")
        data = row.get("bytes")
        digest = row.get("sha256")
        if not isinstance(index, int) or index < 0:
            return False
        if not isinstance(count, int) or count <= 0:
            return False
        if declared_count is None:
            declared_count = count
        if count != declared_count:
            return False
        if not isinstance(data, (bytes, bytearray)):
            return False
        raw = bytes(data)
        if not isinstance(digest, str) or sha256_bytes(raw) != digest:
            return False
        normalized.append((index, raw, digest))

    assert declared_count is not None
    if len(normalized) != declared_count:
        return False
    indexes = [index for index, _, _ in normalized]
    if sorted(indexes) != list(range(declared_count)):
        return False
    if len(set(indexes)) != len(indexes):
        return False

    whole = b"".join(raw for _, raw, _ in sorted(normalized, key=lambda row: row[0]))
    return verify_whole_delivery(
        declared_sha256=declared_sha256,
        declared_bytes=declared_bytes,
        delivered=whole,
    )


def validate_finding_solution_contract(finding: Mapping[str, Any]) -> bool:
    if not isinstance(finding, Mapping):
        return False
    required_text = (
        "finding_id",
        "severity",
        "location",
        "failure_path",
        "evidence",
        "impact",
        "proposed_remediation",
    )
    for field in required_text:
        if not isinstance(finding.get(field), str) or not finding[field].strip():
            return False
    tests = finding.get("regression_tests")
    if not isinstance(tests, list) or not tests or not all(isinstance(x, str) and x.strip() for x in tests):
        return False
    if finding.get("candidate_invalidated") not in {True, False}:
        return False
    if finding.get("blocking") not in {True, False}:
        return False
    return True


def validate_solution_adjudication(record: Mapping[str, Any]) -> bool:
    if not isinstance(record, Mapping):
        return False
    if record.get("state") not in ADJUDICATION_STATES:
        return False
    if not isinstance(record.get("finding_id"), str) or not record["finding_id"].strip():
        return False
    if not isinstance(record.get("reason"), str) or not record["reason"].strip():
        return False
    return True
