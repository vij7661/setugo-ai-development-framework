"""V24 I11 V6 R12 successor bindings.

R12 does not rewrite the historical R9/R11 integrated-successor manifest.
It adds a new fail-closed evidence contract for mandatory adversarial checks and
for trusted execution-boundary evidence. These validators are construction-only
and never grant runtime, release, deployment, or terminal authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import AUTHORITY_EFFECT, digest

REQUIRED_ADVERSARIAL_CHECKS = frozenset({
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
    "EVERY_REACHABLE_TERMINAL_ALLOWED",
    "GENESIS_CROSS_PAIR_REJECTED",
    "APPLICABLE_PREDICATE_OMISSION_REJECTED",
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
})

SCIENTIFIC_EXECUTION_CLOSED = "CLOSED_PENDING_SUCCESSOR_REVIEW"


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hex(value: Any, n: int) -> bool:
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value)


def _record_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "check_id": record.get("check_id"),
        "execution_state": record.get("execution_state"),
        "terminal_result": record.get("terminal_result"),
        "candidate_commit": record.get("candidate_commit"),
        "candidate_tree": record.get("candidate_tree"),
        "environment_digest": record.get("environment_digest"),
        "interpreter_contract_digest": record.get("interpreter_contract_digest"),
        "evidence_digest": record.get("evidence_digest"),
        "run_id": record.get("run_id"),
        "round_id": record.get("round_id"),
        "producer_control_domain": record.get("producer_control_domain"),
        "witness_id": record.get("witness_id"),
        "witness_control_domain": record.get("witness_control_domain"),
        "witness_authority_origin": record.get("witness_authority_origin"),
    }


def validate_adversarial_evidence_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []

    if bundle.get("schema_version") != 1:
        problems.append("R12_ADVERSARIAL_EVIDENCE_SCHEMA_INVALID")
    if bundle.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH":
        problems.append("R12_ADVERSARIAL_EVIDENCE_AUTHORITY_ORIGIN_INVALID")
    if bundle.get("candidate_self_grant") is not False:
        problems.append("R12_ADVERSARIAL_EVIDENCE_SELF_GRANT_FORBIDDEN")
    if bundle.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("R12_ADVERSARIAL_EVIDENCE_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if bundle.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("R12_ADVERSARIAL_EVIDENCE_AUTHORITY_EFFECT_INVALID")

    candidate_commit = bundle.get("candidate_commit")
    candidate_tree = bundle.get("candidate_tree")
    environment_digest = bundle.get("environment_digest")
    interpreter_contract_digest = bundle.get("interpreter_contract_digest")
    if not _hex(candidate_commit, 40):
        problems.append("R12_ADVERSARIAL_EVIDENCE_CANDIDATE_COMMIT_INVALID")
    if not _hex(candidate_tree, 40):
        problems.append("R12_ADVERSARIAL_EVIDENCE_CANDIDATE_TREE_INVALID")
    if not _hex(environment_digest, 64):
        problems.append("R12_ADVERSARIAL_EVIDENCE_ENVIRONMENT_DIGEST_INVALID")
    if not _hex(interpreter_contract_digest, 64):
        problems.append("R12_ADVERSARIAL_EVIDENCE_INTERPRETER_DIGEST_INVALID")

    records = bundle.get("records")
    if not isinstance(records, list):
        records = []
        problems.append("R12_ADVERSARIAL_EVIDENCE_RECORDS_REQUIRED")

    by_id: dict[str, Mapping[str, Any]] = {}
    valid_record_digests: list[str] = []
    for index, raw in enumerate(records):
        if not isinstance(raw, Mapping):
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_RECORD_MALFORMED:{index}")
            continue
        check_id = raw.get("check_id")
        if check_id not in REQUIRED_ADVERSARIAL_CHECKS:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_CHECK_UNKNOWN:{check_id}")
            continue
        if check_id in by_id:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_CHECK_DUPLICATE:{check_id}")
            continue
        by_id[check_id] = raw

        if raw.get("execution_state") != "EXECUTED":
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_NOT_EXECUTED:{check_id}")
        if raw.get("terminal_result") != "PASS":
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_NOT_PASS:{check_id}")
        if raw.get("candidate_commit") != candidate_commit:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_COMMIT_MISMATCH:{check_id}")
        if raw.get("candidate_tree") != candidate_tree:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_TREE_MISMATCH:{check_id}")
        if raw.get("environment_digest") != environment_digest:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_ENVIRONMENT_MISMATCH:{check_id}")
        if raw.get("interpreter_contract_digest") != interpreter_contract_digest:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_INTERPRETER_MISMATCH:{check_id}")
        if not _hex(raw.get("evidence_digest"), 64):
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_DIGEST_INVALID:{check_id}")
        for key in ("run_id", "round_id", "producer_control_domain", "witness_id", "witness_control_domain"):
            if not _nonempty(raw.get(key)):
                problems.append(f"R12_ADVERSARIAL_EVIDENCE_FIELD_REQUIRED:{check_id}:{key}")
        if raw.get("witness_authority_origin") != "EXTERNAL_REVIEW_BRANCH":
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_WITNESS_ORIGIN_INVALID:{check_id}")
        if (
            _nonempty(raw.get("producer_control_domain"))
            and raw.get("producer_control_domain") == raw.get("witness_control_domain")
        ):
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_WITNESS_NOT_INDEPENDENT:{check_id}")

        expected_digest = digest(_record_material(raw))
        if raw.get("record_digest") != expected_digest:
            problems.append(f"R12_ADVERSARIAL_EVIDENCE_RECORD_DIGEST_MISMATCH:{check_id}")
        else:
            valid_record_digests.append(expected_digest)

    for missing in sorted(REQUIRED_ADVERSARIAL_CHECKS - set(by_id)):
        problems.append(f"R12_ADVERSARIAL_EVIDENCE_CHECK_MISSING:{missing}")

    expected_set_digest = digest({"record_digests": sorted(valid_record_digests)})
    if bundle.get("evidence_set_digest") != expected_set_digest:
        problems.append("R12_ADVERSARIAL_EVIDENCE_SET_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": "V24_V6_R12_ADVERSARIAL_EVIDENCE_BOUND" if not problems else "V24_V6_R12_ADVERSARIAL_EVIDENCE_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "required_check_count": len(REQUIRED_ADVERSARIAL_CHECKS),
        "bound_check_count": len(by_id),
        "evidence_set_digest": expected_set_digest,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_execution_boundary_evidence(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate externally produced R12 execution-boundary evidence.

    This validates the evidence record shape/bindings only. It does not itself
    prove the external process properties; those must be produced by the trusted
    review-side parent before candidate bytes execute.
    """
    problems: list[str] = []
    if record.get("schema_version") != 1:
        problems.append("R12_EXECUTION_BOUNDARY_SCHEMA_INVALID")
    if record.get("authority_origin") != "EXTERNAL_REVIEW_BRANCH":
        problems.append("R12_EXECUTION_BOUNDARY_AUTHORITY_ORIGIN_INVALID")
    if record.get("candidate_self_grant") is not False:
        problems.append("R12_EXECUTION_BOUNDARY_SELF_GRANT_FORBIDDEN")
    for key in ("candidate_commit", "candidate_tree", "trusted_parent_git_blob_sha1", "trusted_worker_git_blob_sha1"):
        if not _hex(record.get(key), 40):
            problems.append(f"R12_EXECUTION_BOUNDARY_GIT_ID_INVALID:{key}")
    for key in ("environment_digest", "interpreter_contract_digest", "execution_transcript_digest"):
        if not _hex(record.get(key), 64):
            problems.append(f"R12_EXECUTION_BOUNDARY_SHA256_INVALID:{key}")
    actual = record.get("actual_interpreter_flags")
    if not isinstance(actual, Mapping):
        actual = {}
        problems.append("R12_EXECUTION_BOUNDARY_ACTUAL_FLAGS_REQUIRED")
    required_true = ("isolated", "no_site", "ignore_environment", "safe_path")
    for key in required_true:
        if actual.get(key) is not True:
            problems.append(f"R12_EXECUTION_BOUNDARY_FLAG_NOT_TRUE:{key}")
    if record.get("trusted_parent_imported_candidate") is not False:
        problems.append("R12_EXECUTION_BOUNDARY_PARENT_IMPORTED_CANDIDATE")
    if record.get("candidate_shared_trusted_result_state") is not False:
        problems.append("R12_EXECUTION_BOUNDARY_SHARED_RESULT_STATE")
    if record.get("result_accounting_origin") != "TRUSTED_PARENT":
        problems.append("R12_EXECUTION_BOUNDARY_RESULT_ACCOUNTING_ORIGIN_INVALID")
    if record.get("scientific_execution_state") != SCIENTIFIC_EXECUTION_CLOSED:
        problems.append("R12_EXECUTION_BOUNDARY_SCIENTIFIC_EXECUTION_MUST_REMAIN_CLOSED")
    if record.get("authority_effect") != AUTHORITY_EFFECT:
        problems.append("R12_EXECUTION_BOUNDARY_AUTHORITY_EFFECT_INVALID")

    problems = sorted(set(problems))
    return {
        "state": "V24_V6_R12_EXECUTION_BOUNDARY_BOUND" if not problems else "V24_V6_R12_EXECUTION_BOUNDARY_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_CLOSED,
        "authority_effect": AUTHORITY_EFFECT,
    }
