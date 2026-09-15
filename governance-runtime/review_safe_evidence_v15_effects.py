#!/usr/bin/env python3
"""V15 effect fencing, taint/provenance, and implementation stopping rule.

Construction-stage implementation only. Passing these validators does not create
runtime, scientific, release, deployment, or terminal authority.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Iterable, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    canonical_hash,
    validate_fenced_effect_token,
)

PROVENANCE_CLASSES = frozenset({
    "SOURCE_EVIDENCE",
    "CANONICAL_NEUTRAL_TEMPLATE",
    "DETERMINISTIC_STRUCTURED_VIEW",
    "POST_REVIEW_FINDING",
    "EXTERNAL_NARRATIVE",
    "UNKNOWN_PROVENANCE",
})
CLEAN_PACKAGE_ALLOWED_CLASSES = frozenset({
    "SOURCE_EVIDENCE",
    "CANONICAL_NEUTRAL_TEMPLATE",
    "DETERMINISTIC_STRUCTURED_VIEW",
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


def validate_effect_issuance_record(
    record: Mapping[str, Any],
    *,
    current_sequence: int,
    consumed_token_ids: set[str] | frozenset[str],
    expected_context: Mapping[str, str],
    adjudication_result: Mapping[str, Any],
    currentness_vector_result: Mapping[str, Any],
    blocker_ledger_result: Mapping[str, Any],
    monitor_certificate_result: Mapping[str, Any],
    residual_trust_result: Mapping[str, Any],
) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("EFFECT_ISSUANCE_SCHEMA_INVALID")
    for key in ("issuance_id", "effect_id", "gateway_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"EFFECT_ISSUANCE_FIELD_REQUIRED:{key}")
    if record.get("candidate_controlled") is not False:
        p.append("EFFECT_ISSUANCE_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("effect_fenceable") is not True:
        p.append("EFFECT_ISSUANCE_UNFENCEABLE_EFFECT_NONPROMOTABLE")
    if record.get("decision_time_revalidation_complete") is not True:
        p.append("EFFECT_ISSUANCE_DECISION_TIME_REVALIDATION_REQUIRED")
    if adjudication_result.get("positive_completion_ready") is not True:
        p.append("EFFECT_ISSUANCE_ADJUDICATION_NOT_READY")
    if blocker_ledger_result.get("promotion_blocked") is True:
        p.append("EFFECT_ISSUANCE_BLOCKER_LEDGER_BLOCKING")
    if monitor_certificate_result.get("promotion_blocked") is True:
        p.append("EFFECT_ISSUANCE_MONITOR_CERTIFICATE_BLOCKING")
    if residual_trust_result.get("promotion_blocked") is True:
        p.append("EFFECT_ISSUANCE_RESIDUAL_TRUST_BLOCKING")
    if not currentness_vector_result.get("valid") or not currentness_vector_result.get("current"):
        p.append("EFFECT_ISSUANCE_CURRENTNESS_VECTOR_INVALID")

    token = record.get("token")
    if not isinstance(token, Mapping):
        token = {}
        p.append("EFFECT_ISSUANCE_TOKEN_REQUIRED")
    token_result = validate_fenced_effect_token(
        token,
        current_sequence=current_sequence,
        consumed_token_ids=consumed_token_ids,
        expected=expected_context,
    )
    if not token_result["valid"]:
        p.extend(f"TOKEN:{x}" for x in token_result["problems"])
    for key in ("candidate_id", "snapshot_id", "generation_id"):
        if record.get(key) != expected_context.get(key):
            p.append(f"EFFECT_ISSUANCE_CONTEXT_MISMATCH:{key}")
    if record.get("token_id") != token.get("token_id"):
        p.append("EFFECT_ISSUANCE_TOKEN_ID_MISMATCH")
    if record.get("gateway_version_digest") != expected_context.get("gateway_version_digest"):
        p.append("EFFECT_ISSUANCE_GATEWAY_VERSION_MISMATCH")
    if not _sha256(record.get("gateway_version_digest")):
        p.append("EFFECT_ISSUANCE_GATEWAY_VERSION_DIGEST_INVALID")
    supplied = record.get("issuance_digest")
    if not _sha256(supplied):
        p.append("EFFECT_ISSUANCE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "issuance_digest"):
        p.append("EFFECT_ISSUANCE_DIGEST_MISMATCH")
    out = _finish(p, "FENCED_EFFECT_ISSUANCE_VALID", "FENCED_EFFECT_ISSUANCE_INVALID")
    out["effect_ready"] = out["valid"]
    return out


def validate_external_effect_gateway(
    record: Mapping[str, Any],
    *,
    token: Mapping[str, Any],
    current_sequence: int,
    consumed_token_ids: set[str] | frozenset[str],
    expected_context: Mapping[str, str],
) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("EFFECT_GATEWAY_SCHEMA_INVALID")
    for key in ("gateway_decision_id", "gateway_id", "effect_id", "token_id"):
        if not _nonempty(record.get(key)):
            p.append(f"EFFECT_GATEWAY_FIELD_REQUIRED:{key}")
    if record.get("candidate_controlled") is not False:
        p.append("EFFECT_GATEWAY_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("token_id") != token.get("token_id"):
        p.append("EFFECT_GATEWAY_TOKEN_ID_MISMATCH")
    if record.get("effect_fenceable") is not True:
        p.append("EFFECT_GATEWAY_UNFENCEABLE_EFFECT_REJECTED")
    if record.get("immediate_pre_effect_revalidation") is not True:
        p.append("EFFECT_GATEWAY_IMMEDIATE_REVALIDATION_REQUIRED")
    if record.get("atomic_token_consumption") is not True:
        p.append("EFFECT_GATEWAY_ATOMIC_TOKEN_CONSUMPTION_REQUIRED")
    if record.get("current_gateway_version_digest") != expected_context.get("gateway_version_digest"):
        p.append("EFFECT_GATEWAY_VERSION_DRIFT")
    if not _sha256(record.get("current_gateway_version_digest")):
        p.append("EFFECT_GATEWAY_VERSION_DIGEST_INVALID")
    for key in ("candidate_id", "snapshot_id", "generation_id"):
        if record.get(key) != expected_context.get(key):
            p.append(f"EFFECT_GATEWAY_CONTEXT_MISMATCH:{key}")
    token_result = validate_fenced_effect_token(
        token,
        current_sequence=current_sequence,
        consumed_token_ids=consumed_token_ids,
        expected=expected_context,
    )
    if not token_result["valid"]:
        p.extend(f"TOKEN:{x}" for x in token_result["problems"])
    outcome = record.get("outcome")
    if outcome not in {"EFFECT_AUTHORIZED_ONCE", "REJECTED"}:
        p.append("EFFECT_GATEWAY_OUTCOME_INVALID")
    if p and outcome == "EFFECT_AUTHORIZED_ONCE":
        p.append("EFFECT_GATEWAY_FALSE_GREEN_AUTHORIZATION")
    if not p and outcome != "EFFECT_AUTHORIZED_ONCE":
        p.append("EFFECT_GATEWAY_VALID_CONTEXT_NOT_AUTHORIZED_ONCE")
    supplied = record.get("decision_digest")
    if not _sha256(supplied):
        p.append("EFFECT_GATEWAY_DECISION_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "decision_digest"):
        p.append("EFFECT_GATEWAY_DECISION_DIGEST_MISMATCH")
    out = _finish(p, "EXTERNAL_EFFECT_GATEWAY_VALID", "EXTERNAL_EFFECT_GATEWAY_INVALID")
    out["effect_authorized"] = bool(out["valid"] and outcome == "EFFECT_AUTHORIZED_ONCE")
    return out


def validate_taint_provenance_graph(
    graph: Mapping[str, Any],
    *,
    clean_package_artifact_ids: Sequence[str],
) -> dict[str, Any]:
    p: list[str] = []
    if graph.get("schema_version") != 1:
        p.append("TAINT_GRAPH_SCHEMA_INVALID")
    for key in ("graph_id", "generation_id", "snapshot_id"):
        if not _nonempty(graph.get(key)):
            p.append(f"TAINT_GRAPH_FIELD_REQUIRED:{key}")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        nodes = []
        p.append("TAINT_GRAPH_NODES_REQUIRED")
    if not isinstance(edges, list):
        edges = []
        p.append("TAINT_GRAPH_EDGES_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    outgoing: dict[str, list[str]] = {}
    tainted: set[str] = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, Mapping):
            p.append(f"TAINT_GRAPH_NODE_MALFORMED:{i}")
            continue
        nid = node.get("artifact_id")
        if not _nonempty(nid):
            p.append(f"TAINT_GRAPH_NODE_ID_REQUIRED:{i}")
            continue
        if nid in by_id:
            p.append(f"TAINT_GRAPH_NODE_DUPLICATE:{nid}")
        by_id[str(nid)] = node
        cls = node.get("provenance_class")
        if cls not in PROVENANCE_CLASSES:
            p.append(f"TAINT_GRAPH_PROVENANCE_CLASS_INVALID:{nid}")
        if node.get("candidate_controlled_provenance_label") is not False:
            p.append(f"TAINT_GRAPH_CANDIDATE_PROVENANCE_LABEL_FORBIDDEN:{nid}")
        if not _sha256(node.get("content_digest")):
            p.append(f"TAINT_GRAPH_CONTENT_DIGEST_INVALID:{nid}")
        if cls == "POST_REVIEW_FINDING":
            tainted.add(str(nid))
    for i, edge in enumerate(edges):
        if not isinstance(edge, Mapping):
            p.append(f"TAINT_GRAPH_EDGE_MALFORMED:{i}")
            continue
        src, dst = edge.get("from_artifact_id"), edge.get("to_artifact_id")
        if src not in by_id or dst not in by_id:
            p.append(f"TAINT_GRAPH_EDGE_UNKNOWN_NODE:{i}")
            continue
        if edge.get("relation") not in {"DERIVED_FROM", "SUMMARIZES", "TRANSFORMS", "EXTRACTS", "IMPORTS"}:
            p.append(f"TAINT_GRAPH_EDGE_RELATION_INVALID:{i}")
        outgoing.setdefault(str(src), []).append(str(dst))
    q = deque(sorted(tainted))
    while q:
        src = q.popleft()
        for dst in outgoing.get(src, []):
            if dst not in tainted:
                tainted.add(dst)
                q.append(dst)

    clean = set(clean_package_artifact_ids)
    for aid in sorted(clean):
        node = by_id.get(aid)
        if node is None:
            p.append(f"TAINT_GRAPH_CLEAN_PACKAGE_ARTIFACT_UNKNOWN:{aid}")
            continue
        cls = node.get("provenance_class")
        if aid in tainted:
            p.append(f"TAINT_GRAPH_POST_REVIEW_TAINT_IN_CLEAN_PACKAGE:{aid}")
        if cls not in CLEAN_PACKAGE_ALLOWED_CLASSES:
            p.append(f"TAINT_GRAPH_CLEAN_PACKAGE_PROVENANCE_FORBIDDEN:{aid}:{cls}")
        if node.get("source_allowlisted") is not True:
            p.append(f"TAINT_GRAPH_CLEAN_PACKAGE_SOURCE_NOT_ALLOWLISTED:{aid}")
    supplied = graph.get("graph_digest")
    if not _sha256(supplied):
        p.append("TAINT_GRAPH_DIGEST_INVALID")
    elif supplied != _sealed_digest(graph, "graph_digest"):
        p.append("TAINT_GRAPH_DIGEST_MISMATCH")
    out = _finish(p, "TAINT_PROVENANCE_GRAPH_VALID", "TAINT_PROVENANCE_GRAPH_INVALID")
    out["tainted_artifact_ids"] = sorted(tainted)
    out["clean_package_ready"] = out["valid"]
    return out


def validate_implementation_stopping_rule(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("IMPLEMENTATION_STOPPING_RULE_SCHEMA_INVALID")
    required_true = (
        "all_mandatory_schemas_exist",
        "construction_tests_green",
        "all_adversarial_tests_executed",
        "no_unresolved_critical_high",
        "historical_reds_preserved",
        "exact_candidate_frozen",
        "evidence_package_bound_to_candidate_environment",
        "reviewer_safe_projection_built",
        "fresh_independent_evidence_review_required_next",
    )
    for key in required_true:
        if record.get(key) is not True:
            p.append(f"IMPLEMENTATION_STOPPING_RULE_REQUIRED_TRUE:{key}")
    if record.get("runtime_qualification_state") != "NOT_CLAIMED":
        p.append("IMPLEMENTATION_STOPPING_RULE_RUNTIME_AUTHORITY_CLAIMED")
    if record.get("scientific_execution_state") not in {
        "CLOSED_PENDING_INDEPENDENT_EVIDENCE_REVIEW",
        "NOT_AUTHORIZED",
    }:
        p.append("IMPLEMENTATION_STOPPING_RULE_SCIENTIFIC_EXECUTION_NOT_CLOSED")
    v = record.get("candidate_commit")
    if not isinstance(v, str) or len(v) != 40 or any(c not in "0123456789abcdef" for c in v):
        p.append("IMPLEMENTATION_STOPPING_RULE_SHA40_INVALID:candidate_commit")
    for key in ("candidate_tree_digest", "environment_digest", "evidence_package_digest", "projection_digest"):
        if not _sha256(record.get(key)):
            p.append(f"IMPLEMENTATION_STOPPING_RULE_SHA256_INVALID:{key}")
    if not isinstance(record.get("historical_red_count"), int) or record.get("historical_red_count") < 0:
        p.append("IMPLEMENTATION_STOPPING_RULE_RED_COUNT_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("IMPLEMENTATION_STOPPING_RULE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("IMPLEMENTATION_STOPPING_RULE_DIGEST_MISMATCH")
    out = _finish(p, "IMPLEMENTATION_STOPPING_RULE_SATISFIED", "IMPLEMENTATION_STOPPING_RULE_NOT_SATISFIED")
    out["ready_for_independent_evidence_review"] = out["valid"]
    return out


def effects_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_EFFECT_GATEWAY_TAINT_STOPPING_CONSTRUCTION_READY",
        "implemented_surfaces": [30, 31, 32, 33],
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
