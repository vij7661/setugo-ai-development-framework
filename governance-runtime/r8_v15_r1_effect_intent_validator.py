"""R8 v15-r1 Implementation Slice 7: local EffectIntent binding validation.

This module validates only frozen local EffectIntent structure and deterministic equality
against supplied locally valid DecisionPresealContext, AuthorityReadSet, QualifiedTimeProof,
and VerifiedStateSeal objects. It does not perform COMMIT_WITH_SEAL, append an intent,
authorize dispatch, contact a provider, reconcile an effect, or prove external success.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1
import r8_v15_r1_preseal_validator as slice4
import r8_v15_r1_timeproof_validator as slice5
import r8_v15_r1_seal_validator as slice6

EFFECT_INTENT_FIELDS: Tuple[str, ...] = (
    "effect_intent_id",
    "idempotency_key",
    "verified_state_seal_digest",
    "decision_preseal_digest",
    "effect_class",
    "payload_digest",
    "provider_id",
    "action",
    "candidate_scope_digest",
    "action_scope_digest",
    "tenant_scope_digest",
    "state",
)

_STRING_FIELDS: Tuple[str, ...] = (
    "effect_intent_id",
    "idempotency_key",
    "verified_state_seal_digest",
    "decision_preseal_digest",
    "effect_class",
    "payload_digest",
    "provider_id",
    "action",
    "candidate_scope_digest",
    "action_scope_digest",
    "tenant_scope_digest",
)


class EffectIntentError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _metadata() -> Dict[str, Any]:
    return {
        "authority_effect": "NONE",
        "effect_intent_committed": False,
        "commit_with_seal_authorized": False,
        "current_heads_rechecked": False,
        "state_unchanged_at_commit": False,
        "idempotency_key_derivation_verified": False,
        "payload_digest_verified": False,
        "provider_action_authorized": False,
        "scope_digests_verified": False,
        "executor_qualified": False,
        "dispatch_authorized": False,
        "external_effect_succeeded": False,
        "reconciliation_complete": False,
        "runtime_qualified": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "production_authorized": False,
        "policy_authorized": False,
        "terminal_authority": False,
    }


def _require_exact_fields(value: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping):
        raise EffectIntentError(
            "EFFECT_INTENT_FIELD_SET_INVALID",
            "EffectIntent must be a mapping",
        )
    actual = set(value.keys())
    expected = set(EFFECT_INTENT_FIELDS)
    if len(value) != len(EFFECT_INTENT_FIELDS) or actual != expected:
        raise EffectIntentError(
            "EFFECT_INTENT_FIELD_SET_INVALID",
            f"EffectIntent: missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )


def _validate_gcp_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise EffectIntentError(
            "EFFECT_INTENT_STRING_INVALID",
            f"{field} must be a non-empty string",
        )
    encoded = json.dumps({"value": value}, ensure_ascii=True, separators=(",", ":"))
    try:
        slice1.canonicalize_json_text(encoded, schema_context="object")
    except slice1.GCPError as exc:
        raise EffectIntentError(
            "EFFECT_INTENT_GCP_STRING_INVALID",
            f"{field}: {exc}",
        ) from exc


def validate_effect_intent(
    effect_intent: Mapping[str, Any],
    *,
    decision_preseal: Mapping[str, Any],
    authority_read_set: Mapping[str, Any],
    qualified_time_proof: Mapping[str, Any],
    verified_state_seal: Mapping[str, Any],
    external_effect_involved: bool,
) -> Dict[str, Any]:
    _require_exact_fields(effect_intent)

    if not isinstance(external_effect_involved, bool):
        raise EffectIntentError(
            "EFFECT_INTENT_EFFECT_CONTEXT_INVALID",
            "external_effect_involved must be a verifier-owned boolean",
        )
    if not external_effect_involved:
        raise EffectIntentError(
            "EFFECT_INTENT_EXTERNAL_EFFECT_REQUIRED",
            "EffectIntent local validation requires external_effect_involved=true",
        )

    for field in _STRING_FIELDS:
        _validate_gcp_string(effect_intent[field], field)

    if effect_intent["state"] != "INTENT_COMMITTED":
        raise EffectIntentError(
            "EFFECT_INTENT_STATE_INVALID",
            "EffectIntent.state must be exactly INTENT_COMMITTED",
        )

    try:
        slice4.validate_decision_preseal_context(
            decision_preseal,
            authority_read_set=authority_read_set,
            external_effect_involved=external_effect_involved,
        )
    except (slice4.PresealError, slice1.GCPError) as exc:
        raise EffectIntentError(
            "EFFECT_INTENT_PRESEAL_INVALID",
            str(exc),
        ) from exc

    try:
        slice5.validate_qualified_time_proof(
            qualified_time_proof,
            decision_preseal=decision_preseal,
            authority_read_set=authority_read_set,
            external_effect_involved=external_effect_involved,
        )
    except slice5.TimeProofError as exc:
        raise EffectIntentError(
            "EFFECT_INTENT_TIME_PROOF_INVALID",
            str(exc),
        ) from exc

    try:
        slice6.validate_verified_state_seal(
            verified_state_seal,
            decision_preseal=decision_preseal,
            authority_read_set=authority_read_set,
            qualified_time_proof=qualified_time_proof,
            external_effect_involved=external_effect_involved,
        )
    except slice6.SealError as exc:
        raise EffectIntentError(
            "EFFECT_INTENT_SEAL_INVALID",
            str(exc),
        ) from exc

    if effect_intent["verified_state_seal_digest"] != verified_state_seal["seal_digest"]:
        raise EffectIntentError(
            "EFFECT_INTENT_SEAL_DIGEST_MISMATCH",
            "verified_state_seal_digest does not equal supplied VerifiedStateSeal seal_digest",
        )

    if effect_intent["decision_preseal_digest"] != decision_preseal["decision_preseal_digest"]:
        raise EffectIntentError(
            "EFFECT_INTENT_PRESEAL_DIGEST_MISMATCH",
            "decision_preseal_digest does not equal supplied DecisionPresealContext digest",
        )

    if effect_intent["effect_class"] != decision_preseal["effect_class"]:
        raise EffectIntentError(
            "EFFECT_INTENT_EFFECT_CLASS_MISMATCH",
            "EffectIntent effect_class does not equal supplied DecisionPresealContext effect_class",
        )

    result: Dict[str, Any] = {
        "locally_valid": True,
        "preseal_locally_valid": True,
        "time_proof_locally_valid": True,
        "seal_locally_valid": True,
        "effect_intent_id": effect_intent["effect_intent_id"],
        "verified_state_seal_digest": effect_intent["verified_state_seal_digest"],
        "decision_preseal_digest": effect_intent["decision_preseal_digest"],
        "effect_class": effect_intent["effect_class"],
        "state": effect_intent["state"],
        "validation_scope": "LOCAL_EFFECT_INTENT_STRUCTURE_AND_BINDING_ONLY",
    }
    result.update(_metadata())
    return result
