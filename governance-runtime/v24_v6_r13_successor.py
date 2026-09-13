"""R13 external trusted-oracle evidence bindings.

Candidate-side tests and observations remain non-authoritative. This module only
validates externally produced evidence structure; it never grants runtime or
release authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import AUTHORITY_EFFECT, digest

REQUIRED_ORACLE_CHECKS = frozenset({
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
    "EVERY_REACHABLE_TERMINAL_ALLOWED",
    "GENESIS_CROSS_PAIR_REJECTED",
    "APPLICABLE_PREDICATE_OMISSION_REJECTED",
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
})
SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"
ORACLE_ORIGIN = "EXTERNAL_REVIEW_BRANCH"
ORACLE_DECISION_ORIGIN = "TRUSTED_EXTERNAL_ORACLE"
CANDIDATE_ROLE = "UNTRUSTED_OBSERVATION_ONLY"


def _hex(value: Any, n: int) -> bool:
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _record_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "check_id": record.get("check_id"),
        "challenge_digest": record.get("challenge_digest"),
        "request_digest": record.get("request_digest"),
        "observation_digest": record.get("observation_digest"),
        "assertion_digest": record.get("assertion_digest"),
        "candidate_commit": record.get("candidate_commit"),
        "candidate_tree": record.get("candidate_tree"),
        "environment_digest": record.get("environment_digest"),
        "interpreter_contract_digest": record.get("interpreter_contract_digest"),
        "oracle_git_blob_sha1": record.get("oracle_git_blob_sha1"),
        "observer_git_blob_sha1": record.get("observer_git_blob_sha1"),
        "run_id": record.get("run_id"),
        "round_id": record.get("round_id"),
        "candidate_process_role": record.get("candidate_process_role"),
        "oracle_decision_origin": record.get("oracle_decision_origin"),
        "oracle_control_domain": record.get("oracle_control_domain"),
        "candidate_control_domain": record.get("candidate_control_domain"),
        "oracle_terminal_result": record.get("oracle_terminal_result"),
    }


def validate_external_oracle_evidence_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    if bundle.get("schema_version") != 1:
        problems.append("R13_ORACLE_EVIDENCE_SCHEMA_INVALID")
    if bundle.get("authority_origin") != ORACLE_ORIGIN:
        problems.append("R13_ORACLE_AUTHORITY_ORIGIN_INVALID")
    if bundle.get("candidate_self_grant") is not False:
        problems.append("R13_ORACLE_SELF_GRANT_FORBIDDEN")
    if bundle.get("candidate_side_unittest_role") != "NON_AUTHORITATIVE_DIAGNOSTIC_ONLY":
        problems.append("R13_CANDIDATE_UNITTEST_ROLE_INVALID")
    if bundle.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("R13_ORACLE_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if bundle.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("R13_ORACLE_AUTHORITY_EFFECT_INVALID")

    commit, tree = bundle.get("candidate_commit"), bundle.get("candidate_tree")
    env_digest = bundle.get("environment_digest")
    interpreter_digest = bundle.get("interpreter_contract_digest")
    oracle_blob, observer_blob = bundle.get("oracle_git_blob_sha1"), bundle.get("observer_git_blob_sha1")
    if not _hex(commit, 40): problems.append("R13_ORACLE_CANDIDATE_COMMIT_INVALID")
    if not _hex(tree, 40): problems.append("R13_ORACLE_CANDIDATE_TREE_INVALID")
    if not _hex(env_digest, 64): problems.append("R13_ORACLE_ENVIRONMENT_DIGEST_INVALID")
    if not _hex(interpreter_digest, 64): problems.append("R13_ORACLE_INTERPRETER_DIGEST_INVALID")
    if not _hex(oracle_blob, 40): problems.append("R13_ORACLE_BLOB_INVALID")
    if not _hex(observer_blob, 40): problems.append("R13_OBSERVER_BLOB_INVALID")

    records = bundle.get("records")
    if not isinstance(records, list):
        records = []
        problems.append("R13_ORACLE_RECORDS_REQUIRED")

    by_id: dict[str, Mapping[str, Any]] = {}
    valid_digests: list[str] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            problems.append(f"R13_ORACLE_RECORD_MALFORMED:{index}")
            continue
        check_id = raw.get("check_id")
        if check_id not in REQUIRED_ORACLE_CHECKS:
            problems.append(f"R13_ORACLE_CHECK_UNKNOWN:{check_id}")
            continue
        if check_id in by_id:
            problems.append(f"R13_ORACLE_CHECK_DUPLICATE:{check_id}")
            continue
        by_id[check_id] = raw
        for key in ("challenge_digest", "request_digest", "observation_digest", "assertion_digest"):
            if not _hex(raw.get(key), 64): problems.append(f"R13_ORACLE_DIGEST_INVALID:{check_id}:{key}")
        for key in ("run_id", "round_id", "oracle_control_domain", "candidate_control_domain"):
            if not _nonempty(raw.get(key)): problems.append(f"R13_ORACLE_FIELD_REQUIRED:{check_id}:{key}")
        if raw.get("candidate_commit") != commit: problems.append(f"R13_ORACLE_COMMIT_MISMATCH:{check_id}")
        if raw.get("candidate_tree") != tree: problems.append(f"R13_ORACLE_TREE_MISMATCH:{check_id}")
        if raw.get("environment_digest") != env_digest: problems.append(f"R13_ORACLE_ENVIRONMENT_MISMATCH:{check_id}")
        if raw.get("interpreter_contract_digest") != interpreter_digest: problems.append(f"R13_ORACLE_INTERPRETER_MISMATCH:{check_id}")
        if raw.get("oracle_git_blob_sha1") != oracle_blob: problems.append(f"R13_ORACLE_BLOB_MISMATCH:{check_id}")
        if raw.get("observer_git_blob_sha1") != observer_blob: problems.append(f"R13_OBSERVER_BLOB_MISMATCH:{check_id}")
        if raw.get("candidate_process_role") != CANDIDATE_ROLE: problems.append(f"R13_CANDIDATE_ROLE_INVALID:{check_id}")
        if raw.get("oracle_decision_origin") != ORACLE_DECISION_ORIGIN: problems.append(f"R13_ORACLE_DECISION_ORIGIN_INVALID:{check_id}")
        if raw.get("oracle_control_domain") == raw.get("candidate_control_domain"):
            problems.append(f"R13_ORACLE_NOT_INDEPENDENT:{check_id}")
        if raw.get("oracle_terminal_result") != "PASS": problems.append(f"R13_ORACLE_TERMINAL_RESULT_NOT_PASS:{check_id}")
        if "candidate_terminal_result" in raw or "candidate_reported_pass" in raw:
            problems.append(f"R13_CANDIDATE_PASS_FIELD_FORBIDDEN:{check_id}")
        expected = digest(_record_material(raw))
        if raw.get("record_digest") != expected:
            problems.append(f"R13_ORACLE_RECORD_DIGEST_MISMATCH:{check_id}")
        else:
            valid_digests.append(expected)

    for missing in sorted(REQUIRED_ORACLE_CHECKS - set(by_id)):
        problems.append(f"R13_ORACLE_CHECK_MISSING:{missing}")
    expected_set_digest = digest({"record_digests": sorted(valid_digests)})
    if bundle.get("evidence_set_digest") != expected_set_digest:
        problems.append("R13_ORACLE_EVIDENCE_SET_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": "V24_V6_R13_EXTERNAL_ORACLE_EVIDENCE_BOUND" if not problems else "V24_V6_R13_EXTERNAL_ORACLE_EVIDENCE_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "required_check_count": len(REQUIRED_ORACLE_CHECKS),
        "bound_check_count": len(by_id),
        "evidence_set_digest": expected_set_digest,
        "candidate_side_unittest_role": "NON_AUTHORITATIVE_DIAGNOSTIC_ONLY",
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
    }
