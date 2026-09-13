"""V24 I11 V6 R14 native-observation successor bindings.

R14 treats every Python process that imports candidate code as untrusted. The
qualification-bearing observation must be emitted by a trusted native parent
that does not initialize Python, and the external oracle must independently
apply the assertion. This module validates externally produced evidence only;
it cannot grant runtime, release, deployment, or terminal authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import AUTHORITY_EFFECT, digest

REQUIRED_R14_CHECKS = frozenset({
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
    "EVERY_REACHABLE_TERMINAL_ALLOWED",
    "GENESIS_CROSS_PAIR_REJECTED",
    "APPLICABLE_PREDICATE_OMISSION_REJECTED",
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
})

SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"
EXTERNAL_AUTHORITY_ORIGIN = "EXTERNAL_REVIEW_BRANCH"
OBSERVATION_TRANSPORT = "NATIVE_PARENT_AUTHENTICATED_FRAME"
OBSERVATION_AUTH = "HMAC_SHA256_EPHEMERAL_NATIVE_PARENT"
ORACLE_DECISION_ORIGIN = "TRUSTED_EXTERNAL_ORACLE"
CANDIDATE_ROLE = "UNTRUSTED_EXECUTION_ONLY"


def _hex(value: Any, n: int) -> bool:
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _record_material(record: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "check_id", "challenge_digest", "request_digest", "observation_digest",
        "assertion_digest", "candidate_commit", "candidate_tree",
        "environment_digest", "interpreter_contract_digest",
        "native_observer_source_git_blob_sha1", "native_observer_binary_sha256",
        "native_observer_compiler_digest", "oracle_git_blob_sha1", "run_id",
        "round_id", "candidate_process_role", "observation_transport",
        "observation_authentication", "native_parent_initializes_python",
        "trusted_parent_imports_candidate_python", "oracle_decision_origin",
        "oracle_control_domain", "candidate_control_domain",
        "oracle_terminal_result", "r13_tailored_frame_regression",
        "r13_tailored_frame_regression_evidence_digest",
    )
    return {key: record.get(key) for key in keys}


def validate_native_observation_evidence_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    if bundle.get("schema_version") != 1:
        problems.append("R14_NATIVE_EVIDENCE_SCHEMA_INVALID")
    if bundle.get("authority_origin") != EXTERNAL_AUTHORITY_ORIGIN:
        problems.append("R14_NATIVE_EVIDENCE_AUTHORITY_ORIGIN_INVALID")
    if bundle.get("candidate_self_grant") is not False:
        problems.append("R14_NATIVE_EVIDENCE_SELF_GRANT_FORBIDDEN")
    if bundle.get("candidate_side_unittest_role") != "NON_AUTHORITATIVE_DIAGNOSTIC_ONLY":
        problems.append("R14_CANDIDATE_UNITTEST_ROLE_INVALID")
    if bundle.get("native_parent_process_initializes_python") is not False:
        problems.append("R14_NATIVE_PARENT_PYTHON_INITIALIZATION_FORBIDDEN")
    if bundle.get("candidate_python_executes_only_in_forked_child") is not True:
        problems.append("R14_CANDIDATE_CHILD_BOUNDARY_REQUIRED")
    if bundle.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("R14_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if bundle.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("R14_AUTHORITY_EFFECT_INVALID")

    commit = bundle.get("candidate_commit")
    tree = bundle.get("candidate_tree")
    env_digest = bundle.get("environment_digest")
    interpreter_digest = bundle.get("interpreter_contract_digest")
    native_source = bundle.get("native_observer_source_git_blob_sha1")
    native_binary = bundle.get("native_observer_binary_sha256")
    compiler_digest = bundle.get("native_observer_compiler_digest")
    oracle_blob = bundle.get("oracle_git_blob_sha1")
    r13_regression_digest = bundle.get("r13_tailored_frame_regression_evidence_digest")
    if not _hex(commit, 40): problems.append("R14_CANDIDATE_COMMIT_INVALID")
    if not _hex(tree, 40): problems.append("R14_CANDIDATE_TREE_INVALID")
    if not _hex(env_digest, 64): problems.append("R14_ENVIRONMENT_DIGEST_INVALID")
    if not _hex(interpreter_digest, 64): problems.append("R14_INTERPRETER_DIGEST_INVALID")
    if not _hex(native_source, 40): problems.append("R14_NATIVE_SOURCE_BLOB_INVALID")
    if not _hex(native_binary, 64): problems.append("R14_NATIVE_BINARY_DIGEST_INVALID")
    if not _hex(compiler_digest, 64): problems.append("R14_COMPILER_DIGEST_INVALID")
    if not _hex(oracle_blob, 40): problems.append("R14_ORACLE_BLOB_INVALID")
    if not _hex(r13_regression_digest, 64): problems.append("R14_R13_REGRESSION_EVIDENCE_DIGEST_INVALID")

    records = bundle.get("records")
    if not isinstance(records, list):
        records = []
        problems.append("R14_NATIVE_EVIDENCE_RECORDS_REQUIRED")

    by_id: dict[str, Mapping[str, Any]] = {}
    valid_record_digests: list[str] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            problems.append(f"R14_NATIVE_RECORD_MALFORMED:{index}")
            continue
        check_id = raw.get("check_id")
        if check_id not in REQUIRED_R14_CHECKS:
            problems.append(f"R14_NATIVE_CHECK_UNKNOWN:{check_id}")
            continue
        if check_id in by_id:
            problems.append(f"R14_NATIVE_CHECK_DUPLICATE:{check_id}")
            continue
        by_id[check_id] = raw
        for key in ("challenge_digest", "request_digest", "observation_digest", "assertion_digest"):
            if not _hex(raw.get(key), 64):
                problems.append(f"R14_NATIVE_DIGEST_INVALID:{check_id}:{key}")
        for key in ("run_id", "round_id", "oracle_control_domain", "candidate_control_domain"):
            if not _nonempty(raw.get(key)):
                problems.append(f"R14_NATIVE_FIELD_REQUIRED:{check_id}:{key}")
        if raw.get("candidate_commit") != commit: problems.append(f"R14_NATIVE_COMMIT_MISMATCH:{check_id}")
        if raw.get("candidate_tree") != tree: problems.append(f"R14_NATIVE_TREE_MISMATCH:{check_id}")
        if raw.get("environment_digest") != env_digest: problems.append(f"R14_NATIVE_ENVIRONMENT_MISMATCH:{check_id}")
        if raw.get("interpreter_contract_digest") != interpreter_digest: problems.append(f"R14_NATIVE_INTERPRETER_MISMATCH:{check_id}")
        if raw.get("native_observer_source_git_blob_sha1") != native_source: problems.append(f"R14_NATIVE_SOURCE_MISMATCH:{check_id}")
        if raw.get("native_observer_binary_sha256") != native_binary: problems.append(f"R14_NATIVE_BINARY_MISMATCH:{check_id}")
        if raw.get("native_observer_compiler_digest") != compiler_digest: problems.append(f"R14_NATIVE_COMPILER_MISMATCH:{check_id}")
        if raw.get("oracle_git_blob_sha1") != oracle_blob: problems.append(f"R14_ORACLE_BLOB_MISMATCH:{check_id}")
        if raw.get("r13_tailored_frame_regression_evidence_digest") != r13_regression_digest:
            problems.append(f"R14_R13_REGRESSION_EVIDENCE_MISMATCH:{check_id}")
        if raw.get("candidate_process_role") != CANDIDATE_ROLE: problems.append(f"R14_CANDIDATE_ROLE_INVALID:{check_id}")
        if raw.get("observation_transport") != OBSERVATION_TRANSPORT: problems.append(f"R14_OBSERVATION_TRANSPORT_INVALID:{check_id}")
        if raw.get("observation_authentication") != OBSERVATION_AUTH: problems.append(f"R14_OBSERVATION_AUTH_INVALID:{check_id}")
        if raw.get("native_parent_initializes_python") is not False: problems.append(f"R14_NATIVE_PARENT_PYTHON_INVALID:{check_id}")
        if raw.get("trusted_parent_imports_candidate_python") is not False: problems.append(f"R14_PARENT_CANDIDATE_IMPORT_INVALID:{check_id}")
        if raw.get("oracle_decision_origin") != ORACLE_DECISION_ORIGIN: problems.append(f"R14_ORACLE_DECISION_ORIGIN_INVALID:{check_id}")
        if raw.get("oracle_control_domain") == raw.get("candidate_control_domain"):
            problems.append(f"R14_ORACLE_NOT_INDEPENDENT:{check_id}")
        if raw.get("oracle_terminal_result") != "PASS": problems.append(f"R14_ORACLE_TERMINAL_RESULT_NOT_PASS:{check_id}")
        if raw.get("r13_tailored_frame_regression") != "REJECTED": problems.append(f"R14_R13_REGRESSION_NOT_REJECTED:{check_id}")
        if "candidate_terminal_result" in raw or "candidate_reported_pass" in raw:
            problems.append(f"R14_CANDIDATE_PASS_FIELD_FORBIDDEN:{check_id}")
        expected = digest(_record_material(raw))
        if raw.get("record_digest") != expected:
            problems.append(f"R14_NATIVE_RECORD_DIGEST_MISMATCH:{check_id}")
        else:
            valid_record_digests.append(expected)

    for missing in sorted(REQUIRED_R14_CHECKS - set(by_id)):
        problems.append(f"R14_NATIVE_CHECK_MISSING:{missing}")
    expected_set_digest = digest({"record_digests": sorted(valid_record_digests)})
    if bundle.get("evidence_set_digest") != expected_set_digest:
        problems.append("R14_NATIVE_EVIDENCE_SET_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": "V24_V6_R14_NATIVE_EVIDENCE_BOUND" if not problems else "V24_V6_R14_NATIVE_EVIDENCE_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "required_check_count": len(REQUIRED_R14_CHECKS),
        "bound_check_count": len(by_id),
        "evidence_set_digest": expected_set_digest,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
    }
