"""V24 I11 V6 remediation R1: generic governance foundation.

Construction-only implementation of the exact approved V6 design foundation.
This module validates governance records and invariants. It does not grant
runtime, qualification, release, deployment, production, or terminal authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"

QUALIFIED = "QUALIFIED"
INVALID = "INVALID"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
CURRENT = "CURRENT"
STALE = "STALE"

COMPLETENESS_DERIVATION_REJECTION = (
    "COMPLETENESS_DERIVATION_CYCLE_OR_UNROOTED_SOURCE_REJECTED"
)
GENESIS_TRUST_SCOPE_REJECTION = "GENESIS_TRUST_SCOPE_MISMATCH_REJECTED"

ALLOWED_COMPLETENESS_ROOT_KINDS = frozenset(
    {
        "IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY",
        "RUNTIME_MATERIAL_OBSERVATION_LEDGER",
        "EFFECT_PATH_OBSERVATION",
        "CONTROL_PLANE_OBSERVATION",
        "DURABLE_STORE_DATABASE_OFFLINE_RECOVERY_OBSERVATION",
        "NORMATIVE_ARTIFACT_BYTES_STRUCTURE",
        "GENESIS_ROOT_ARTIFACT",
    }
)

QUALIFICATION_RESULTS = frozenset({QUALIFIED, INVALID, INSUFFICIENT_EVIDENCE})
CURRENTNESS_RESULTS = frozenset({CURRENT, STALE, INSUFFICIENT_EVIDENCE})
INDEPENDENCE_RESULTS = frozenset({QUALIFIED, "CONFLICT", INSUFFICIENT_EVIDENCE})


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _unique_strings(value: Any) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    if not isinstance(value, list):
        return [], ["LIST_REQUIRED"]
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not _nonempty_str(item):
            problems.append("STRING_MEMBER_INVALID")
            continue
        if item in seen:
            problems.append(f"DUPLICATE_MEMBER:{item}")
        else:
            seen.add(item)
            out.append(item)
    return out, problems


def _record_digest(record: Mapping[str, Any], digest_field: str) -> str:
    material = dict(record)
    material.pop(digest_field, None)
    return digest(material)


def validate_governed_object_envelope(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "object_id",
        "object_kind",
        "governance_generation_id",
        "schema_id",
        "schema_version",
        "object_version",
        "content_digest",
        "currentness_rule_id",
        "authority_owner_id",
        "authority_owner_control_domain_id",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"GOVERNED_OBJECT_FIELD_REQUIRED:{key}")
    if record.get("predecessor_object_digest") is not None and not _is_sha256(
        record.get("predecessor_object_digest")
    ):
        p.append("GOVERNED_OBJECT_PREDECESSOR_DIGEST_INVALID")
    if not _is_sha256(record.get("content_digest")):
        p.append("GOVERNED_OBJECT_CONTENT_DIGEST_INVALID")
    seq = record.get("activation_sequence")
    if not isinstance(seq, int) or seq < 0:
        p.append("GOVERNED_OBJECT_ACTIVATION_SEQUENCE_INVALID")
    return sorted(set(p))


def validate_currentness_binding(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "currentness_rule_id",
        "source_object_id",
        "source_version_or_sequence",
        "source_digest",
        "verifier_qualification_digest",
        "binding_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"CURRENTNESS_FIELD_REQUIRED:{key}")
    if not _is_sha256(record.get("source_digest")):
        p.append("CURRENTNESS_SOURCE_DIGEST_INVALID")
    if not _is_sha256(record.get("verifier_qualification_digest")):
        p.append("CURRENTNESS_VERIFIER_QUALIFICATION_DIGEST_INVALID")
    if record.get("result") not in CURRENTNESS_RESULTS:
        p.append("CURRENTNESS_RESULT_INVALID")
    observed = record.get("observed_at_sequence")
    if not isinstance(observed, int) or observed < 0:
        p.append("CURRENTNESS_OBSERVED_SEQUENCE_INVALID")
    supplied = record.get("binding_digest")
    if _is_sha256(supplied) and supplied != _record_digest(record, "binding_digest"):
        p.append("CURRENTNESS_BINDING_DIGEST_MISMATCH")
    return sorted(set(p))


def validate_evidence_class_descriptor(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "evidence_class_id",
        "control_id",
        "schema_version",
        "required_independence_rule_id",
        "currentness_rule_id",
        "evidence_schema_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"EVIDENCE_CLASS_FIELD_REQUIRED:{key}")
    if not _is_sha256(record.get("evidence_schema_digest")):
        p.append("EVIDENCE_CLASS_SCHEMA_DIGEST_INVALID")
    for key in (
        "allowed_source_kinds",
        "allowed_producer_component_classes",
        "required_identity_fields",
        "required_anchor_fields",
    ):
        values, problems = _unique_strings(record.get(key))
        if not values:
            p.append(f"EVIDENCE_CLASS_NONEMPTY_SET_REQUIRED:{key}")
        p.extend(f"{key}:{item}" for item in problems)
    return sorted(set(p))


def validate_mechanism_descriptor(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "mechanism_id",
        "mechanism_kind",
        "governance_generation_id",
        "rule_or_algorithm_digest",
        "owner_id",
        "owner_control_domain_id",
        "descriptor_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"MECHANISM_FIELD_REQUIRED:{key}")
    for key in ("implementation_content_digests", "input_schema_ids", "output_schema_ids"):
        values, problems = _unique_strings(record.get(key))
        if not values:
            p.append(f"MECHANISM_NONEMPTY_SET_REQUIRED:{key}")
        p.extend(f"{key}:{item}" for item in problems)
    if not _is_sha256(record.get("rule_or_algorithm_digest")):
        p.append("MECHANISM_ALGORITHM_DIGEST_INVALID")
    impl = record.get("implementation_content_digests")
    if isinstance(impl, list) and not all(_is_sha256(x) for x in impl):
        p.append("MECHANISM_IMPLEMENTATION_DIGEST_INVALID")
    supplied = record.get("descriptor_digest")
    if _is_sha256(supplied) and supplied != _record_digest(record, "descriptor_digest"):
        p.append("MECHANISM_DESCRIPTOR_DIGEST_MISMATCH")
    return sorted(set(p))


def validate_independence_qualification(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "independence_qualification_id",
        "independence_rule_id",
        "subject_identity_id",
        "verifier_qualification_digest",
        "qualification_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"INDEPENDENCE_FIELD_REQUIRED:{key}")
    subject_controls, subject_problems = _unique_strings(record.get("subject_control_closure"))
    p.extend(f"SUBJECT_CONTROL:{x}" for x in subject_problems)
    counterparties = record.get("counterparties")
    if not isinstance(counterparties, list) or not counterparties:
        p.append("INDEPENDENCE_COUNTERPARTIES_REQUIRED")
        counterparties = []
    actual_intersections: set[str] = set()
    cp_ids: set[str] = set()
    for cp in counterparties:
        if not isinstance(cp, Mapping):
            p.append("INDEPENDENCE_COUNTERPARTY_MALFORMED")
            continue
        cid = cp.get("identity_id")
        if not _nonempty_str(cid):
            p.append("INDEPENDENCE_COUNTERPARTY_ID_REQUIRED")
            continue
        if cid in cp_ids:
            p.append(f"INDEPENDENCE_COUNTERPARTY_DUPLICATE:{cid}")
        cp_ids.add(cid)
        controls, problems = _unique_strings(cp.get("control_closure"))
        p.extend(f"COUNTERPARTY_CONTROL:{cid}:{x}" for x in problems)
        actual_intersections.update(set(subject_controls).intersection(controls))
    declared, declared_problems = _unique_strings(record.get("shared_control_intersections"))
    p.extend(f"INDEPENDENCE_DECLARED_INTERSECTION:{x}" for x in declared_problems)
    if set(declared) != actual_intersections:
        p.append("INDEPENDENCE_INTERSECTION_PROOF_MISMATCH")
    result = record.get("result")
    if result not in INDEPENDENCE_RESULTS:
        p.append("INDEPENDENCE_RESULT_INVALID")
    if result == QUALIFIED and actual_intersections:
        p.append("INDEPENDENCE_QUALIFIED_WITH_SHARED_CONTROL")
    evidence, evidence_problems = _unique_strings(record.get("evidence_record_digests"))
    p.extend(f"INDEPENDENCE_EVIDENCE:{x}" for x in evidence_problems)
    if not evidence or not all(_is_sha256(x) for x in evidence):
        p.append("INDEPENDENCE_EVIDENCE_DIGESTS_INVALID")
    currentness = record.get("currentness_bindings")
    if not isinstance(currentness, list) or not currentness:
        p.append("INDEPENDENCE_CURRENTNESS_REQUIRED")
    else:
        for idx, item in enumerate(currentness):
            if not isinstance(item, Mapping):
                p.append(f"INDEPENDENCE_CURRENTNESS_MALFORMED:{idx}")
                continue
            for problem in validate_currentness_binding(item):
                p.append(f"INDEPENDENCE_CURRENTNESS:{idx}:{problem}")
            if result == QUALIFIED and item.get("result") != CURRENT:
                p.append(f"INDEPENDENCE_QUALIFIED_WITH_NONCURRENT_BINDING:{idx}")
    if not _is_sha256(record.get("verifier_qualification_digest")):
        p.append("INDEPENDENCE_VERIFIER_QUALIFICATION_DIGEST_INVALID")
    supplied = record.get("qualification_digest")
    if _is_sha256(supplied) and supplied != _record_digest(record, "qualification_digest"):
        p.append("INDEPENDENCE_QUALIFICATION_DIGEST_MISMATCH")
    return sorted(set(p))


def validate_governed_qualification(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "qualification_id",
        "subject_object_id",
        "subject_content_digest",
        "subject_kind",
        "qualification_authority_id",
        "subject_owner_id",
        "verifier_mechanism_id",
        "verifier_mechanism_qualification_digest",
        "proof_digest",
        "qualification_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"QUALIFICATION_FIELD_REQUIRED:{key}")
    if not _is_sha256(record.get("subject_content_digest")):
        p.append("QUALIFICATION_SUBJECT_DIGEST_INVALID")
    if record.get("result") not in QUALIFICATION_RESULTS:
        p.append("QUALIFICATION_RESULT_INVALID")
    subject_id = record.get("subject_object_id")
    subject_owner = record.get("subject_owner_id")
    authority_id = record.get("qualification_authority_id")
    verifier_id = record.get("verifier_mechanism_id")
    if authority_id in {subject_id, subject_owner}:
        p.append("QUALIFICATION_SELF_AUTHORITY_FORBIDDEN")
    if verifier_id == subject_id:
        p.append("QUALIFICATION_SELF_VERIFIER_FORBIDDEN")
    for key in (
        "authority_member_ids",
        "authority_control_domain_ids",
        "independence_qualification_digests",
        "evidence_record_digests",
        "evidence_class_ids",
    ):
        values, problems = _unique_strings(record.get(key))
        if not values:
            p.append(f"QUALIFICATION_NONEMPTY_SET_REQUIRED:{key}")
        p.extend(f"{key}:{item}" for item in problems)
        if key.endswith("_digests") and values and not all(_is_sha256(x) for x in values):
            p.append(f"QUALIFICATION_DIGEST_SET_INVALID:{key}")
    currentness = record.get("currentness_bindings")
    if not isinstance(currentness, list) or not currentness:
        p.append("QUALIFICATION_CURRENTNESS_REQUIRED")
    else:
        for idx, item in enumerate(currentness):
            if not isinstance(item, Mapping):
                p.append(f"QUALIFICATION_CURRENTNESS_MALFORMED:{idx}")
                continue
            for problem in validate_currentness_binding(item):
                p.append(f"QUALIFICATION_CURRENTNESS:{idx}:{problem}")
            if record.get("result") == QUALIFIED and item.get("result") != CURRENT:
                p.append(f"QUALIFICATION_QUALIFIED_WITH_NONCURRENT_BINDING:{idx}")
    if not _is_sha256(record.get("verifier_mechanism_qualification_digest")):
        p.append("QUALIFICATION_VERIFIER_DIGEST_INVALID")
    if not _is_sha256(record.get("proof_digest")):
        p.append("QUALIFICATION_PROOF_DIGEST_INVALID")
    supplied = record.get("qualification_digest")
    if _is_sha256(supplied) and supplied != _record_digest(record, "qualification_digest"):
        p.append("QUALIFICATION_DIGEST_MISMATCH")
    return sorted(set(p))


def validate_completeness_derivation_graph(graph: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    nodes_raw = graph.get("nodes")
    edges_raw = graph.get("edges")
    if not isinstance(nodes_raw, list) or not nodes_raw:
        nodes_raw = []
        p.append("COMPLETENESS_GRAPH_NODES_REQUIRED")
    if not isinstance(edges_raw, list):
        edges_raw = []
        p.append("COMPLETENESS_GRAPH_EDGES_REQUIRED")

    nodes: dict[str, Mapping[str, Any]] = {}
    for node in nodes_raw:
        if not isinstance(node, Mapping):
            p.append("COMPLETENESS_GRAPH_NODE_MALFORMED")
            continue
        node_id = node.get("node_id")
        if not _nonempty_str(node_id):
            p.append("COMPLETENESS_GRAPH_NODE_ID_REQUIRED")
            continue
        if node_id in nodes:
            p.append(f"COMPLETENESS_GRAPH_NODE_DUPLICATE:{node_id}")
            continue
        nodes[node_id] = node

    adjacency: dict[str, set[str]] = {node_id: set() for node_id in nodes}
    for edge in edges_raw:
        if not isinstance(edge, Mapping):
            p.append("COMPLETENESS_GRAPH_EDGE_MALFORMED")
            continue
        src, dst = edge.get("from"), edge.get("to")
        if src not in nodes or dst not in nodes:
            p.append(f"COMPLETENESS_GRAPH_EDGE_UNKNOWN_NODE:{src}:{dst}")
            continue
        if src == dst:
            p.append(f"COMPLETENESS_GRAPH_SELF_EDGE:{src}")
        adjacency[src].add(dst)

    color: dict[str, int] = {node_id: 0 for node_id in nodes}
    cycle = False

    def visit(node_id: str) -> None:
        nonlocal cycle
        color[node_id] = 1
        for nxt in adjacency[node_id]:
            if color[nxt] == 1:
                cycle = True
            elif color[nxt] == 0:
                visit(nxt)
        color[node_id] = 2

    for node_id in nodes:
        if color[node_id] == 0:
            visit(node_id)
    if cycle:
        p.append(COMPLETENESS_DERIVATION_REJECTION)

    terminals = {node_id for node_id, deps in adjacency.items() if not deps}
    allowed_roots: set[str] = set()
    for node_id in terminals:
        node = nodes[node_id]
        root_kind = node.get("root_kind")
        omission_sensitive = node.get("omission_sensitive")
        source_digest = node.get("source_surface_digest")
        if (
            root_kind in ALLOWED_COMPLETENESS_ROOT_KINDS
            and omission_sensitive is False
            and _is_sha256(source_digest)
        ):
            allowed_roots.add(node_id)
        else:
            p.append(f"COMPLETENESS_GRAPH_DISALLOWED_TERMINAL:{node_id}")

    memo: dict[str, set[str]] = {}

    def reachable_terminals(node_id: str, stack: set[str]) -> set[str]:
        if node_id in memo:
            return memo[node_id]
        if node_id in stack:
            return set()
        deps = adjacency[node_id]
        if not deps:
            memo[node_id] = {node_id}
            return memo[node_id]
        out: set[str] = set()
        next_stack = set(stack)
        next_stack.add(node_id)
        for nxt in deps:
            out.update(reachable_terminals(nxt, next_stack))
        memo[node_id] = out
        return out

    subject_nodes = {
        node_id
        for node_id, node in nodes.items()
        if node.get("omission_sensitive") is True
    }
    for subject in subject_nodes:
        reachable = reachable_terminals(subject, set())
        if not reachable or not reachable.issubset(allowed_roots):
            p.append(COMPLETENESS_DERIVATION_REJECTION)
            p.append(f"COMPLETENESS_GRAPH_SUBJECT_NOT_UNIVERSALLY_ROOTED:{subject}")

    def depends_on(start: str, target: str, seen: set[str]) -> bool:
        if start in seen:
            return False
        seen.add(start)
        for nxt in adjacency[start]:
            if nxt == target or depends_on(nxt, target, seen):
                return True
        return False

    for subject in subject_nodes:
        if depends_on(subject, subject, set()):
            p.append(COMPLETENESS_DERIVATION_REJECTION)
            p.append(f"COMPLETENESS_GRAPH_TRANSITIVE_SELF_DEPENDENCY:{subject}")

    p = sorted(set(p))
    return {
        "state": "COMPLETENESS_DERIVATION_GRAPH_VALID" if not p else "COMPLETENESS_DERIVATION_GRAPH_INVALID",
        "problems": p,
        "terminals": sorted(terminals),
        "allowed_roots": sorted(allowed_roots),
        "graph_digest": digest(graph),
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_registry_completeness_qualification(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "subject_object_id",
        "subject_content_digest",
        "expected_member_set_digest",
        "actual_member_set_digest",
        "set_equality_proof_digest",
        "verifier_qualification_digest",
        "qualification_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"REGISTRY_COMPLETENESS_FIELD_REQUIRED:{key}")
    for key in (
        "subject_content_digest",
        "expected_member_set_digest",
        "actual_member_set_digest",
        "set_equality_proof_digest",
        "verifier_qualification_digest",
    ):
        if not _is_sha256(record.get(key)):
            p.append(f"REGISTRY_COMPLETENESS_DIGEST_INVALID:{key}")

    expected, expected_problems = _unique_strings(record.get("expected_members"))
    actual, actual_problems = _unique_strings(record.get("actual_members"))
    p.extend(f"EXPECTED_MEMBERS:{x}" for x in expected_problems)
    p.extend(f"ACTUAL_MEMBERS:{x}" for x in actual_problems)
    expected_canon = sorted(expected)
    actual_canon = sorted(actual)
    if _is_sha256(record.get("expected_member_set_digest")) and record.get(
        "expected_member_set_digest"
    ) != digest(expected_canon):
        p.append("REGISTRY_COMPLETENESS_EXPECTED_SET_DIGEST_MISMATCH")
    if _is_sha256(record.get("actual_member_set_digest")) and record.get(
        "actual_member_set_digest"
    ) != digest(actual_canon):
        p.append("REGISTRY_COMPLETENESS_ACTUAL_SET_DIGEST_MISMATCH")
    if expected_canon != actual_canon:
        p.append("REGISTRY_COMPLETENESS_SET_EQUALITY_FAILED")

    graph = record.get("completeness_derivation_graph")
    if not isinstance(graph, Mapping):
        p.append("REGISTRY_COMPLETENESS_DERIVATION_GRAPH_REQUIRED")
    else:
        graph_result = validate_completeness_derivation_graph(graph)
        for problem in graph_result["problems"]:
            p.append(f"REGISTRY_COMPLETENESS_GRAPH:{problem}")
        target = record.get("subject_object_id")
        graph_nodes = {
            node.get("node_id")
            for node in graph.get("nodes", [])
            if isinstance(node, Mapping)
        }
        if target not in graph_nodes:
            p.append("REGISTRY_COMPLETENESS_SUBJECT_NOT_IN_DERIVATION_GRAPH")

    for key in (
        "derivation_mechanism_qualification_digests",
        "derivation_authority_independence_digests",
        "source_surface_digests",
    ):
        values, problems = _unique_strings(record.get(key))
        if not values:
            p.append(f"REGISTRY_COMPLETENESS_NONEMPTY_SET_REQUIRED:{key}")
        p.extend(f"{key}:{x}" for x in problems)
        if values and not all(_is_sha256(x) for x in values):
            p.append(f"REGISTRY_COMPLETENESS_DIGEST_SET_INVALID:{key}")

    currentness = record.get("currentness_bindings")
    if not isinstance(currentness, list) or not currentness:
        p.append("REGISTRY_COMPLETENESS_CURRENTNESS_REQUIRED")
    else:
        for idx, item in enumerate(currentness):
            if not isinstance(item, Mapping):
                p.append(f"REGISTRY_COMPLETENESS_CURRENTNESS_MALFORMED:{idx}")
                continue
            for problem in validate_currentness_binding(item):
                p.append(f"REGISTRY_COMPLETENESS_CURRENTNESS:{idx}:{problem}")
            if record.get("result") == QUALIFIED and item.get("result") != CURRENT:
                p.append(f"REGISTRY_COMPLETENESS_QUALIFIED_WITH_NONCURRENT_BINDING:{idx}")

    if record.get("result") not in QUALIFICATION_RESULTS:
        p.append("REGISTRY_COMPLETENESS_RESULT_INVALID")
    if record.get("result") == QUALIFIED and p:
        p.append("REGISTRY_COMPLETENESS_FALSE_QUALIFIED_RESULT")
    supplied = record.get("qualification_digest")
    if _is_sha256(supplied) and supplied != _record_digest(record, "qualification_digest"):
        p.append("REGISTRY_COMPLETENESS_QUALIFICATION_DIGEST_MISMATCH")
    return sorted(set(p))


def validate_genesis_trusted_scope(record: Mapping[str, Any]) -> list[str]:
    p: list[str] = []
    for key in (
        "governance_generation_id",
        "genesis_record_digest",
        "root_kernel_digest",
        "trusted_object_pair_set_digest",
        "creation_ceremony_digest",
        "durable_anchor_digest",
        "scope_digest",
    ):
        if not _nonempty_str(record.get(key)):
            p.append(f"GENESIS_SCOPE_FIELD_REQUIRED:{key}")
    for key in (
        "genesis_record_digest",
        "root_kernel_digest",
        "trusted_object_pair_set_digest",
        "creation_ceremony_digest",
        "durable_anchor_digest",
    ):
        if not _is_sha256(record.get(key)):
            p.append(f"GENESIS_SCOPE_DIGEST_INVALID:{key}")
    trusted = record.get("trusted_objects")
    if not isinstance(trusted, list) or not trusted:
        trusted = []
        p.append("GENESIS_SCOPE_TRUSTED_OBJECTS_REQUIRED")
    pairs: list[dict[str, str]] = []
    ids: set[str] = set()
    pair_keys: set[tuple[str, str]] = set()
    for item in trusted:
        if not isinstance(item, Mapping):
            p.append("GENESIS_SCOPE_TRUSTED_OBJECT_MALFORMED")
            continue
        object_id = item.get("object_id")
        content_digest = item.get("content_digest")
        if not _nonempty_str(object_id):
            p.append("GENESIS_SCOPE_TRUSTED_OBJECT_ID_REQUIRED")
            continue
        if not _is_sha256(content_digest):
            p.append(f"GENESIS_SCOPE_TRUSTED_OBJECT_DIGEST_INVALID:{object_id}")
            continue
        pair = (object_id, content_digest)
        if pair in pair_keys:
            p.append(f"GENESIS_SCOPE_TRUSTED_PAIR_DUPLICATE:{object_id}:{content_digest}")
        pair_keys.add(pair)
        if object_id in ids:
            p.append(f"GENESIS_SCOPE_OBJECT_ID_AMBIGUOUS:{object_id}")
        ids.add(object_id)
        pairs.append({"object_id": object_id, "content_digest": content_digest})
    canonical_pairs = sorted(pairs, key=lambda x: (x["object_id"], x["content_digest"]))
    if _is_sha256(record.get("trusted_object_pair_set_digest")) and record.get(
        "trusted_object_pair_set_digest"
    ) != digest(canonical_pairs):
        p.append("GENESIS_SCOPE_PAIR_SET_DIGEST_MISMATCH")
    roles, role_problems = _unique_strings(record.get("permitted_bootstrap_roles"))
    reasons, reason_problems = _unique_strings(record.get("residual_trust_reason_ids"))
    if not roles:
        p.append("GENESIS_SCOPE_BOOTSTRAP_ROLES_REQUIRED")
    if not reasons:
        p.append("GENESIS_SCOPE_RESIDUAL_TRUST_REASONS_REQUIRED")
    p.extend(f"GENESIS_SCOPE_ROLE:{x}" for x in role_problems)
    p.extend(f"GENESIS_SCOPE_REASON:{x}" for x in reason_problems)
    supplied = record.get("scope_digest")
    if _is_sha256(supplied) and supplied != _record_digest(record, "scope_digest"):
        p.append("GENESIS_SCOPE_DIGEST_MISMATCH")
    return sorted(set(p))


def genesis_scope_match(
    record: Mapping[str, Any],
    *,
    object_id: str,
    content_digest: str,
) -> dict[str, Any]:
    problems = validate_genesis_trusted_scope(record)
    if problems:
        return {
            "matched": False,
            "endpoint": GENESIS_TRUST_SCOPE_REJECTION,
            "problems": problems,
            "authority_effect": AUTHORITY_EFFECT,
        }
    matched = any(
        isinstance(item, Mapping)
        and item.get("object_id") == object_id
        and item.get("content_digest") == content_digest
        for item in record["trusted_objects"]
    )
    return {
        "matched": matched,
        "endpoint": None if matched else GENESIS_TRUST_SCOPE_REJECTION,
        "problems": [] if matched else [GENESIS_TRUST_SCOPE_REJECTION],
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    """Construction-only statement; does not qualify runtime authority."""
    return {
        "state": "V24_V6_R1_GOVERNANCE_FOUNDATION_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R1",
        "authority_effect": AUTHORITY_EFFECT,
    }
