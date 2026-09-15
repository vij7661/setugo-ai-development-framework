#!/usr/bin/env python3
"""V15 review/blocker ledgers, adjudication, generation, currentness, residual trust.

Construction-stage implementation only. No runtime, scientific, deployment, release,
or terminal authority is granted by these validators.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    canonical_hash,
    validate_blocker_record,
    validate_currentness_binding,
    validate_residual_trust_root,
)

REVIEW_LEDGER_STATES = frozenset({"RECEIVED", "VALIDATED", "NONPROMOTABLE", "SUPERSEDED"})
GENERATION_IMPACT_STATES = frozenset({
    "MATERIAL_GOVERNANCE_CHANGE",
    "PROVEN_NON_IMPACTING",
    "GOVERNANCE_IMPACT_UNKNOWN",
})
ALWAYS_LOAD_BEARING_CHANGE_CLASSES = frozenset({
    "REVIEW_GOVERNANCE_ROOT",
    "CONTROL_DOMAIN_ANCESTRY",
    "ROLE_AUTHORITY_REGISTRY",
    "REVIEWER_QUALIFICATION_POLICY",
    "HIDDEN_EVIDENCE_MONITOR_POLICY",
    "ADJUDICATION_POLICY",
    "EFFECT_FENCING_POLICY",
    "RESIDUAL_TRUST_POLICY",
    "CURRENTNESS_POLICY",
})


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _sealed_digest(record: Mapping[str, Any], field: str) -> str:
    return canonical_hash({k: v for k, v in record.items() if k != field})


def _finish(problems: Iterable[str], ok: str, bad: str) -> dict[str, Any]:
    p = sorted(set(problems))
    return {
        "state": ok if not p else bad,
        "valid": not p,
        "qualified": False,
        "problems": p,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_review_response_ledger(bundle: Mapping[str, Any], *, expected_snapshot_id: str) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("REVIEW_LEDGER_SCHEMA_INVALID")
    for key in ("ledger_id", "generation_id", "witness_id", "witness_control_domain_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"REVIEW_LEDGER_FIELD_REQUIRED:{key}")
    if bundle.get("candidate_controlled") is not False:
        p.append("REVIEW_LEDGER_CANDIDATE_CONTROL_FORBIDDEN")
    rows = bundle.get("records")
    if not isinstance(rows, list) or not rows:
        rows = []
        p.append("REVIEW_LEDGER_RECORDS_REQUIRED")
    prev = "GENESIS"
    expected_sequence = 1
    ids: set[str] = set()
    record_digests: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"REVIEW_LEDGER_RECORD_MALFORMED:{i}")
            continue
        rid = row.get("ledger_record_id")
        if not _nonempty(rid):
            p.append(f"REVIEW_LEDGER_RECORD_ID_REQUIRED:{i}")
            continue
        if rid in ids:
            p.append(f"REVIEW_LEDGER_RECORD_ID_DUPLICATE:{rid}")
        ids.add(str(rid))
        if row.get("ledger_sequence") != expected_sequence:
            p.append(f"REVIEW_LEDGER_SEQUENCE_MISMATCH:{rid}:{expected_sequence}")
        expected_sequence += 1
        if row.get("predecessor_record_digest") != prev:
            p.append(f"REVIEW_LEDGER_PREDECESSOR_MISMATCH:{rid}")
        if row.get("snapshot_id") != expected_snapshot_id:
            p.append(f"REVIEW_LEDGER_SNAPSHOT_MISMATCH:{rid}")
        if row.get("state") not in REVIEW_LEDGER_STATES:
            p.append(f"REVIEW_LEDGER_STATE_INVALID:{rid}")
        for key in ("review_id", "reviewer_id", "session_id"):
            if not _nonempty(row.get(key)):
                p.append(f"REVIEW_LEDGER_RECORD_FIELD_REQUIRED:{rid}:{key}")
        for key in ("response_receipt_digest", "content_root_digest"):
            if not _sha256(row.get(key)):
                p.append(f"REVIEW_LEDGER_RECORD_SHA256_INVALID:{rid}:{key}")
        if row.get("candidate_controlled") is not False:
            p.append(f"REVIEW_LEDGER_RECORD_CANDIDATE_CONTROL_FORBIDDEN:{rid}")
        supplied = row.get("record_digest")
        if not _sha256(supplied):
            p.append(f"REVIEW_LEDGER_RECORD_DIGEST_INVALID:{rid}")
            prev = "INVALID"
        else:
            expected = _sealed_digest(row, "record_digest")
            if supplied != expected:
                p.append(f"REVIEW_LEDGER_RECORD_DIGEST_MISMATCH:{rid}")
            prev = expected
            record_digests.append(expected)
    if rows:
        if bundle.get("current_head_digest") != prev:
            p.append("REVIEW_LEDGER_CURRENT_HEAD_MISMATCH")
        if bundle.get("witnessed_head_digest") != prev:
            p.append("REVIEW_LEDGER_WITNESSED_HEAD_MISMATCH")
    if bundle.get("witness_currentness_state") != "CURRENT":
        p.append("REVIEW_LEDGER_WITNESS_NOT_CURRENT")
    if bundle.get("witness_independence_result") != "INDEPENDENT":
        p.append("REVIEW_LEDGER_WITNESS_INDEPENDENCE_REQUIRED")
    supplied = bundle.get("ledger_digest")
    if not _sha256(supplied):
        p.append("REVIEW_LEDGER_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "ledger_digest"):
        p.append("REVIEW_LEDGER_DIGEST_MISMATCH")
    out = _finish(p, "REVIEW_RESPONSE_LEDGER_VALID", "REVIEW_RESPONSE_LEDGER_INVALID")
    out["current_head_digest"] = prev
    out["record_count"] = len(record_digests)
    return out


def validate_blocker_ledger(bundle: Mapping[str, Any], *, expected_snapshot_id: str) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("BLOCKER_LEDGER_SCHEMA_INVALID")
    for key in ("ledger_id", "generation_id", "witness_id", "witness_control_domain_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"BLOCKER_LEDGER_FIELD_REQUIRED:{key}")
    if bundle.get("candidate_controlled") is not False:
        p.append("BLOCKER_LEDGER_CANDIDATE_CONTROL_FORBIDDEN")
    rows = bundle.get("records")
    if not isinstance(rows, list):
        rows = []
        p.append("BLOCKER_LEDGER_RECORDS_REQUIRED")
    prev = "GENESIS"
    expected_sequence = 1
    open_blockers: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"BLOCKER_LEDGER_RECORD_MALFORMED:{i}")
            continue
        bid = row.get("blocker_id")
        checked = validate_blocker_record(row)
        if not checked["valid"]:
            p.extend(f"BLOCKER[{i}]:{x}" for x in checked["problems"])
        if row.get("snapshot_id") != expected_snapshot_id:
            p.append(f"BLOCKER_LEDGER_SNAPSHOT_MISMATCH:{bid}")
        if row.get("ledger_sequence") != expected_sequence:
            p.append(f"BLOCKER_LEDGER_SEQUENCE_MISMATCH:{bid}:{expected_sequence}")
        expected_sequence += 1
        if row.get("predecessor_record_digest") != prev:
            p.append(f"BLOCKER_LEDGER_PREDECESSOR_MISMATCH:{bid}")
        expected_digest = _sealed_digest(row, "record_digest")
        prev = expected_digest
        if row.get("state") == "OPEN_BLOCKER":
            open_blockers.append(str(bid))
    if rows:
        if bundle.get("current_head_digest") != prev:
            p.append("BLOCKER_LEDGER_CURRENT_HEAD_MISMATCH")
        if bundle.get("witnessed_head_digest") != prev:
            p.append("BLOCKER_LEDGER_WITNESSED_HEAD_MISMATCH")
    if bundle.get("witness_currentness_state") != "CURRENT":
        p.append("BLOCKER_LEDGER_WITNESS_NOT_CURRENT")
    if bundle.get("witness_independence_result") != "INDEPENDENT":
        p.append("BLOCKER_LEDGER_WITNESS_INDEPENDENCE_REQUIRED")
    supplied = bundle.get("ledger_digest")
    if not _sha256(supplied):
        p.append("BLOCKER_LEDGER_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "ledger_digest"):
        p.append("BLOCKER_LEDGER_DIGEST_MISMATCH")
    out = _finish(p, "BLOCKER_LEDGER_VALID", "BLOCKER_LEDGER_INVALID")
    out["current_head_digest"] = prev
    out["open_blockers"] = sorted(open_blockers)
    out["promotion_blocked"] = bool(open_blockers or not out["valid"])
    return out


def validate_currentness_vector(bundle: Mapping[str, Any], *, required_subject_ids: Sequence[str]) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("CURRENTNESS_VECTOR_SCHEMA_INVALID")
    for key in ("vector_id", "generation_id", "snapshot_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"CURRENTNESS_VECTOR_FIELD_REQUIRED:{key}")
    rows = bundle.get("bindings")
    if not isinstance(rows, list) or not rows:
        rows = []
        p.append("CURRENTNESS_VECTOR_BINDINGS_REQUIRED")
    by_subject: dict[str, Mapping[str, Any]] = {}
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"CURRENTNESS_VECTOR_BINDING_MALFORMED:{i}")
            continue
        checked = validate_currentness_binding(row)
        if not checked["valid"]:
            p.extend(f"CURRENTNESS[{i}]:{x}" for x in checked["problems"])
        sid = row.get("subject_id")
        if _nonempty(sid):
            if sid in by_subject:
                p.append(f"CURRENTNESS_VECTOR_SUBJECT_DUPLICATE:{sid}")
            else:
                by_subject[str(sid)] = row
        if row.get("generation_id") != bundle.get("generation_id"):
            p.append(f"CURRENTNESS_VECTOR_GENERATION_MISMATCH:{sid}")
        if row.get("state") != "CURRENT":
            p.append(f"CURRENTNESS_VECTOR_NONCURRENT:{sid}")
    expected = set(required_subject_ids)
    if set(by_subject) != expected:
        p.append("CURRENTNESS_VECTOR_SUBJECT_SET_MISMATCH")
    supplied = bundle.get("vector_digest")
    if not _sha256(supplied):
        p.append("CURRENTNESS_VECTOR_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "vector_digest"):
        p.append("CURRENTNESS_VECTOR_DIGEST_MISMATCH")
    out = _finish(p, "CURRENTNESS_VECTOR_VALID", "CURRENTNESS_VECTOR_INVALID")
    out["current"] = out["valid"]
    out["subject_count"] = len(by_subject)
    return out


def validate_governance_generation(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("GOVERNANCE_GENERATION_SCHEMA_INVALID")
    for key in ("generation_id", "predecessor_generation_id", "transition_id", "authority_id"):
        if not _nonempty(record.get(key)):
            p.append(f"GOVERNANCE_GENERATION_FIELD_REQUIRED:{key}")
    changes = record.get("change_classes")
    if not isinstance(changes, list) or not changes or not all(_nonempty(x) for x in changes):
        p.append("GOVERNANCE_GENERATION_CHANGE_CLASSES_REQUIRED")
        changes = []
    if len(changes) != len(set(changes)):
        p.append("GOVERNANCE_GENERATION_CHANGE_CLASS_DUPLICATE")
    impact = record.get("impact_state")
    if impact not in GENERATION_IMPACT_STATES:
        p.append("GOVERNANCE_GENERATION_IMPACT_STATE_INVALID")
    load_bearing = bool(set(changes) & ALWAYS_LOAD_BEARING_CHANGE_CLASSES)
    if load_bearing and impact != "MATERIAL_GOVERNANCE_CHANGE":
        p.append("GOVERNANCE_GENERATION_LOAD_BEARING_CHANGE_MUST_BE_MATERIAL")
    if not load_bearing and impact == "PROVEN_NON_IMPACTING":
        if record.get("independent_nonimpact_proof_valid") is not True:
            p.append("GOVERNANCE_GENERATION_NONIMPACT_PROOF_REQUIRED")
    if impact == "GOVERNANCE_IMPACT_UNKNOWN" and record.get("promotion_blocked") is not True:
        p.append("GOVERNANCE_GENERATION_UNKNOWN_IMPACT_MUST_BLOCK")
    for key in ("change_set_digest", "cumulative_generation_digest", "transition_evidence_digest", "witness_anchor_digest"):
        if not _sha256(record.get(key)):
            p.append(f"GOVERNANCE_GENERATION_SHA256_INVALID:{key}")
    if record.get("witness_currentness_state") != "CURRENT":
        p.append("GOVERNANCE_GENERATION_WITNESS_NOT_CURRENT")
    if record.get("witness_independence_result") != "INDEPENDENT":
        p.append("GOVERNANCE_GENERATION_WITNESS_INDEPENDENCE_REQUIRED")
    if record.get("candidate_controlled") is not False:
        p.append("GOVERNANCE_GENERATION_CANDIDATE_CONTROL_FORBIDDEN")
    supplied = record.get("generation_record_digest")
    if not _sha256(supplied):
        p.append("GOVERNANCE_GENERATION_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "generation_record_digest"):
        p.append("GOVERNANCE_GENERATION_RECORD_DIGEST_MISMATCH")
    out = _finish(p, "GOVERNANCE_GENERATION_RECORD_VALID", "GOVERNANCE_GENERATION_RECORD_INVALID")
    out["promotion_blocked"] = bool(not out["valid"] or impact == "GOVERNANCE_IMPACT_UNKNOWN")
    out["load_bearing_change"] = load_bearing
    return out


def validate_residual_trust_state(state: Mapping[str, Any], *, root_records: Sequence[Mapping[str, Any]], required_root_ids: Sequence[str]) -> dict[str, Any]:
    p: list[str] = []
    if state.get("schema_version") != 1:
        p.append("RESIDUAL_TRUST_STATE_SCHEMA_INVALID")
    for key in ("state_id", "generation_id", "snapshot_id", "risk_owner_id"):
        if not _nonempty(state.get(key)):
            p.append(f"RESIDUAL_TRUST_STATE_FIELD_REQUIRED:{key}")
    roots: dict[str, Mapping[str, Any]] = {}
    for i, row in enumerate(root_records):
        if not isinstance(row, Mapping):
            p.append(f"RESIDUAL_TRUST_STATE_ROOT_MALFORMED:{i}")
            continue
        checked = validate_residual_trust_root(row)
        if not checked["valid"]:
            p.extend(f"ROOT[{i}]:{x}" for x in checked["problems"])
        rid = row.get("root_id")
        if _nonempty(rid):
            roots[str(rid)] = row
        if row.get("currentness_state") != "CURRENT":
            p.append(f"RESIDUAL_TRUST_STATE_ROOT_NOT_CURRENT:{rid}")
        if row.get("generation_id") != state.get("generation_id"):
            p.append(f"RESIDUAL_TRUST_STATE_ROOT_GENERATION_MISMATCH:{rid}")
    if set(roots) != set(required_root_ids):
        p.append("RESIDUAL_TRUST_STATE_ROOT_SET_MISMATCH")
    declared = state.get("declared_root_ids")
    if not isinstance(declared, list) or set(declared) != set(required_root_ids):
        p.append("RESIDUAL_TRUST_STATE_DECLARED_ROOT_SET_MISMATCH")
    limitations = state.get("unresolved_limitations")
    if not isinstance(limitations, list):
        p.append("RESIDUAL_TRUST_STATE_LIMITATIONS_REQUIRED")
    if state.get("cannot_override_blockers") is not True:
        p.append("RESIDUAL_TRUST_STATE_CANNOT_OVERRIDE_BLOCKERS_REQUIRED")
    if state.get("cannot_override_insufficiency") is not True:
        p.append("RESIDUAL_TRUST_STATE_CANNOT_OVERRIDE_INSUFFICIENCY_REQUIRED")
    if state.get("cannot_override_unproven_independence") is not True:
        p.append("RESIDUAL_TRUST_STATE_CANNOT_OVERRIDE_INDEPENDENCE_REQUIRED")
    if not _sha256(state.get("risk_owner_acceptance_digest")):
        p.append("RESIDUAL_TRUST_STATE_RISK_OWNER_ACCEPTANCE_REQUIRED")
    if state.get("currentness_state") != "CURRENT":
        p.append("RESIDUAL_TRUST_STATE_NOT_CURRENT")
    if state.get("unresolved_common_control_risk") is True and state.get("promotion_blocked") is not True:
        p.append("RESIDUAL_TRUST_STATE_COMMON_CONTROL_RISK_MUST_BLOCK")
    supplied = state.get("state_digest")
    if not _sha256(supplied):
        p.append("RESIDUAL_TRUST_STATE_DIGEST_INVALID")
    elif supplied != _sealed_digest(state, "state_digest"):
        p.append("RESIDUAL_TRUST_STATE_DIGEST_MISMATCH")
    out = _finish(p, "RESIDUAL_TRUST_STATE_VALID", "RESIDUAL_TRUST_STATE_INVALID")
    out["promotion_blocked"] = bool(not out["valid"] or state.get("unresolved_common_control_risk") is True)
    return out


def validate_adjudication_firewall(record: Mapping[str, Any], *, expected: Mapping[str, str], blocker_ledger_result: Mapping[str, Any], currentness_vector_result: Mapping[str, Any], residual_trust_result: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("ADJUDICATION_SCHEMA_INVALID")
    for key in ("adjudication_id", "adjudicator_id", "adjudicator_control_domain_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"ADJUDICATION_FIELD_REQUIRED:{key}")
    if record.get("raw_hidden_evidence_read_capability") is not False:
        p.append("ADJUDICATION_HIDDEN_RAW_READ_CAPABILITY_FORBIDDEN")
    if record.get("candidate_controlled") is not False:
        p.append("ADJUDICATION_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("adjudicator_independence_result") != "INDEPENDENT":
        p.append("ADJUDICATION_INDEPENDENCE_REQUIRED")
    allowed_inputs = record.get("allowed_input_classes")
    required_inputs = {"REVIEWER_VISIBLE_EVIDENCE", "AUTHENTICATED_REVIEW_RESPONSES", "REVIEW_RESPONSE_LEDGER", "BLOCKER_LEDGER", "HIDDEN_MONITOR_CERTIFICATE", "GOVERNED_POLICY", "CURRENTNESS_VECTOR", "RESIDUAL_TRUST_STATE"}
    if not isinstance(allowed_inputs, list) or set(allowed_inputs) != required_inputs:
        p.append("ADJUDICATION_ALLOWED_INPUT_SET_MISMATCH")
    for key in ("reviewer_visible_evidence_root_digest", "review_ledger_head_digest", "blocker_ledger_head_digest", "monitor_certificate_digest", "policy_digest", "currentness_vector_digest", "residual_trust_state_digest"):
        if not _sha256(record.get(key)):
            p.append(f"ADJUDICATION_SHA256_INVALID:{key}")
        if key in expected and record.get(key) != expected[key]:
            p.append(f"ADJUDICATION_BINDING_MISMATCH:{key}")
    if blocker_ledger_result.get("promotion_blocked") is True:
        p.append("ADJUDICATION_OPEN_BLOCKER_PRESENT")
    if not currentness_vector_result.get("valid") or not currentness_vector_result.get("current"):
        p.append("ADJUDICATION_CURRENTNESS_VECTOR_INVALID")
    if residual_trust_result.get("promotion_blocked") is True:
        p.append("ADJUDICATION_RESIDUAL_TRUST_BLOCKING")
    if record.get("monitor_reopen_required") is True:
        p.append("ADJUDICATION_MONITOR_REOPEN_REQUIRED")
    if record.get("review_response_valid") is not True:
        p.append("ADJUDICATION_REVIEW_RESPONSE_INVALID")
    if record.get("clean_room_promotable") is not True:
        p.append("ADJUDICATION_CLEAN_ROOM_NONPROMOTABLE")
    if record.get("decision_time_revalidation_complete") is not True:
        p.append("ADJUDICATION_DECISION_TIME_REVALIDATION_REQUIRED")
    supplied = record.get("adjudication_digest")
    if not _sha256(supplied):
        p.append("ADJUDICATION_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "adjudication_digest"):
        p.append("ADJUDICATION_DIGEST_MISMATCH")
    out = _finish(p, "ADJUDICATION_FIREWALL_VALID", "ADJUDICATION_FIREWALL_INVALID")
    out["positive_completion_ready"] = out["valid"]
    return out


def governance_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_LEDGER_ADJUDICATION_GENERATION_RESIDUAL_TRUST_CONSTRUCTION_READY",
        "implemented_surfaces": [25, 26, 27, 28, 29],
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
