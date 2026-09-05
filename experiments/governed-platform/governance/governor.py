"""Minimal deterministic governor for governed-platform falsification.

The governor enforces event authenticity, replay protection, exact project/task/SHA
binding, optimistic state-version checks, manual gates, evidence requirements,
and scoped corrective authority. It is intentionally small enough to falsify in
EXP-D/F before a larger orchestration service exists.
"""
from __future__ import annotations

from copy import deepcopy

TERMINAL_DECISIONS = {"IGNORE", "BLOCK", "REQUEST_HUMAN", "CONTINUE", "DIAGNOSE", "COMPLETE"}
FAILURE_CLASSES = {
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "REQUIREMENT UNRESOLVED",
}
ALLOWED_BY_CLASS = {
    "CODE DEFECT": {"production_code"},
    "FIXTURE-DATA DEFECT": {"fixtures", "seed_data", "test_data"},
    "TEST DEFECT": {"tests", "test_harness"},
    "ENVIRONMENT-TOOLING DEFECT": {"ci", "tooling", "environment_config", "build_config"},
    "REQUIREMENT UNRESOLVED": set(),
}


def _result(decision: str, reason: str, state: dict, event: dict, *, mutate: bool = False) -> dict:
    if decision not in TERMINAL_DECISIONS:
        raise ValueError(f"unsupported decision {decision}")
    return {
        "decision": decision,
        "reason": reason,
        "event_key": f"{event.get('source','')}::{event.get('event_id','')}",
        "state": deepcopy(state),
        "mutated": mutate,
    }


def _consume(current: dict, event_key: str, evidence_refs: set[str]) -> dict:
    """Record an authoritative event before any downstream side effect is dispatched."""
    consumed = deepcopy(current)
    processed = set(consumed.get("processed_event_keys", []))
    consumed["processed_event_keys"] = sorted(processed | {event_key})
    consumed["state_version"] = int(consumed.get("state_version", 0)) + 1
    consumed["last_event_key"] = event_key
    consumed["last_evidence_refs"] = sorted(evidence_refs)
    return consumed


def _string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def _required_evidence_provenance_is_current(current: dict, required_evidence: set[str]) -> bool:
    """Validate authoritative evidence bindings when the state declares them.

    Legacy pilot states may omit evidence_bindings. Once bindings are present,
    every required evidence reference must be bound to the current project, task,
    and exact execution SHA; a stale or cross-scope binding fails closed.
    """
    bindings = current.get("evidence_bindings")
    if bindings is None:
        return True
    if not isinstance(bindings, dict):
        return False
    expected = {
        "project_id": current.get("project_id"),
        "task_id": current.get("task_id"),
        "execution_sha": current.get("execution_sha"),
    }
    for ref in required_evidence:
        binding = bindings.get(ref)
        if not isinstance(binding, dict):
            return False
        for key, value in expected.items():
            if binding.get(key) != value:
                return False
    return True


def process_event(state: dict, event: dict) -> dict:
    """Evaluate one event against authoritative state.

    The caller must persist the returned state and event ledger atomically. The
    expected_state_version field provides compare-and-swap semantics so racing or
    out-of-order completions cannot advance the same state twice.
    """
    current = deepcopy(state)
    required_event = ["source", "event_id", "project_id", "task_id", "execution_sha", "expected_state_version"]
    missing = [k for k in required_event if event.get(k) in (None, "")]
    if missing:
        return _result("BLOCK", "missing required event fields: " + ",".join(missing), current, event)

    if not event.get("authenticated", False):
        return _result("BLOCK", "event authenticity not established", current, event)

    event_key = f"{event['source']}::{event['event_id']}"
    processed = set(current.get("processed_event_keys", []))
    if event_key in processed:
        return _result("IGNORE", "duplicate/replayed event", current, event)

    if event["project_id"] != current.get("project_id") or event["task_id"] != current.get("task_id"):
        return _result("IGNORE", "event belongs to a different project/task", current, event)

    if event["execution_sha"] != current.get("execution_sha"):
        return _result("IGNORE", "event is stale or bound to a different execution SHA", current, event)

    try:
        expected_version = int(event["expected_state_version"])
        current_version = int(current.get("state_version", 0))
    except (TypeError, ValueError):
        return _result("BLOCK", "state version is malformed", current, event)
    if expected_version != current_version:
        return _result("IGNORE", "event is out-of-order or lost an optimistic state-version race", current, event)

    evidence_value = event.get("evidence_refs", [])
    if not _string_list(evidence_value):
        return _result("BLOCK", "evidence refs are malformed", current, event)
    supplied_evidence = set(evidence_value)

    if current.get("manual_gate_active", False):
        return _result("REQUEST_HUMAN", "mandatory manual gate is active", current, event)

    if event.get("budget_exhausted", False):
        return _result("BLOCK", "resource/budget exhaustion cannot be interpreted as PASS", current, event)

    conclusion = str(event.get("conclusion", "")).lower()
    if conclusion in {"failure", "timed_out"}:
        classification = event.get("classification")
        if not classification:
            return _result("DIAGNOSE", "failed execution requires evidence-based classification", current, event)
        if classification not in FAILURE_CLASSES:
            return _result("BLOCK", "unrecognized failure classification", current, event)
        if not supplied_evidence:
            return _result("BLOCK", "classified failure requires evidence refs", current, event)
        requested_value = event.get("requested_artifact_classes", [])
        if not _string_list(requested_value):
            return _result("BLOCK", "requested corrective scope is malformed", current, event)
        requested = set(requested_value)
        allowed = ALLOWED_BY_CLASS[classification]
        if not requested.issubset(allowed):
            return _result("BLOCK", "requested corrective scope exceeds classified authority", current, event)
        consumed = _consume(current, event_key, supplied_evidence)
        if classification == "REQUIREMENT UNRESOLVED":
            return _result(
                "REQUEST_HUMAN",
                "requirement ambiguity cannot receive automatic corrective authority",
                consumed,
                event,
                mutate=True,
            )
        return _result(
            "DIAGNOSE",
            "failure classified; scoped repair may be dispatched by corrective controller",
            consumed,
            event,
            mutate=True,
        )

    if conclusion != "success":
        return _result("IGNORE", "event is not a terminal success/failure signal", current, event)

    required_evidence = set(current.get("required_evidence", []))
    if not required_evidence.issubset(supplied_evidence):
        return _result("BLOCK", "required evidence is incomplete", current, event)
    if not _required_evidence_provenance_is_current(current, required_evidence):
        return _result("BLOCK", "required evidence provenance is stale, malformed, or out of scope", current, event)

    requested_transition = event.get("requested_transition", "CONTINUING")
    if requested_transition == "COMPLETE" and not current.get("completion_authorized", False):
        return _result("BLOCK", "COMPLETE promotion is not authorized for the current gate", current, event)

    if requested_transition not in {"CONTINUING", "COMPLETE"}:
        return _result("BLOCK", "unsupported success transition", current, event)

    current = _consume(current, event_key, supplied_evidence)
    current["status"] = requested_transition
    return _result(requested_transition if requested_transition == "COMPLETE" else "CONTINUE", "validated event advanced authoritative state", current, event, mutate=True)
