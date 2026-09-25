"""R8 v15-r1 Implementation Slice 5: local QualifiedTimeProof validation.

This module validates only frozen local structure and the explicit binding to a supplied
locally valid DecisionPresealContext digest. It does not establish nonce consumption,
source status, source independence, freshness, attestation signature validity,
time-proof digest correctness, seal validity, or runtime authority.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1
import r8_v15_r1_preseal_validator as slice4

INT64_MAX = slice1.INT64_MAX

TIME_SOURCE_ATTESTATION_FIELDS: Tuple[str, ...] = (
    "time_source_id",
    "source_status_digest",
    "attestation_digest",
)

QUALIFIED_TIME_PROOF_FIELDS: Tuple[str, ...] = (
    "nonce_256bit_hex",
    "decision_preseal_digest",
    "effective_sequence",
    "source_attestations",
    "time_proof_digest",
)

_NONCE_RE = re.compile(r"[0-9A-Fa-f]{64}\Z")


class TimeProofError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _metadata() -> Dict[str, Any]:
    return {
        "authority_effect": "NONE",
        "runtime_qualified": False,
        "nonce_consumed": False,
        "source_status_valid": False,
        "source_independence_proven": False,
        "freshness_proven": False,
        "signature_verified": False,
        "time_proof_digest_verified": False,
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
        raise TimeProofError(code, f"{label} must be a mapping")
    actual = set(value.keys())
    expected = set(fields)
    if len(value) != len(fields) or actual != expected:
        raise TimeProofError(
            code,
            f"{label}: missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )


def _validate_gcp_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise TimeProofError(
            "TIME_PROOF_STRING_INVALID",
            f"{field} must be a non-empty string",
        )
    encoded = json.dumps({"value": value}, ensure_ascii=True, separators=(",", ":"))
    try:
        slice1.canonicalize_json_text(encoded, schema_context="object")
    except slice1.GCPError as exc:
        raise TimeProofError(
            "TIME_PROOF_GCP_STRING_INVALID",
            f"{field}: {exc}",
        ) from exc


def _validate_sequence(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TimeProofError(
            "TIME_PROOF_SEQUENCE_INVALID",
            f"{field} must be a non-boolean integer",
        )
    if value < 0 or value > INT64_MAX:
        raise TimeProofError(
            "TIME_PROOF_SEQUENCE_INVALID",
            f"{field} outside frozen Sequence range",
        )


def validate_time_source_attestation(attestation: Mapping[str, Any]) -> Dict[str, Any]:
    _require_exact_fields(
        attestation,
        TIME_SOURCE_ATTESTATION_FIELDS,
        code="TIME_SOURCE_ATTESTATION_FIELD_SET_INVALID",
        label="TimeSourceAttestation",
    )
    for field in TIME_SOURCE_ATTESTATION_FIELDS:
        _validate_gcp_string(attestation[field], field)

    result: Dict[str, Any] = {
        "locally_valid": True,
        "time_source_id": attestation["time_source_id"],
        "source_status_valid": False,
        "signature_verified": False,
        "validation_scope": "LOCAL_STRUCTURE_ONLY",
    }
    result.update(_metadata())
    return result


def validate_qualified_time_proof(
    proof: Mapping[str, Any],
    *,
    decision_preseal: Mapping[str, Any],
    authority_read_set: Mapping[str, Any],
    external_effect_involved: bool,
) -> Dict[str, Any]:
    _require_exact_fields(
        proof,
        QUALIFIED_TIME_PROOF_FIELDS,
        code="TIME_PROOF_FIELD_SET_INVALID",
        label="QualifiedTimeProof",
    )

    nonce = proof["nonce_256bit_hex"]
    if not isinstance(nonce, str) or _NONCE_RE.fullmatch(nonce) is None:
        raise TimeProofError(
            "TIME_PROOF_NONCE_INVALID",
            "nonce_256bit_hex must be exactly 64 ASCII hex characters",
        )

    _validate_gcp_string(proof["decision_preseal_digest"], "decision_preseal_digest")
    _validate_sequence(proof["effective_sequence"], "effective_sequence")
    _validate_gcp_string(proof["time_proof_digest"], "time_proof_digest")

    attestations = proof["source_attestations"]
    if not isinstance(attestations, list) or not (2 <= len(attestations) <= 3):
        raise TimeProofError(
            "TIME_PROOF_ATTESTATIONS_INVALID",
            "source_attestations must be a JSON-array-equivalent Python list of length 2..3",
        )
    for attestation in attestations:
        validate_time_source_attestation(attestation)

    try:
        slice4.validate_decision_preseal_context(
            decision_preseal,
            authority_read_set=authority_read_set,
            external_effect_involved=external_effect_involved,
        )
    except (slice4.PresealError, slice1.GCPError) as exc:
        raise TimeProofError(
            "TIME_PROOF_PRESEAL_INVALID",
            str(exc),
        ) from exc

    if proof["decision_preseal_digest"] != decision_preseal["decision_preseal_digest"]:
        raise TimeProofError(
            "TIME_PROOF_PRESEAL_DIGEST_MISMATCH",
            "QualifiedTimeProof decision_preseal_digest does not equal supplied DecisionPresealContext digest",
        )

    result: Dict[str, Any] = {
        "locally_valid": True,
        "decision_preseal_locally_valid": True,
        "decision_preseal_digest": proof["decision_preseal_digest"],
        "effective_sequence": proof["effective_sequence"],
        "source_attestation_count": len(attestations),
        "validation_scope": "LOCAL_STRUCTURE_AND_PRESEAL_DIGEST_BINDING_ONLY",
    }
    result.update(_metadata())
    return result
