"""Fail-closed entry preflight for V24-I11-V6 Runtime Qualification 1.

This module validates whether an exact runtime has enough bound evidence to
begin falsification.  It cannot qualify a runtime, open scientific execution,
or create authority.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

PHASE_ID = "V24-I11-V6-RUNTIME-QUALIFICATION-1"
PHASE_BRANCH = "qualification/v24-i11-v6-runtime-qualification-1"
CONSTRUCTION_COMMIT = "c6304d0f14914c3b1e9f30a8a42ac231f152fa8f"
CONSTRUCTION_TREE = "dc55289eff2294dbc172e41b045ec80b05d61299"
SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"
AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
EXPECTED_CASE_IDS = tuple(f"RQ-{i:02d}" for i in range(1, 33))

RUNTIME_REQUIRED_FIELDS = (
    "host_or_image_id",
    "image_digest",
    "os_release",
    "kernel_release",
    "architecture",
    "service_manager",
    "filesystem_type",
    "mount_options_digest",
    "runtime_owner",
    "evidence_custodian",
    "independent_reviewer",
    "candidate_uid",
    "trusted_uid",
    "record_fs_device",
    "consumed_fs_device",
    "trusted_path_owner_uid",
    "socket_parent_owner_uid",
    "unprivileged_userns_blocked",
    "ptrace_candidate_to_service_denied",
    "synthetic_sinks_only",
)


def _is_hex(value: Any, length: int) -> bool:
    if not isinstance(value, str) or len(value) != length:
        return False
    return all(c in "0123456789abcdef" for c in value)


def validate_runtime_qualification_entry(
    subject: Mapping[str, Any], runtime: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    problems: list[str] = []

    if subject.get("phase_id") != PHASE_ID:
        problems.append("PHASE_ID_MISMATCH")
    if subject.get("phase_branch") != PHASE_BRANCH:
        problems.append("PHASE_BRANCH_MISMATCH")
    construction = subject.get("immutable_construction_evidence", {})
    if construction.get("commit_sha") != CONSTRUCTION_COMMIT:
        problems.append("CONSTRUCTION_COMMIT_MISMATCH")
    if construction.get("tree_sha") != CONSTRUCTION_TREE:
        problems.append("CONSTRUCTION_TREE_MISMATCH")
    if construction.get("independent_review_disposition") != "PASS":
        problems.append("INDEPENDENT_CONSTRUCTION_REVIEW_NOT_PASS")
    if subject.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if subject.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("AUTHORITY_EFFECT_MUST_REMAIN_NONE_EVIDENCE_ONLY")
    if (
        subject.get("phase_state") != "IN_PROGRESS_NOT_QUALIFIED"
        or subject.get("current_disposition") != "NOT_QUALIFIED"
    ):
        problems.append("PREFLIGHT_SUBJECT_MUST_REMAIN_NOT_QUALIFIED")
    cases = subject.get("falsification_matrix", {}).get("case_ids")
    if tuple(cases or ()) != EXPECTED_CASE_IDS:
        problems.append("FALSIFICATION_MATRIX_IDENTITY_MISMATCH")

    bound = dict(runtime if runtime is not None else subject.get("runtime_binding", {}))
    if bound.get("status") != "NOMINATED":
        problems.append("RUNTIME_NOT_NOMINATED")
    else:
        for field in RUNTIME_REQUIRED_FIELDS:
            if bound.get(field) is None or bound.get(field) == "":
                problems.append(f"RUNTIME_FIELD_MISSING:{field}")
        if not _is_hex(bound.get("image_digest"), 64):
            problems.append("RUNTIME_IMAGE_DIGEST_INVALID")
        if not _is_hex(bound.get("mount_options_digest"), 64):
            problems.append("MOUNT_OPTIONS_DIGEST_INVALID")
        if bound.get("candidate_uid") == 0:
            problems.append("CANDIDATE_IDENTITY_IS_ROOT")
        if bound.get("trusted_uid") != 0:
            problems.append("TRUSTED_IDENTITY_IS_NOT_ROOT")
        if bound.get("trusted_path_owner_uid") != 0:
            problems.append("TRUSTED_PATH_NOT_ROOT_OWNED")
        if bound.get("socket_parent_owner_uid") != 0:
            problems.append("SOCKET_PARENT_NOT_ROOT_OWNED")
        if bound.get("record_fs_device") != bound.get("consumed_fs_device"):
            problems.append("RECORD_AND_CONSUMED_FILESYSTEM_DIFFER")
        if bound.get("unprivileged_userns_blocked") is not True:
            problems.append("UNPRIVILEGED_USER_NAMESPACE_NOT_BLOCKED")
        if bound.get("ptrace_candidate_to_service_denied") is not True:
            problems.append("CANDIDATE_PTRACE_DENIAL_NOT_EVIDENCED")
        if bound.get("synthetic_sinks_only") is not True:
            problems.append("SYNTHETIC_EVIDENCE_ONLY_SINKS_NOT_ENFORCED")

    return {
        "phase_id": PHASE_ID,
        "entry_ready": not problems,
        "qualified": False,
        "current_disposition": "NOT_QUALIFIED",
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
        "problems": problems,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    subject_path = root / "implementation/v24/V24-I11-V6-RUNTIME-QUALIFICATION-1-SUBJECT.json"
    subject = json.loads(subject_path.read_text(encoding="utf-8"))
    result = validate_runtime_qualification_entry(subject)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["entry_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
