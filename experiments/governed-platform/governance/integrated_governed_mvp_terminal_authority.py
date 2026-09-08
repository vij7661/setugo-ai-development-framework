"""Integrated Governed MVP Slice 6 terminal-authority reference gate.

This module issues a deterministic terminal-action authorization receipt only.
It performs no remote push, merge, release, deploy, production mutation, or
completion side effect.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping


TERMINAL_ACTIONS = frozenset({"RELEASE", "DEPLOY", "MERGE", "COMPLETE"})
AUTHORITY_SOURCE_CLASSES = frozenset({"HUMAN", "PLATFORM_POLICY"})
EXECUTION_SUCCESS_STATES = frozenset(
    {
        "EXECUTED",
        "RECOVERED_AND_EXECUTED",
        "REPLAYED",
        "RECOVERED_REPLAY",
        "COMMITTED",
        "ACKED",
        "ISOLATED_EXECUTION_SUCCEEDED",
    }
)


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def with_self_hash(record: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = deepcopy(dict(record))
    result.pop(field, None)
    result[field] = canonical_hash(result)
    return result


def _self_hash_valid(record: Mapping[str, Any], field: str) -> bool:
    try:
        supplied = record.get(field)
        if not isinstance(supplied, str) or not supplied:
            return False
        material = deepcopy(dict(record))
        material.pop(field, None)
        return canonical_hash(material) == supplied
    except (TypeError, ValueError):
        return False


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _evidence_refs_valid(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_string(ref) for ref in value)


def _bound_lineage(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "project_id": request.get("project_id"),
        "task_id": request.get("task_id"),
        "effect_id": request.get("effect_id"),
        "action": request.get("action"),
        "artifact_sha": request.get("artifact_sha"),
        "state_version": request.get("expected_state_version"),
    }


def _decision(
    state: str,
    reason: str,
    request: Mapping[str, Any] | None = None,
    *,
    authority_id: str | None = None,
    review_evidence_refs: list[str] | None = None,
    authority_evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    authorized = state == "AUTHORIZED_FOR_TERMINAL_ACTION"
    body = {
        "state": state,
        "reason": reason,
        "authorized": authorized,
        "terminal_authority": authorized,
        "release_completion_authority": authorized,
        "actual_side_effect_performed": False,
        "bound_lineage": _bound_lineage(request or {}),
        "authority_id": authority_id,
        "review_evidence_refs": list(review_evidence_refs or []),
        "authority_evidence_refs": list(authority_evidence_refs or []),
    }
    return {**body, "receipt_hash": canonical_hash(body)}


def _request_valid(request: Mapping[str, Any]) -> bool:
    if not isinstance(request, Mapping):
        return False
    for field in ("project_id", "task_id", "effect_id", "artifact_sha"):
        if not _nonempty_string(request.get(field)):
            return False
    if request.get("action") not in TERMINAL_ACTIONS:
        return False
    version = request.get("expected_state_version")
    return isinstance(version, int) and not isinstance(version, bool) and version >= 0


def _current_state_valid(current_state: Mapping[str, Any]) -> bool:
    if not isinstance(current_state, Mapping):
        return False
    if not _nonempty_string(current_state.get("project_id")):
        return False
    version = current_state.get("state_version")
    return isinstance(version, int) and not isinstance(version, bool) and version >= 0


def _execution_evidence_valid(evidence: Mapping[str, Any]) -> bool:
    if not isinstance(evidence, Mapping) or not _self_hash_valid(evidence, "execution_evidence_hash"):
        return False
    if evidence.get("state") not in EXECUTION_SUCCESS_STATES:
        return False
    for field in ("project_id", "task_id", "effect_id", "artifact_sha"):
        if not _nonempty_string(evidence.get(field)):
            return False
    if bool(evidence.get("terminal_authority", False)):
        return False
    if bool(evidence.get("release_completion_authority", False)):
        return False
    return True


def _review_gate_shape_valid(review_gate: Mapping[str, Any]) -> bool:
    return (
        isinstance(review_gate, Mapping)
        and _nonempty_string(review_gate.get("state"))
        and _nonempty_string(review_gate.get("action"))
        and _nonempty_string(review_gate.get("artifact_sha"))
        and _evidence_refs_valid(review_gate.get("evidence_refs"))
    )


def _authority_record_shape_valid(authority_record: Mapping[str, Any]) -> bool:
    if not isinstance(authority_record, Mapping):
        return False
    if not _self_hash_valid(authority_record, "authority_record_hash"):
        return False
    for field in (
        "authority_id",
        "source_class",
        "decision",
        "project_id",
        "task_id",
        "effect_id",
        "action",
        "artifact_sha",
    ):
        if not _nonempty_string(authority_record.get(field)):
            return False
    state_version = authority_record.get("state_version")
    if not isinstance(state_version, int) or isinstance(state_version, bool) or state_version < 0:
        return False
    issued = authority_record.get("issued_at_epoch")
    expires = authority_record.get("expires_at_epoch")
    if not isinstance(issued, int) or isinstance(issued, bool):
        return False
    if not isinstance(expires, int) or isinstance(expires, bool):
        return False
    if expires <= issued:
        return False
    return _evidence_refs_valid(authority_record.get("evidence_refs"))


def _lineage_matches(request: Mapping[str, Any], other: Mapping[str, Any]) -> bool:
    return all(
        request.get(field) == other.get(field)
        for field in ("project_id", "task_id", "effect_id", "artifact_sha")
    )


def evaluate_terminal_authority(
    *,
    terminal_request: Mapping[str, Any],
    execution_evidence: Mapping[str, Any] | None,
    review_gate: Mapping[str, Any],
    authority_record: Mapping[str, Any] | None,
    current_state: Mapping[str, Any],
    now_epoch: int,
) -> dict[str, Any]:
    """Evaluate one exact terminal action without performing that action."""

    if not _request_valid(terminal_request):
        return _decision("DENY_REQUEST", "terminal request is malformed or action is unsupported", terminal_request)

    if not _current_state_valid(current_state) or current_state.get("project_id") != terminal_request.get("project_id"):
        return _decision("DENY_STATE_VERSION", "current authoritative state is malformed or project-mismatched", terminal_request)

    if terminal_request.get("expected_state_version") != current_state.get("state_version"):
        return _decision("DENY_STATE_VERSION", "expected state version does not equal current authoritative state version", terminal_request)

    if not isinstance(execution_evidence, Mapping) or not _execution_evidence_valid(execution_evidence):
        return _decision("DENY_EXECUTION_EVIDENCE", "prior isolated execution evidence is missing, malformed, tampered, non-successful, or attempts terminal authority", terminal_request)

    if not _lineage_matches(terminal_request, execution_evidence):
        return _decision("DENY_EXECUTION_EVIDENCE", "execution evidence is not bound to the exact terminal request lineage", terminal_request)

    if not _review_gate_shape_valid(review_gate):
        return _decision("DENY_REVIEW_GATE", "review gate is malformed or lacks immutable evidence references", terminal_request)

    if review_gate.get("state") != "CLEAR":
        return _decision("DENY_REVIEW_GATE", "review gate is not CLEAR for terminal action", terminal_request)

    if review_gate.get("action") != terminal_request.get("action") or review_gate.get("artifact_sha") != terminal_request.get("artifact_sha"):
        return _decision("DENY_REVIEW_GATE", "review gate is not bound to the exact action and artifact", terminal_request)

    if not isinstance(authority_record, Mapping):
        return _decision(
            "DENY_AUTHORITY_RECORD",
            "external terminal authority record is missing",
            terminal_request,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
        )

    source_class = authority_record.get("source_class")
    if source_class not in AUTHORITY_SOURCE_CLASSES:
        return _decision(
            "DENY_AUTHORITY_SOURCE",
            "authority source class is not permitted to mint terminal authority",
            terminal_request,
            authority_id=authority_record.get("authority_id") if _nonempty_string(authority_record.get("authority_id")) else None,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
        )

    if not _authority_record_shape_valid(authority_record):
        return _decision(
            "DENY_AUTHORITY_RECORD",
            "authority record is malformed, tampered, or non-deterministic",
            terminal_request,
            authority_id=authority_record.get("authority_id") if _nonempty_string(authority_record.get("authority_id")) else None,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
        )

    authority_evidence_refs = list(authority_record.get("evidence_refs", []))
    authority_id = authority_record.get("authority_id")

    if (
        not _lineage_matches(terminal_request, authority_record)
        or authority_record.get("action") != terminal_request.get("action")
        or authority_record.get("state_version") != terminal_request.get("expected_state_version")
    ):
        return _decision(
            "DENY_AUTHORITY_RECORD",
            "authority record is not bound to the exact project/task/effect/action/artifact/state-version lineage",
            terminal_request,
            authority_id=authority_id,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
            authority_evidence_refs=authority_evidence_refs,
        )

    issued_at = authority_record.get("issued_at_epoch")
    expires_at = authority_record.get("expires_at_epoch")
    if issued_at > now_epoch:
        return _decision(
            "DENY_AUTHORITY_RECORD",
            "authority record was issued in the future",
            terminal_request,
            authority_id=authority_id,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
            authority_evidence_refs=authority_evidence_refs,
        )
    if now_epoch >= expires_at:
        return _decision(
            "DENY_EXPIRED_AUTHORITY",
            "authority record is expired",
            terminal_request,
            authority_id=authority_id,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
            authority_evidence_refs=authority_evidence_refs,
        )

    decision = authority_record.get("decision")
    if decision == "DENY":
        return _decision(
            "TERMINAL_ACTION_DENIED",
            "external terminal authority explicitly denied the action",
            terminal_request,
            authority_id=authority_id,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
            authority_evidence_refs=authority_evidence_refs,
        )
    if decision != "APPROVE":
        return _decision(
            "DENY_AUTHORITY_RECORD",
            "authority decision is malformed or unrecognized",
            terminal_request,
            authority_id=authority_id,
            review_evidence_refs=list(review_gate.get("evidence_refs", [])),
            authority_evidence_refs=authority_evidence_refs,
        )

    return _decision(
        "AUTHORIZED_FOR_TERMINAL_ACTION",
        "exact execution lineage, review gate, state version, artifact, action, and external approval are current and bound",
        terminal_request,
        authority_id=authority_id,
        review_evidence_refs=list(review_gate.get("evidence_refs", [])),
        authority_evidence_refs=authority_evidence_refs,
    )
