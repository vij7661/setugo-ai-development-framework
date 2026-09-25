"""R8 v15-r1 Implementation Slice 2: deterministic LAS/GGS state-root construction.

This module is deliberately non-authoritative. It constructs and verifies only the
frozen digest formulas for LASAuthorityStateRoot and GGSGenesisStateRoot. It does not
prove currentness, sequencing, barrier certification, quorum, runtime qualification,
or any downstream authority.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX = slice1.INT64_MAX

LAS_PREIMAGE_MEMBERS: Tuple[str, ...] = (
    "semantic_state_sequence",
    "committed_log_prefix_digest",
    "stream_head_map_root",
    "idempotency_ledger_root",
    "authority_state_machine_root",
    "revocation_stream_head",
    "nonce_ledger_head",
    "effect_stream_head",
    "csm5_registry_head",
    "aim4_descriptor_head",
    "any_scope_permission_head",
    "aim_scope_policy_head",
    "resolver_policy_head",
    "resolver_implementation_registry_head",
    "guard_registry_head",
    "configuration_generation",
    "prior_certificate_chain_digest",
)

GGS_PREIMAGE_MEMBERS: Tuple[str, ...] = (
    "barrier_index",
    "committed_log_prefix_digest",
    "constitution_namespace_root",
    "bootstrap_authorization_root",
    "idempotency_ledger_root",
    "configuration_generation",
    "prior_certificate_chain_digest",
)

LAS_SEQUENCE_MEMBERS = frozenset(
    {"semantic_state_sequence", "configuration_generation"}
)
GGS_SEQUENCE_MEMBERS = frozenset({"barrier_index", "configuration_generation"})

_LOWER_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class StateRootError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _result_metadata() -> Dict[str, Any]:
    return {
        "authority_effect": "NONE",
        "runtime_qualified": False,
        "release_authorized": False,
        "deployment_authorized": False,
        "production_authorized": False,
        "policy_authorized": False,
        "terminal_authority": False,
    }


def _validate_exact_members(
    data: Mapping[str, Any],
    members: Tuple[str, ...],
    *,
    label: str,
) -> None:
    if not isinstance(data, Mapping):
        raise StateRootError(
            "ROOT_MEMBER_SET_INVALID",
            f"{label} must be a mapping",
        )

    actual = set(data.keys())
    expected = set(members)
    if len(data) != len(members) or actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise StateRootError(
            "ROOT_MEMBER_SET_INVALID",
            f"{label}: missing={missing} extra={extra}",
        )


def _validate_sequence(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise StateRootError(
            "ROOT_SEQUENCE_INVALID",
            f"{field} must be a non-boolean integer",
        )
    if value < 0 or value > INT64_MAX:
        raise StateRootError(
            "ROOT_SEQUENCE_INVALID",
            f"{field} outside frozen Sequence range",
        )


def _validate_component_digest(value: Any, field: str) -> None:
    # Generic frozen Digest is intentionally opaque. Do not impose a global SHA-256
    # lexical form here; require only the schema's non-empty-string shape. The GCP
    # canonicalizer later enforces frozen authority-string Unicode/NFC constraints.
    if not isinstance(value, str) or not value:
        raise StateRootError(
            "ROOT_COMPONENT_DIGEST_INVALID",
            f"{field} must be a non-empty string",
        )


def _validate_preimage_values(
    data: Mapping[str, Any],
    members: Tuple[str, ...],
    sequence_members: frozenset[str],
    *,
    label: str,
) -> None:
    _validate_exact_members(data, members, label=label)
    for field in members:
        value = data[field]
        if field in sequence_members:
            _validate_sequence(value, field)
        else:
            _validate_component_digest(value, field)


def _canonicalize_preimage(data: Mapping[str, Any]) -> bytes:
    # json.dumps is only a transport into the already-closed Slice 1 GCP parser.
    # ensure_ascii=True preserves every Python string losslessly as JSON escape
    # sequences, allowing Slice 1 to perform the authoritative NFC/noncharacter/
    # surrogate checks and canonical re-encoding.
    text = json.dumps(
        dict(data),
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=False,
    )
    return slice1.canonicalize_json_text(text, schema_context="object")


def _compute(
    data: Mapping[str, Any],
    members: Tuple[str, ...],
    sequence_members: frozenset[str],
    *,
    root_type: str,
) -> Dict[str, Any]:
    _validate_preimage_values(
        data,
        members,
        sequence_members,
        label=f"{root_type} preimage",
    )
    canonical = _canonicalize_preimage(data)
    digest = hashlib.sha256(canonical).hexdigest()

    root = {member: data[member] for member in members}
    root["state_root_digest"] = digest

    result: Dict[str, Any] = {
        "root_type": root_type,
        "root": root,
        "canonical_preimage_utf8": canonical,
        "state_root_digest": digest,
    }
    result.update(_result_metadata())
    return result


def compute_las_authority_state_root(preimage: Mapping[str, Any]) -> Dict[str, Any]:
    return _compute(
        preimage,
        LAS_PREIMAGE_MEMBERS,
        LAS_SEQUENCE_MEMBERS,
        root_type="LASAuthorityStateRoot",
    )


def compute_ggs_genesis_state_root(preimage: Mapping[str, Any]) -> Dict[str, Any]:
    return _compute(
        preimage,
        GGS_PREIMAGE_MEMBERS,
        GGS_SEQUENCE_MEMBERS,
        root_type="GGSGenesisStateRoot",
    )


def _verify(
    root: Mapping[str, Any],
    members: Tuple[str, ...],
    sequence_members: frozenset[str],
    *,
    root_type: str,
) -> Dict[str, Any]:
    full_members = members + ("state_root_digest",)
    _validate_exact_members(root, full_members, label=f"{root_type} root")

    supplied = root["state_root_digest"]
    if not isinstance(supplied, str) or _LOWER_SHA256_RE.fullmatch(supplied) is None:
        raise StateRootError(
            "ROOT_DIGEST_ENCODING_INVALID",
            "state_root_digest must be lowercase 64-hex SHA-256",
        )

    preimage = {member: root[member] for member in members}
    computed = _compute(
        preimage,
        members,
        sequence_members,
        root_type=root_type,
    )
    observed = computed["state_root_digest"]

    if not hmac.compare_digest(supplied, observed):
        raise StateRootError(
            "STATE_ROOT_DIGEST_MISMATCH",
            f"expected recomputed {observed}, got {supplied}",
        )

    result: Dict[str, Any] = {
        "root_type": root_type,
        "verified_digest": True,
        "canonical_preimage_utf8": computed["canonical_preimage_utf8"],
        "state_root_digest": observed,
    }
    result.update(_result_metadata())
    return result


def verify_las_authority_state_root(root: Mapping[str, Any]) -> Dict[str, Any]:
    return _verify(
        root,
        LAS_PREIMAGE_MEMBERS,
        LAS_SEQUENCE_MEMBERS,
        root_type="LASAuthorityStateRoot",
    )


def verify_ggs_genesis_state_root(root: Mapping[str, Any]) -> Dict[str, Any]:
    return _verify(
        root,
        GGS_PREIMAGE_MEMBERS,
        GGS_SEQUENCE_MEMBERS,
        root_type="GGSGenesisStateRoot",
    )
