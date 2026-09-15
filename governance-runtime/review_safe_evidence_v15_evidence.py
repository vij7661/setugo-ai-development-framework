#!/usr/bin/env python3
"""V15 raw-evidence registry and governed NOT_APPLICABLE lifecycle.

Construction-stage implementation only. No authority effect.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    canonical_hash,
    validate_independently_rooted_proof,
)

EVIDENCE_STATES = frozenset({
    "CAPTURED",
    "EVIDENCE_MISSING",
    "NOT_APPLICABLE_WITH_GOVERNED_PROOF",
})
NA_CHALLENGE_STATES = frozenset({
    "OPEN",
    "RESOLVED_SUPPORTED",
    "RESOLVED_REJECTED",
    "EXPIRED",
})
OBSERVATION_APPLICABILITY = "OBSERVATION_APPLICABILITY"


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _sealed_digest(record: Mapping[str, Any], field: str) -> str:
    return canonical_hash({k: v for k, v in record.items() if k != field})


def _result(problems: list[str], ok: str, bad: str) -> dict[str, Any]:
    p = sorted(set(problems))
    return {
        "state": ok if not p else bad,
        "valid": not p,
        "qualified": False,
        "problems": p,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_raw_evidence_record(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("RAW_EVIDENCE_SCHEMA_INVALID")
    for key in (
        "evidence_id", "obligation_id", "candidate_id", "snapshot_id", "generation_id",
        "environment_id", "capture_authority_id", "capture_control_domain_id",
        "source_identity", "currentness_state",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"RAW_EVIDENCE_FIELD_REQUIRED:{key}")
    state = record.get("state")
    if state not in EVIDENCE_STATES:
        p.append("RAW_EVIDENCE_STATE_INVALID")
    if record.get("candidate_self_captured") is not False:
        p.append("RAW_EVIDENCE_CANDIDATE_SELF_CAPTURE_FORBIDDEN")
    if record.get("currentness_state") != "CURRENT":
        p.append("RAW_EVIDENCE_NOT_CURRENT")
    if not _sha256(record.get("source_digest")):
        p.append("RAW_EVIDENCE_SOURCE_DIGEST_INVALID")

    payload_digest = record.get("payload_digest")
    na_proof_id = record.get("not_applicable_proof_id")
    na_proof_digest = record.get("not_applicable_proof_digest")
    if state == "CAPTURED":
        if not _sha256(payload_digest):
            p.append("RAW_EVIDENCE_CAPTURED_PAYLOAD_DIGEST_REQUIRED")
        if na_proof_id is not None or na_proof_digest is not None:
            p.append("RAW_EVIDENCE_CAPTURED_MUST_NOT_CARRY_NA_PROOF")
    elif state == "EVIDENCE_MISSING":
        if payload_digest is not None:
            p.append("RAW_EVIDENCE_MISSING_MUST_NOT_CARRY_PAYLOAD")
        if na_proof_id is not None or na_proof_digest is not None:
            p.append("RAW_EVIDENCE_MISSING_MUST_NOT_CARRY_NA_PROOF")
    elif state == "NOT_APPLICABLE_WITH_GOVERNED_PROOF":
        if payload_digest is not None:
            p.append("RAW_EVIDENCE_NA_MUST_NOT_CARRY_PAYLOAD")
        if not _nonempty(na_proof_id):
            p.append("RAW_EVIDENCE_NA_PROOF_ID_REQUIRED")
        if not _sha256(na_proof_digest):
            p.append("RAW_EVIDENCE_NA_PROOF_DIGEST_REQUIRED")

    predecessor = record.get("predecessor_record_digest")
    if predecessor != "GENESIS" and not _sha256(predecessor):
        p.append("RAW_EVIDENCE_PREDECESSOR_DIGEST_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("RAW_EVIDENCE_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("RAW_EVIDENCE_RECORD_DIGEST_MISMATCH")
    return _result(p, "RAW_EVIDENCE_RECORD_VALID", "RAW_EVIDENCE_RECORD_INVALID")


def validate_not_applicable_proof(record: Mapping[str, Any], *,
                                  independence_proof: Mapping[str, Any],
                                  current_sequence: int) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("N_A_PROOF_SCHEMA_INVALID")
    for key in (
        "proof_id", "obligation_id", "subject_id", "candidate_id", "snapshot_id", "generation_id",
        "proof_authority_id", "proof_control_domain_id", "verifier_id", "verifier_control_domain_id",
        "currentness_rule",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"N_A_PROOF_FIELD_REQUIRED:{key}")
    if record.get("candidate_self_authored") is not False:
        p.append("N_A_PROOF_SELF_AUTHORED_FORBIDDEN")
    if record.get("result") != "NOT_APPLICABLE_SUPPORTED":
        p.append("N_A_PROOF_RESULT_NOT_SUPPORTED")
    if record.get("contradiction_state") != "NONE":
        p.append("N_A_PROOF_CONTRADICTED")
    if not _sha256(record.get("source_digest")):
        p.append("N_A_PROOF_SOURCE_DIGEST_INVALID")
    challenges = record.get("challenge_evidence_digests")
    if not isinstance(challenges, list) or not challenges or not all(_sha256(x) for x in challenges):
        p.append("N_A_PROOF_CHALLENGE_EVIDENCE_REQUIRED")
    issued = record.get("issued_sequence")
    expires = record.get("expires_sequence")
    if not isinstance(issued, int) or issued < 1:
        p.append("N_A_PROOF_ISSUED_SEQUENCE_INVALID")
    if not isinstance(expires, int) or not isinstance(issued, int) or expires <= issued:
        p.append("N_A_PROOF_EXPIRY_INVALID")
    elif current_sequence > expires:
        p.append("N_A_PROOF_EXPIRED")

    checked = validate_independently_rooted_proof(independence_proof)
    if not checked["valid"]:
        p.extend(f"N_A_INDEPENDENCE:{x}" for x in checked["problems"])
    expected_subjects = frozenset((str(record.get("proof_control_domain_id")), str(record.get("verifier_control_domain_id"))))
    actual_subjects = frozenset((str(independence_proof.get("subject_a")), str(independence_proof.get("subject_b"))))
    if expected_subjects != actual_subjects:
        p.append("N_A_PROOF_INDEPENDENCE_SUBJECT_MISMATCH")
    if independence_proof.get("result") != "INDEPENDENT":
        p.append("N_A_PROOF_VERIFIER_INDEPENDENCE_REQUIRED")
    if record.get("proof_control_domain_id") == record.get("verifier_control_domain_id"):
        p.append("N_A_PROOF_CONTROL_DOMAIN_COLLAPSE")

    supplied = record.get("proof_digest")
    if not _sha256(supplied):
        p.append("N_A_PROOF_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "proof_digest"):
        p.append("N_A_PROOF_DIGEST_MISMATCH")
    out = _result(p, "N_A_GOVERNED_PROOF_VALID", "N_A_GOVERNED_PROOF_INVALID")
    out["promotion_blocked"] = not out["valid"]
    return out


def validate_na_challenge(record: Mapping[str, Any], *, proof: Mapping[str, Any],
                          current_sequence: int) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("N_A_CHALLENGE_SCHEMA_INVALID")
    for key in ("challenge_id", "proof_id", "obligation_id", "snapshot_id", "generation_id",
                "challenger_id", "verifier_id"):
        if not _nonempty(record.get(key)):
            p.append(f"N_A_CHALLENGE_FIELD_REQUIRED:{key}")
    if record.get("proof_id") != proof.get("proof_id"):
        p.append("N_A_CHALLENGE_PROOF_ID_MISMATCH")
    if record.get("obligation_id") != proof.get("obligation_id"):
        p.append("N_A_CHALLENGE_OBLIGATION_MISMATCH")
    if record.get("snapshot_id") != proof.get("snapshot_id"):
        p.append("N_A_CHALLENGE_SNAPSHOT_MISMATCH")
    if record.get("generation_id") != proof.get("generation_id"):
        p.append("N_A_CHALLENGE_GENERATION_MISMATCH")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("N_A_CHALLENGE_VERIFIER_INDEPENDENCE_REQUIRED")
    state = record.get("state")
    if state not in NA_CHALLENGE_STATES:
        p.append("N_A_CHALLENGE_STATE_INVALID")
    opened = record.get("opened_sequence")
    expires = record.get("expires_sequence")
    if not isinstance(opened, int) or opened < 1:
        p.append("N_A_CHALLENGE_OPENED_SEQUENCE_INVALID")
    if not isinstance(expires, int) or not isinstance(opened, int) or expires <= opened:
        p.append("N_A_CHALLENGE_EXPIRY_INVALID")
    elif current_sequence > expires and state not in {"RESOLVED_SUPPORTED", "RESOLVED_REJECTED"}:
        p.append("N_A_CHALLENGE_EXPIRED_UNRESOLVED")
    if state in {"RESOLVED_SUPPORTED", "RESOLVED_REJECTED"}:
        if not _sha256(record.get("resolution_evidence_digest")):
            p.append("N_A_CHALLENGE_RESOLUTION_EVIDENCE_REQUIRED")
        if not _nonempty(record.get("resolution_verifier_id")):
            p.append("N_A_CHALLENGE_RESOLUTION_VERIFIER_REQUIRED")
    supplied = record.get("challenge_digest")
    if not _sha256(supplied):
        p.append("N_A_CHALLENGE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "challenge_digest"):
        p.append("N_A_CHALLENGE_DIGEST_MISMATCH")
    out = _result(p, "N_A_CHALLENGE_RECORD_VALID", "N_A_CHALLENGE_RECORD_INVALID")
    out["promotion_blocked"] = (not out["valid"]) or state in {"OPEN", "EXPIRED", "RESOLVED_REJECTED"}
    return out


def validate_observation_applicability(record: Mapping[str, Any], *,
                                       na_proof: Mapping[str, Any] | None,
                                       independence_proof: Mapping[str, Any] | None,
                                       current_sequence: int) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("OBSERVATION_APPLICABILITY_SCHEMA_INVALID")
    for key in ("observation_source_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"OBSERVATION_APPLICABILITY_FIELD_REQUIRED:{key}")
    applicable = record.get("applicable")
    if applicable not in {True, False}:
        p.append("OBSERVATION_APPLICABILITY_BOOLEAN_REQUIRED")
    if applicable is False:
        if na_proof is None or independence_proof is None:
            p.append("OBSERVATION_APPLICABILITY_N_A_PROOF_REQUIRED")
        else:
            proof_result = validate_not_applicable_proof(
                na_proof, independence_proof=independence_proof, current_sequence=current_sequence)
            if not proof_result["valid"]:
                p.extend(f"OBSERVATION_N_A:{x}" for x in proof_result["problems"])
            if na_proof.get("subject_id") != record.get("observation_source_id"):
                p.append("OBSERVATION_APPLICABILITY_N_A_SUBJECT_MISMATCH")
            if na_proof.get("candidate_id") != record.get("candidate_id") or na_proof.get("snapshot_id") != record.get("snapshot_id"):
                p.append("OBSERVATION_APPLICABILITY_N_A_CONTEXT_MISMATCH")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("OBSERVATION_APPLICABILITY_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("OBSERVATION_APPLICABILITY_DIGEST_MISMATCH")
    out = _result(p, "OBSERVATION_APPLICABILITY_VALID", "OBSERVATION_APPLICABILITY_INVALID")
    out["promotion_blocked"] = not out["valid"]
    return out


def validate_evidence_registry(bundle: Mapping[str, Any], *, expected_obligations: Sequence[str],
                               na_proofs: Mapping[str, tuple[Mapping[str, Any], Mapping[str, Any]]],
                               challenges: Mapping[str, Sequence[Mapping[str, Any]]],
                               current_sequence: int) -> dict[str, Any]:
    p: list[str] = []
    blocking: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("EVIDENCE_REGISTRY_SCHEMA_INVALID")
    for key in ("registry_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"EVIDENCE_REGISTRY_FIELD_REQUIRED:{key}")
    expected = list(expected_obligations)
    if not expected or not all(_nonempty(x) for x in expected) or len(expected) != len(set(expected)):
        p.append("EVIDENCE_REGISTRY_EXPECTED_OBLIGATIONS_INVALID")
    rows = bundle.get("records")
    if not isinstance(rows, list):
        rows = []
        p.append("EVIDENCE_REGISTRY_RECORDS_REQUIRED")
    by_obligation: dict[str, Mapping[str, Any]] = {}
    prev = "GENESIS"
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"EVIDENCE_REGISTRY_RECORD_MALFORMED:{i}")
            continue
        checked = validate_raw_evidence_record(row)
        if not checked["valid"]:
            p.extend(f"EVIDENCE_RECORD[{i}]:{x}" for x in checked["problems"])
        oid = row.get("obligation_id")
        if isinstance(oid, str):
            if oid in by_obligation:
                p.append(f"EVIDENCE_REGISTRY_DUPLICATE_OBLIGATION:{oid}")
            else:
                by_obligation[oid] = row
        if row.get("candidate_id") != bundle.get("candidate_id") or row.get("snapshot_id") != bundle.get("snapshot_id") or row.get("generation_id") != bundle.get("generation_id"):
            p.append(f"EVIDENCE_REGISTRY_CONTEXT_MISMATCH:{row.get('evidence_id')}")
        if row.get("predecessor_record_digest") != prev:
            p.append(f"EVIDENCE_REGISTRY_PREDECESSOR_MISMATCH:{row.get('evidence_id')}")
        if _sha256(row.get("record_digest")):
            prev = str(row["record_digest"])

    exp_set = set(expected)
    for oid in sorted(exp_set - set(by_obligation)):
        p.append(f"EVIDENCE_REGISTRY_OBLIGATION_RECORD_MISSING:{oid}")
        blocking.append(f"EVIDENCE_MISSING:{oid}")
    for oid in sorted(set(by_obligation) - exp_set):
        p.append(f"EVIDENCE_REGISTRY_UNDERIVED_OBLIGATION:{oid}")

    for oid in sorted(exp_set & set(by_obligation)):
        row = by_obligation[oid]
        state = row.get("state")
        if state == "EVIDENCE_MISSING":
            blocking.append(f"EVIDENCE_MISSING:{oid}")
        elif state == "NOT_APPLICABLE_WITH_GOVERNED_PROOF":
            proof_id = row.get("not_applicable_proof_id")
            pair = na_proofs.get(str(proof_id)) if isinstance(proof_id, str) else None
            if pair is None:
                p.append(f"EVIDENCE_REGISTRY_N_A_PROOF_NOT_FOUND:{oid}:{proof_id}")
                blocking.append(f"N_A_INVALID:{oid}")
                continue
            proof, independence = pair
            checked = validate_not_applicable_proof(
                proof, independence_proof=independence, current_sequence=current_sequence)
            if not checked["valid"]:
                p.extend(f"N_A_PROOF[{oid}]:{x}" for x in checked["problems"])
                blocking.append(f"N_A_INVALID:{oid}")
            if proof.get("proof_id") != proof_id or proof.get("proof_digest") != row.get("not_applicable_proof_digest"):
                p.append(f"EVIDENCE_REGISTRY_N_A_BINDING_MISMATCH:{oid}")
                blocking.append(f"N_A_INVALID:{oid}")
            if proof.get("obligation_id") != oid or proof.get("candidate_id") != bundle.get("candidate_id") or proof.get("snapshot_id") != bundle.get("snapshot_id") or proof.get("generation_id") != bundle.get("generation_id"):
                p.append(f"EVIDENCE_REGISTRY_N_A_CONTEXT_MISMATCH:{oid}")
                blocking.append(f"N_A_INVALID:{oid}")
            for challenge in challenges.get(str(proof_id), ()): 
                c = validate_na_challenge(challenge, proof=proof, current_sequence=current_sequence)
                if not c["valid"]:
                    p.extend(f"N_A_CHALLENGE[{oid}]:{x}" for x in c["problems"])
                if c["promotion_blocked"]:
                    blocking.append(f"N_A_CHALLENGE_BLOCKING:{oid}:{challenge.get('challenge_id')}")

    expected_head = "GENESIS" if not rows else rows[-1].get("record_digest")
    if bundle.get("registry_head_digest") != expected_head:
        p.append("EVIDENCE_REGISTRY_HEAD_DIGEST_MISMATCH")
    if not _sha256(bundle.get("registry_digest")):
        p.append("EVIDENCE_REGISTRY_DIGEST_INVALID")
    elif bundle.get("registry_digest") != _sealed_digest(bundle, "registry_digest"):
        p.append("EVIDENCE_REGISTRY_DIGEST_MISMATCH")

    out = _result(p, "RAW_EVIDENCE_REGISTRY_VALID", "RAW_EVIDENCE_REGISTRY_INVALID")
    out["blocking_reasons"] = sorted(set(blocking))
    out["promotion_blocked"] = (not out["valid"]) or bool(blocking)
    out["expected_obligation_count"] = len(exp_set)
    out["recorded_obligation_count"] = len(by_obligation)
    return out


def evidence_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_RAW_EVIDENCE_AND_N_A_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
