"""R12 executed-evidence binding for mandatory V6 adversarial checks.

This validator is construction-only.  It deliberately refuses to treat a
check name, child-process exit code, or self-authored PASS label as evidence
that a mandatory adversarial check executed successfully.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from v24_v6_governance_foundation import AUTHORITY_EFFECT, digest

SCIENTIFIC_EXECUTION_STATE = "CLOSED_PENDING_R12_SUCCESSOR_REVIEW"
EXTERNAL_AUTHORITY_ORIGIN = "EXTERNAL_REVIEW_BRANCH"
EXECUTED = "EXECUTED"
PASS = "PASS"
CURRENT = "CURRENT"

REQUIRED_ADVERSARIAL_CHECKS = frozenset({
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
    "EVERY_REACHABLE_TERMINAL_ALLOWED",
    "GENESIS_CROSS_PAIR_REJECTED",
    "APPLICABLE_PREDICATE_OMISSION_REJECTED",
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
})

RECORD_FIELDS = frozenset({
    "check_id",
    "candidate_commit",
    "candidate_tree",
    "environment_contract_digest",
    "run_id",
    "round_id",
    "terminal_state",
    "result",
    "execution_evidence_digest",
    "producer_identity",
    "witness_identity",
    "authority_origin",
    "candidate_self_authored",
    "currentness_state",
    "record_digest",
})


def _git_sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v)


def evidence_record_digest(record: Mapping[str, Any]) -> str:
    material = {k: record.get(k) for k in sorted(RECORD_FIELDS - {"record_digest"})}
    return digest(material)


def validate_mandatory_adversarial_evidence(
    *,
    records: Sequence[Mapping[str, Any]] | Any,
    expected_candidate_commit: str,
    expected_candidate_tree: str,
    expected_environment_contract_digest: str,
    expected_run_id: str,
    expected_round_id: str,
    forbidden_producer_identities: Sequence[str] = (),
) -> dict[str, Any]:
    """Validate one current externally-witnessed executed record per required check."""
    problems: list[str] = []

    if not _git_sha(expected_candidate_commit):
        problems.append("ADVERSARIAL_EVIDENCE_EXPECTED_CANDIDATE_COMMIT_INVALID")
    if not _git_sha(expected_candidate_tree):
        problems.append("ADVERSARIAL_EVIDENCE_EXPECTED_CANDIDATE_TREE_INVALID")
    if not _sha256(expected_environment_contract_digest):
        problems.append("ADVERSARIAL_EVIDENCE_EXPECTED_ENVIRONMENT_DIGEST_INVALID")
    if not _nonempty(expected_run_id):
        problems.append("ADVERSARIAL_EVIDENCE_EXPECTED_RUN_ID_INVALID")
    if not _nonempty(expected_round_id):
        problems.append("ADVERSARIAL_EVIDENCE_EXPECTED_ROUND_ID_INVALID")

    if not isinstance(records, Sequence) or isinstance(records, (str, bytes, bytearray)):
        records = []
        problems.append("ADVERSARIAL_EVIDENCE_RECORDS_REQUIRED")

    forbidden = set(forbidden_producer_identities)
    by_check: dict[str, Mapping[str, Any]] = {}
    normalized: list[dict[str, Any]] = []

    for i, record in enumerate(records):
        if not isinstance(record, Mapping):
            problems.append(f"ADVERSARIAL_EVIDENCE_RECORD_MALFORMED:{i}")
            continue
        extra = set(record) - RECORD_FIELDS
        missing_fields = RECORD_FIELDS - set(record)
        for key in sorted(extra):
            problems.append(f"ADVERSARIAL_EVIDENCE_FIELD_UNKNOWN:{i}:{key}")
        for key in sorted(missing_fields):
            problems.append(f"ADVERSARIAL_EVIDENCE_FIELD_MISSING:{i}:{key}")

        check_id = record.get("check_id")
        if check_id not in REQUIRED_ADVERSARIAL_CHECKS:
            problems.append(f"ADVERSARIAL_EVIDENCE_CHECK_UNKNOWN:{check_id}")
            continue
        if check_id in by_check:
            problems.append(f"ADVERSARIAL_EVIDENCE_CHECK_DUPLICATE:{check_id}")
            continue
        by_check[check_id] = record

        if record.get("candidate_commit") != expected_candidate_commit:
            problems.append(f"ADVERSARIAL_EVIDENCE_CANDIDATE_COMMIT_MISMATCH:{check_id}")
        if record.get("candidate_tree") != expected_candidate_tree:
            problems.append(f"ADVERSARIAL_EVIDENCE_CANDIDATE_TREE_MISMATCH:{check_id}")
        if record.get("environment_contract_digest") != expected_environment_contract_digest:
            problems.append(f"ADVERSARIAL_EVIDENCE_ENVIRONMENT_MISMATCH:{check_id}")
        if record.get("run_id") != expected_run_id:
            problems.append(f"ADVERSARIAL_EVIDENCE_RUN_MISMATCH:{check_id}")
        if record.get("round_id") != expected_round_id:
            problems.append(f"ADVERSARIAL_EVIDENCE_ROUND_MISMATCH:{check_id}")
        if record.get("terminal_state") != EXECUTED:
            problems.append(f"ADVERSARIAL_EVIDENCE_NOT_EXECUTED:{check_id}")
        if record.get("result") != PASS:
            problems.append(f"ADVERSARIAL_EVIDENCE_NOT_PASS:{check_id}")
        if not _sha256(record.get("execution_evidence_digest")):
            problems.append(f"ADVERSARIAL_EVIDENCE_EXECUTION_DIGEST_INVALID:{check_id}")
        producer = record.get("producer_identity")
        witness = record.get("witness_identity")
        if not _nonempty(producer):
            problems.append(f"ADVERSARIAL_EVIDENCE_PRODUCER_REQUIRED:{check_id}")
        if not _nonempty(witness):
            problems.append(f"ADVERSARIAL_EVIDENCE_WITNESS_REQUIRED:{check_id}")
        if producer == witness:
            problems.append(f"ADVERSARIAL_EVIDENCE_WITNESS_NOT_INDEPENDENT:{check_id}")
        if producer in forbidden:
            problems.append(f"ADVERSARIAL_EVIDENCE_PRODUCER_FORBIDDEN:{check_id}")
        if witness in forbidden:
            problems.append(f"ADVERSARIAL_EVIDENCE_WITNESS_FORBIDDEN:{check_id}")
        if record.get("authority_origin") != EXTERNAL_AUTHORITY_ORIGIN:
            problems.append(f"ADVERSARIAL_EVIDENCE_AUTHORITY_ORIGIN_INVALID:{check_id}")
        if record.get("candidate_self_authored") is not False:
            problems.append(f"ADVERSARIAL_EVIDENCE_SELF_AUTHORED_FORBIDDEN:{check_id}")
        if record.get("currentness_state") != CURRENT:
            problems.append(f"ADVERSARIAL_EVIDENCE_STALE:{check_id}")
        actual_digest = evidence_record_digest(record)
        if record.get("record_digest") != actual_digest:
            problems.append(f"ADVERSARIAL_EVIDENCE_RECORD_DIGEST_MISMATCH:{check_id}")

        normalized.append({k: record.get(k) for k in sorted(RECORD_FIELDS)})

    for missing in sorted(REQUIRED_ADVERSARIAL_CHECKS - set(by_check)):
        problems.append(f"ADVERSARIAL_EVIDENCE_REQUIRED_CHECK_MISSING:{missing}")

    problems = sorted(set(problems))
    normalized.sort(key=lambda r: str(r.get("check_id")))
    binding_material = {
        "candidate_commit": expected_candidate_commit,
        "candidate_tree": expected_candidate_tree,
        "environment_contract_digest": expected_environment_contract_digest,
        "run_id": expected_run_id,
        "round_id": expected_round_id,
        "records": normalized,
    }
    return {
        "state": "MANDATORY_ADVERSARIAL_EVIDENCE_BOUND" if not problems else "MANDATORY_ADVERSARIAL_EVIDENCE_INVALID",
        "valid": not problems,
        "qualified": False,
        "problems": problems,
        "record_count": len(normalized),
        "binding_digest": digest(binding_material),
        "records": normalized,
        "scientific_execution_state": SCIENTIFIC_EXECUTION_STATE,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R12_ADVERSARIAL_EVIDENCE_BINDING_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R12",
        "scientific_execution_state": SCIENTIFIC_EXECUTION_STATE,
        "authority_effect": AUTHORITY_EFFECT,
    }
