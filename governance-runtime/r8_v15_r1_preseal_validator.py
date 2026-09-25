"""R8 v15-r1 Implementation Slice 4: local AuthorityReadSet / DecisionPresealContext validation.

This module validates only frozen local structure and deterministic cross-field equality.
It deliberately does not recompute authority_read_set_digest or decision_preseal_digest and
does not establish read-set completeness, currentness, resolver qualification, time/seal
validity, or any downstream authority.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence as SequenceABC
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX = slice1.INT64_MAX

AUTHORITY_READ_SET_ENTRY_FIELDS: Tuple[str, ...] = (
    "input_id",
    "source_id",
    "head_digest",
    "value_digest",
    "schema_semantic_entry_digest",
)

AUTHORITY_READ_SET_FIELDS: Tuple[str, ...] = (
    "entries",
    "authority_read_set_digest",
)

DECISION_PRESEAL_FIELDS: Tuple[str, ...] = (
    "candidate_id",
    "action_id",
    "decision_scope_digest",
    "governance_snapshot_digest",
    "authority_read_set_digest",
    "semantic_state_sequence",
    "semantic_heads",
    "rir_record_id",
    "rir_head_digest",
    "resolver_identity",
    "revocation_state_digest",
    "runtime_state_digest",
    "workload_state_digest",
    "effect_class",
    "decision_preseal_digest",
)

SEMANTIC_HEAD_FIELDS: Tuple[str, ...] = (
    "csm_head",
    "aim_head",
    "semantic_any_permission_head",
    "aim_scope_policy_head",
    "resolver_policy_head",
    "resolver_implementation_registry_head",
    "guard_registry_head",
    "revocation_head",
    "nonce_ledger_head",
    "effect_stream_head",
    "configuration_head",
)

RESOLVER_IDENTITY_FIELDS: Tuple[str, ...] = (
    "resolver_policy_digest",
    "implementation_id",
    "runtime_identity_digest",
    "workload_identity_digest",
    "conformance_suite_digest",
    "conformance_evidence_digest",
)

_PRESEAL_STRING_FIELDS: Tuple[str, ...] = (
    "candidate_id",
    "action_id",
    "decision_scope_digest",
    "governance_snapshot_digest",
    "authority_read_set_digest",
    "rir_record_id",
    "rir_head_digest",
    "revocation_state_digest",
    "runtime_state_digest",
    "workload_state_digest",
    "decision_preseal_digest",
)


class PresealError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _metadata() -> Dict[str, Any]:
    return {
        "authority_effect": "NONE",
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
        raise PresealError(code, f"{label} must be a mapping")
    actual = set(value.keys())
    expected = set(fields)
    if len(value) != len(fields) or actual != expected:
        raise PresealError(
            code,
            f"{label}: missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )


def _validate_gcp_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise PresealError("PRESEAL_STRING_INVALID", f"{field} must be a non-empty string")
    encoded = json.dumps({"value": value}, ensure_ascii=True, separators=(",", ":"))
    slice1.canonicalize_json_text(encoded, schema_context="object")


def _validate_sequence(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PresealError("PRESEAL_SEQUENCE_INVALID", f"{field} must be a non-boolean integer")
    if value < 0 or value > INT64_MAX:
        raise PresealError("PRESEAL_SEQUENCE_INVALID", f"{field} outside frozen Sequence range")


def _validate_semantic_heads(heads: Any) -> None:
    _require_exact_fields(
        heads,
        SEMANTIC_HEAD_FIELDS,
        code="PRESEAL_SEMANTIC_HEADS_INVALID",
        label="semantic_heads",
    )
    for field in SEMANTIC_HEAD_FIELDS:
        _validate_gcp_string(heads[field], f"semantic_heads.{field}")


def _validate_resolver_identity(identity: Any) -> None:
    _require_exact_fields(
        identity,
        RESOLVER_IDENTITY_FIELDS,
        code="PRESEAL_RESOLVER_IDENTITY_INVALID",
        label="resolver_identity",
    )
    for field in RESOLVER_IDENTITY_FIELDS:
        _validate_gcp_string(identity[field], f"resolver_identity.{field}")


def _validate_authority_read_set_entry(entry: Any, index: int) -> None:
    _require_exact_fields(
        entry,
        AUTHORITY_READ_SET_ENTRY_FIELDS,
        code="ARS_ENTRY_FIELD_SET_INVALID",
        label=f"AuthorityReadSet.entries[{index}]",
    )
    for field in AUTHORITY_READ_SET_ENTRY_FIELDS:
        _validate_gcp_string(entry[field], f"entries[{index}].{field}")


def validate_authority_read_set(read_set: Mapping[str, Any]) -> Dict[str, Any]:
    _require_exact_fields(
        read_set,
        AUTHORITY_READ_SET_FIELDS,
        code="ARS_FIELD_SET_INVALID",
        label="AuthorityReadSet",
    )

    entries = read_set["entries"]
    if (
        not isinstance(entries, SequenceABC)
        or isinstance(entries, (str, bytes, bytearray))
        or len(entries) < 1
    ):
        raise PresealError("ARS_ENTRIES_INVALID", "entries must be a non-empty array")

    for index, entry in enumerate(entries):
        _validate_authority_read_set_entry(entry, index)

    _validate_gcp_string(read_set["authority_read_set_digest"], "authority_read_set_digest")

    result: Dict[str, Any] = {
        "locally_valid": True,
        "entry_count": len(entries),
        "authority_read_set_digest": read_set["authority_read_set_digest"],
        "read_set_completeness_proven": False,
        "authority_read_set_digest_verified": False,
        "validation_scope": "LOCAL_STRUCTURE_ONLY",
    }
    result.update(_metadata())
    return result


def validate_decision_preseal_context(
    decision_preseal: Mapping[str, Any],
    *,
    authority_read_set: Mapping[str, Any],
    external_effect_involved: bool,
) -> Dict[str, Any]:
    _require_exact_fields(
        decision_preseal,
        DECISION_PRESEAL_FIELDS,
        code="PRESEAL_FIELD_SET_INVALID",
        label="DecisionPresealContext",
    )

    if not isinstance(external_effect_involved, bool):
        raise PresealError(
            "PRESEAL_EFFECT_CONTEXT_INVALID",
            "external_effect_involved must be verifier-owned boolean context",
        )

    for field in _PRESEAL_STRING_FIELDS:
        _validate_gcp_string(decision_preseal[field], field)

    _validate_sequence(
        decision_preseal["semantic_state_sequence"],
        "semantic_state_sequence",
    )
    _validate_semantic_heads(decision_preseal["semantic_heads"])
    _validate_resolver_identity(decision_preseal["resolver_identity"])

    effect_class = decision_preseal["effect_class"]
    if external_effect_involved:
        if not isinstance(effect_class, str) or not effect_class:
            raise PresealError(
                "PRESEAL_EFFECT_CLASS_INVALID",
                "external effect requires a non-empty effect_class",
            )
        _validate_gcp_string(effect_class, "effect_class")
    else:
        if effect_class is not None:
            raise PresealError(
                "PRESEAL_EFFECT_CLASS_INVALID",
                "no external effect requires effect_class=null",
            )

    read_set_result = validate_authority_read_set(authority_read_set)
    if (
        decision_preseal["authority_read_set_digest"]
        != authority_read_set["authority_read_set_digest"]
    ):
        raise PresealError(
            "PRESEAL_AUTHORITY_READ_SET_DIGEST_MISMATCH",
            "DecisionPresealContext authority_read_set_digest does not equal supplied AuthorityReadSet digest",
        )

    result: Dict[str, Any] = {
        "locally_valid": True,
        "semantic_state_sequence": decision_preseal["semantic_state_sequence"],
        "external_effect_involved": external_effect_involved,
        "authority_read_set_entry_count": read_set_result["entry_count"],
        "authority_read_set_digest": authority_read_set["authority_read_set_digest"],
        "read_set_completeness_proven": False,
        "authority_read_set_digest_verified": False,
        "decision_preseal_digest_verified": False,
        "resolver_qualified": False,
        "currentness_proven": False,
        "validation_scope": "LOCAL_STRUCTURE_AND_SUPPLIED_DIGEST_EQUALITY_ONLY",
    }
    result.update(_metadata())
    return result
