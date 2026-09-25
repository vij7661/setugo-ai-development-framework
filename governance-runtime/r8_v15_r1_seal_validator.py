"""R8 v15-r1 Implementation Slice 6: local VerifiedStateSeal binding validation.

This module validates only frozen local seal structure and deterministic equality against
supplied locally valid DecisionPresealContext, AuthorityReadSet, and QualifiedTimeProof
objects. It does not verify seal_digest, qualified time, current LAS heads/state,
STATE_CHANGED protection, COMMIT_WITH_SEAL, effect intent commit, or runtime authority.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1
import r8_v15_r1_preseal_validator as slice4
import r8_v15_r1_timeproof_validator as slice5

INT64_MAX = slice1.INT64_MAX

VERIFIED_STATE_SEAL_FIELDS: Tuple[str, ...] = (
    "decision_preseal_digest",
    "time_proof_digest",
    "authority_read_set_digest",
    "semantic_state_sequence",
    "semantic_heads",
    "revocation_head",
    "seal_digest",
)

_SEAL_DIGEST_FIELDS: Tuple[str, ...] = (
    "decision_preseal_digest",
    "time_proof_digest",
    "authority_read_set_digest",
    "revocation_head",
    "seal_digest",
)


class SealError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _metadata() -> Dict[str, Any]:
    return {
        "authority_effect": "NONE",
        "seal_digest_verified": False,
        "qualified_time_proven": False,
        "nonce_consumed": False,
        "current_heads_rechecked": False,
        "state_unchanged_at_commit": False,
        "current_revocation_proven": False,
        "current_runtime_workload_proven": False,
        "verified_state_seal_authoritative": False,
        "commit_with_seal_authorized": False,
        "effect_intent_committed": False,
        "runtime_qualified": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "production_authorized": False,
        "policy_authorized": False,
        "terminal_authority": False,
    }


def _require_exact_fields(
    value: Mapping[str, Any],
    fields: Tuple[str, ...],
    *,
    code: str,
    label: str,
) -> None:
    if not isinstance(value, Mapping):
        raise SealError(code, f"{label} must be a mapping")
    actual = set(value.keys())
    expected = set(fields)
    if len(value) != len(fields) or actual != expected:
        raise SealError(
            code,
            f"{label}: missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )


def _validate_gcp_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise SealError("SEAL_STRING_INVALID", f"{field} must be a non-empty string")
    encoded = json.dumps({"value": value}, ensure_ascii=True, separators=(",", ":"))
    try:
        slice1.canonicalize_json_text(encoded, schema_context="object")
    except slice1.GCPError as exc:
        raise SealError("SEAL_GCP_STRING_INVALID", f"{field}: {exc}") from exc


def _validate_sequence(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SealError("SEAL_SEQUENCE_INVALID", f"{field} must be a non-boolean integer")
    if value < 0 or value > INT64_MAX:
        raise SealError("SEAL_SEQUENCE_INVALID", f"{field} outside frozen Sequence range")


def _validate_semantic_heads(heads: Any) -> None:
    if not isinstance(heads, Mapping):
        raise SealError("SEAL_SEMANTIC_HEADS_INVALID", "semantic_heads must be a mapping")

    expected = set(slice4.SEMANTIC_HEAD_FIELDS)
    actual = set(heads.keys())
    if len(heads) != len(slice4.SEMANTIC_HEAD_FIELDS) or actual != expected:
        raise SealError(
            "SEAL_SEMANTIC_HEADS_INVALID",
            f"semantic_heads: missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )

    for field in slice4.SEMANTIC_HEAD_FIELDS:
        try:
            _validate_gcp_string(heads[field], f"semantic_heads.{field}")
        except SealError as exc:
            raise SealError("SEAL_SEMANTIC_HEADS_INVALID", str(exc)) from exc


def validate_verified_state_seal(
    seal: Mapping[str, Any],
    *,
    decision_preseal: Mapping[str, Any],
    authority_read_set: Mapping[str, Any],
    qualified_time_proof: Mapping[str, Any],
    external_effect_involved: bool,
) -> Dict[str, Any]:
    _require_exact_fields(
        seal,
        VERIFIED_STATE_SEAL_FIELDS,
        code="SEAL_FIELD_SET_INVALID",
        label="VerifiedStateSeal",
    )

    for field in _SEAL_DIGEST_FIELDS:
        _validate_gcp_string(seal[field], field)

    _validate_sequence(seal["semantic_state_sequence"], "semantic_state_sequence")
    _validate_semantic_heads(seal["semantic_heads"])

    try:
        slice4.validate_decision_preseal_context(
            decision_preseal,
            authority_read_set=authority_read_set,
            external_effect_involved=external_effect_involved,
        )
    except (slice4.PresealError, slice1.GCPError) as exc:
        raise SealError("SEAL_PRESEAL_INVALID", str(exc)) from exc

    try:
        slice5.validate_qualified_time_proof(
            qualified_time_proof,
            decision_preseal=decision_preseal,
            authority_read_set=authority_read_set,
            external_effect_involved=external_effect_involved,
        )
    except slice5.TimeProofError as exc:
        raise SealError("SEAL_TIME_PROOF_INVALID", str(exc)) from exc

    if seal["decision_preseal_digest"] != decision_preseal["decision_preseal_digest"]:
        raise SealError(
            "SEAL_PRESEAL_DIGEST_MISMATCH",
            "seal decision_preseal_digest does not equal supplied DecisionPresealContext digest",
        )

    if seal["time_proof_digest"] != qualified_time_proof["time_proof_digest"]:
        raise SealError(
            "SEAL_TIME_PROOF_DIGEST_MISMATCH",
            "seal time_proof_digest does not equal supplied QualifiedTimeProof digest",
        )

    if (
        seal["authority_read_set_digest"] != decision_preseal["authority_read_set_digest"]
        or seal["authority_read_set_digest"] != authority_read_set["authority_read_set_digest"]
    ):
        raise SealError(
            "SEAL_AUTHORITY_READ_SET_DIGEST_MISMATCH",
            "seal authority_read_set_digest is not identical across seal/preseal/read-set",
        )

    if seal["semantic_state_sequence"] != decision_preseal["semantic_state_sequence"]:
        raise SealError(
            "SEAL_SEMANTIC_SEQUENCE_MISMATCH",
            "seal semantic_state_sequence does not equal DecisionPresealContext sequence",
        )

    if qualified_time_proof["effective_sequence"] != decision_preseal["semantic_state_sequence"]:
        raise SealError(
            "SEAL_TIME_SEQUENCE_MISMATCH",
            "QualifiedTimeProof effective_sequence does not equal DecisionPresealContext semantic_state_sequence",
        )

    if dict(seal["semantic_heads"]) != dict(decision_preseal["semantic_heads"]):
        raise SealError(
            "SEAL_SEMANTIC_HEADS_MISMATCH",
            "seal semantic_heads do not exactly equal DecisionPresealContext semantic_heads",
        )

    if (
        seal["revocation_head"] != seal["semantic_heads"]["revocation_head"]
        or seal["revocation_head"] != decision_preseal["semantic_heads"]["revocation_head"]
    ):
        raise SealError(
            "SEAL_REVOCATION_HEAD_MISMATCH",
            "standalone seal revocation_head does not equal bound SemanticHeads revocation_head",
        )

    result: Dict[str, Any] = {
        "locally_valid": True,
        "preseal_locally_valid": True,
        "time_proof_locally_valid": True,
        "decision_preseal_digest": seal["decision_preseal_digest"],
        "time_proof_digest": seal["time_proof_digest"],
        "authority_read_set_digest": seal["authority_read_set_digest"],
        "semantic_state_sequence": seal["semantic_state_sequence"],
        "validation_scope": "LOCAL_SEAL_STRUCTURE_AND_CROSS_OBJECT_BINDING_ONLY",
    }
    result.update(_metadata())
    return result
