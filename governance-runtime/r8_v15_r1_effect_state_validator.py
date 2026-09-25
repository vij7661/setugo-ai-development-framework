"""R8 v15-r1 Slice 8: local EffectStateRecord validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1
import r8_v15_r1_effect_intent_validator as slice7

EFFECT_STATE_RECORD_FIELDS: Tuple[str, ...] = (
    "effect_intent_id",
    "idempotency_key",
    "state",
    "executor_identity_digest",
    "reconciliation_evidence_digest",
    "state_record_digest",
)

EFFECT_STATES = {
    "INTENT_COMMITTED",
    "DISPATCHING",
    "ACKNOWLEDGED_UNVERIFIED",
    "SUCCEEDED_RECONCILED",
    "FAILED_FINAL",
    "UNCERTAIN",
    "COMPENSATION_REQUIRED",
    "COMPENSATED",
}


class EffectStateError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _meta() -> Dict[str, Any]:
    return {
        "authority_effect": "NONE",
        "effect_state_committed": False,
        "executor_qualified": False,
        "reconciliation_verified": False,
        "external_effect_succeeded": False,
        "compensation_authorized": False,
        "runtime_qualified": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "production_authorized": False,
        "policy_authorized": False,
        "terminal_authority": False,
    }


def _exact(obj: Mapping[str, Any]) -> None:
    if not isinstance(obj, Mapping):
        raise EffectStateError("EFFECT_STATE_FIELD_SET_INVALID", "record must be a mapping")
    actual=set(obj.keys()); expected=set(EFFECT_STATE_RECORD_FIELDS)
    if len(obj)!=len(EFFECT_STATE_RECORD_FIELDS) or actual!=expected:
        raise EffectStateError(
            "EFFECT_STATE_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )


def _string(value: Any, field: str) -> None:
    if not isinstance(value,str) or not value:
        raise EffectStateError("EFFECT_STATE_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise EffectStateError("EFFECT_STATE_GCP_STRING_INVALID",f"{field}: {exc}") from exc


def _nullable_string(value: Any, field: str) -> None:
    if value is None:
        return
    _string(value,field)


def validate_effect_state_record(
    record: Mapping[str, Any],
    *,
    effect_intent: Mapping[str, Any],
    decision_preseal: Mapping[str, Any],
    authority_read_set: Mapping[str, Any],
    qualified_time_proof: Mapping[str, Any],
    verified_state_seal: Mapping[str, Any],
    external_effect_involved: bool,
) -> Dict[str, Any]:
    _exact(record)

    _string(record["effect_intent_id"],"effect_intent_id")
    _string(record["idempotency_key"],"idempotency_key")
    _string(record["state_record_digest"],"state_record_digest")

    state=record["state"]
    if not isinstance(state,str) or state not in EFFECT_STATES:
        raise EffectStateError("EFFECT_STATE_STATE_INVALID","state is not a frozen EffectStateRecord state")

    _nullable_string(record["executor_identity_digest"],"executor_identity_digest")
    _nullable_string(record["reconciliation_evidence_digest"],"reconciliation_evidence_digest")

    if state=="SUCCEEDED_RECONCILED":
        if record["executor_identity_digest"] is None or record["reconciliation_evidence_digest"] is None:
            raise EffectStateError(
                "EFFECT_STATE_SUCCESS_EVIDENCE_REQUIRED",
                "SUCCEEDED_RECONCILED requires non-null executor and reconciliation evidence digests",
            )

    try:
        slice7.validate_effect_intent(
            effect_intent,
            decision_preseal=decision_preseal,
            authority_read_set=authority_read_set,
            qualified_time_proof=qualified_time_proof,
            verified_state_seal=verified_state_seal,
            external_effect_involved=external_effect_involved,
        )
    except slice7.EffectIntentError as exc:
        raise EffectStateError("EFFECT_STATE_INTENT_INVALID",str(exc)) from exc

    if record["effect_intent_id"] != effect_intent["effect_intent_id"]:
        raise EffectStateError("EFFECT_STATE_INTENT_ID_MISMATCH","effect_intent_id mismatch")
    if record["idempotency_key"] != effect_intent["idempotency_key"]:
        raise EffectStateError("EFFECT_STATE_IDEMPOTENCY_MISMATCH","idempotency_key mismatch")

    result={
        "locally_valid":True,
        "effect_intent_locally_valid":True,
        "effect_intent_id":record["effect_intent_id"],
        "idempotency_key":record["idempotency_key"],
        "state":state,
        "validation_scope":"LOCAL_EFFECT_STATE_STRUCTURE_AND_INTENT_BINDING_ONLY",
    }
    result.update(_meta())
    return result
