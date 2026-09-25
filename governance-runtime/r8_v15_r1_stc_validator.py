"""R8 v15-r1 Implementation Slice 3: local StateTransferCertificate validation.

This module validates only the frozen local STC structure and deterministic cross-field
consistency. It does not validate ROTATION_PREPARE authority, quorum, barrier currentness,
STC_COMMIT uniqueness, or runtime qualification.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1
import r8_v15_r1_state_roots as slice2

INT64_MAX = slice1.INT64_MAX

STC_REQUIRED_FIELDS: Tuple[str, ...] = (
    "system_id",
    "rotation_id",
    "transition_id",
    "rotation_prepare_certificate_digest",
    "old_configuration_generation",
    "old_configuration_digest",
    "proposed_new_configuration_digest",
    "barrier_snapshot_index",
    "committed_log_prefix_digest",
    "highest_seen_term",
    "highest_committed_index",
    "highest_applied_index",
    "last_committed_entry_digest",
    "state_root_digest",
    "stream_head_map_root_digest",
    "idempotency_dedup_ledger_root_digest",
    "prior_certificate_chain_digest",
    "ggs_namespace_root_digest",
    "ggs_authorization_root_digest",
    "semantic_state_binding_required",
    "semantic_heads",
    "ggs_genesis_state_root",
    "stc_digest",
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

_SEQUENCE_FIELDS = (
    "old_configuration_generation",
    "barrier_snapshot_index",
    "highest_seen_term",
    "highest_committed_index",
)

_NONEMPTY_STRING_FIELDS = (
    "rotation_id",
    "transition_id",
    "rotation_prepare_certificate_digest",
    "old_configuration_digest",
    "proposed_new_configuration_digest",
    "committed_log_prefix_digest",
    "last_committed_entry_digest",
    "idempotency_dedup_ledger_root_digest",
    "prior_certificate_chain_digest",
    "stc_digest",
)

_LOWER_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class STCError(ValueError):
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


def _require_exact_fields(value: Mapping[str, Any], fields: Tuple[str, ...], code: str, label: str) -> None:
    if not isinstance(value, Mapping):
        raise STCError(code, f"{label} must be a mapping")
    actual = set(value.keys())
    expected = set(fields)
    if len(value) != len(fields) or actual != expected:
        raise STCError(
            code,
            f"{label}: missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )


def _validate_sequence(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise STCError("STC_SEQUENCE_INVALID", f"{field} must be a non-boolean integer")
    if value < 0 or value > INT64_MAX:
        raise STCError("STC_SEQUENCE_INVALID", f"{field} outside frozen Sequence range")


def _validate_gcp_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise STCError("STC_STRING_INVALID", f"{field} must be a non-empty string")
    encoded = json.dumps({"value": value}, ensure_ascii=True, separators=(",", ":"))
    slice1.canonicalize_json_text(encoded, schema_context="object")


def _validate_nullable_gcp_string(value: Any, field: str) -> None:
    if value is None:
        return
    _validate_gcp_string(value, field)


def _validate_root_digest(value: Any) -> None:
    if not isinstance(value, str) or _LOWER_SHA256_RE.fullmatch(value) is None:
        raise STCError(
            "STC_ROOT_DIGEST_ENCODING_INVALID",
            "state_root_digest must be lowercase 64-hex SHA-256",
        )


def _validate_semantic_heads(heads: Any) -> None:
    _require_exact_fields(heads, SEMANTIC_HEAD_FIELDS, "SEMANTIC_HEADS_INVALID", "semantic_heads")
    for field in SEMANTIC_HEAD_FIELDS:
        _validate_gcp_string(heads[field], f"semantic_heads.{field}")


def _validate_common(stc: Mapping[str, Any]) -> None:
    _require_exact_fields(stc, STC_REQUIRED_FIELDS, "STC_FIELD_SET_INVALID", "StateTransferCertificate")

    if stc["system_id"] not in ("LAS-3", "GGS-3"):
        raise STCError("STC_SYSTEM_ID_INVALID", repr(stc["system_id"]))

    for field in _SEQUENCE_FIELDS:
        _validate_sequence(stc[field], field)

    if stc["highest_applied_index"] is not None:
        _validate_sequence(stc["highest_applied_index"], "highest_applied_index")

    if not isinstance(stc["semantic_state_binding_required"], bool):
        raise STCError(
            "STC_BOOLEAN_INVALID",
            "semantic_state_binding_required must be boolean",
        )

    for field in _NONEMPTY_STRING_FIELDS:
        _validate_gcp_string(stc[field], field)

    _validate_root_digest(stc["state_root_digest"])

    for field in (
        "stream_head_map_root_digest",
        "ggs_namespace_root_digest",
        "ggs_authorization_root_digest",
    ):
        _validate_nullable_gcp_string(stc[field], field)

    # Validate every present semantic-head value through the inherited GCP rules.
    if stc["semantic_heads"] is not None:
        _validate_semantic_heads(stc["semantic_heads"])


def _validate_las(stc: Mapping[str, Any]) -> None:
    if stc["semantic_state_binding_required"] is not True:
        raise STCError("STC_CONDITIONAL_INVALID", "LAS-3 requires semantic_state_binding_required=true")
    if stc["semantic_heads"] is None:
        raise STCError("STC_CONDITIONAL_INVALID", "LAS-3 requires semantic_heads")
    if stc["stream_head_map_root_digest"] is None:
        raise STCError("STC_CONDITIONAL_INVALID", "LAS-3 requires stream_head_map_root_digest")
    if stc["ggs_namespace_root_digest"] is not None:
        raise STCError("STC_CONDITIONAL_INVALID", "LAS-3 requires null ggs_namespace_root_digest")
    if stc["ggs_authorization_root_digest"] is not None:
        raise STCError("STC_CONDITIONAL_INVALID", "LAS-3 requires null ggs_authorization_root_digest")
    if stc["ggs_genesis_state_root"] is not None:
        raise STCError("STC_CONDITIONAL_INVALID", "LAS-3 requires null ggs_genesis_state_root")


def _validate_ggs(stc: Mapping[str, Any]) -> None:
    if stc["stream_head_map_root_digest"] is not None:
        raise STCError("STC_CONDITIONAL_INVALID", "GGS-3 requires null stream_head_map_root_digest")
    if stc["ggs_namespace_root_digest"] is None:
        raise STCError("STC_CONDITIONAL_INVALID", "GGS-3 requires ggs_namespace_root_digest")
    if stc["ggs_authorization_root_digest"] is None:
        raise STCError("STC_CONDITIONAL_INVALID", "GGS-3 requires ggs_authorization_root_digest")

    if stc["semantic_state_binding_required"]:
        if stc["semantic_heads"] is None:
            raise STCError("STC_CONDITIONAL_INVALID", "GGS semantic binding requires semantic_heads")
    else:
        if stc["semantic_heads"] is not None:
            raise STCError("STC_CONDITIONAL_INVALID", "GGS without semantic binding requires semantic_heads=null")

    root = stc["ggs_genesis_state_root"]
    if not isinstance(root, Mapping):
        raise STCError("STC_CONDITIONAL_INVALID", "GGS-3 requires ggs_genesis_state_root")

    try:
        slice2.verify_ggs_genesis_state_root(root)
    except slice2.StateRootError as exc:
        raise STCError("STC_GGS_ROOT_INVALID", str(exc)) from exc

    mappings = (
        ("barrier_index", "barrier_snapshot_index"),
        ("committed_log_prefix_digest", "committed_log_prefix_digest"),
        ("constitution_namespace_root", "ggs_namespace_root_digest"),
        ("bootstrap_authorization_root", "ggs_authorization_root_digest"),
        ("idempotency_ledger_root", "idempotency_dedup_ledger_root_digest"),
        ("configuration_generation", "old_configuration_generation"),
        ("prior_certificate_chain_digest", "prior_certificate_chain_digest"),
        ("state_root_digest", "state_root_digest"),
    )
    for root_field, stc_field in mappings:
        if root[root_field] != stc[stc_field]:
            raise STCError(
                "STC_GGS_ROOT_MISMATCH",
                f"ggs_genesis_state_root.{root_field} != {stc_field}",
            )


def validate_state_transfer_certificate(stc: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate local frozen STC shape/cross-field consistency only."""
    _validate_common(stc)

    if stc["system_id"] == "LAS-3":
        _validate_las(stc)
    else:
        _validate_ggs(stc)

    result: Dict[str, Any] = {
        "locally_valid": True,
        "system_id": stc["system_id"],
        "semantic_state_binding_required": stc["semantic_state_binding_required"],
        "validation_scope": "LOCAL_STRUCTURE_AND_CROSS_FIELD_CONSISTENCY_ONLY",
    }
    result.update(_metadata())
    return result
