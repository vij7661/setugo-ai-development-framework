"""Minimal invariant/dependency graph for EXP-E change-impact falsification.

Graph convention: each edge points from a dependent artifact to the artifact it
depends on. If REQ-2 depends on INV-1, the edge is REQ-2 -> INV-1. A change to
INV-1 therefore invalidates REQ-2 and every transitive dependent of REQ-2.

This module is deliberately semantic-model agnostic. It does deterministic graph
integrity, impact propagation, missing-edge checks when a relationship is supplied
as evidence, and stale-evidence invalidation. It does not pretend that graph
reachability alone can infer whether natural-language requirements contradict.
"""
from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy


def validate_graph(graph: dict) -> None:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("graph requires nodes and edges lists")

    ids = [n.get("id") for n in nodes]
    if any(not x for x in ids):
        raise ValueError("every node requires a non-empty id")
    if len(ids) != len(set(ids)):
        raise ValueError("node ids must be unique")

    known = set(ids)
    seen_edges: set[tuple[str, str, str]] = set()
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        relation = edge.get("relation")
        if source not in known or target not in known:
            raise ValueError(f"dangling edge: {source}->{target}")
        if source == target:
            raise ValueError(f"self edge is not allowed: {source}")
        if not relation:
            raise ValueError("edge relation is required")
        key = (source, target, relation)
        if key in seen_edges:
            raise ValueError(f"duplicate edge: {key}")
        seen_edges.add(key)


def transitive_dependents(graph: dict, changed_node_ids: list[str] | set[str], *, include_changed: bool = True) -> list[str]:
    """Return deterministic transitive reverse impact for changed nodes."""
    validate_graph(graph)
    known = {n["id"] for n in graph["nodes"]}
    changed = set(changed_node_ids)
    unknown = sorted(changed - known)
    if unknown:
        raise ValueError("unknown changed node ids: " + ",".join(unknown))

    reverse: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        reverse[edge["to"]].add(edge["from"])

    impacted = set(changed if include_changed else [])
    queue = deque(sorted(changed))
    visited = set(changed)
    while queue:
        dependency = queue.popleft()
        for dependent in sorted(reverse.get(dependency, set())):
            impacted.add(dependent)
            if dependent not in visited:
                visited.add(dependent)
                queue.append(dependent)
    return sorted(impacted)


def stale_evidence(graph: dict, changed_node_ids: list[str] | set[str]) -> list[str]:
    """Return evidence IDs bound to changed or transitively impacted artifacts."""
    impacted = set(transitive_dependents(graph, changed_node_ids))
    stale = []
    for item in graph.get("evidence", []):
        if item.get("artifact_id") in impacted and item.get("id"):
            stale.append(item["id"])
    return sorted(set(stale))


def missing_declared_relationships(graph: dict, relationships: list[dict]) -> list[dict]:
    """Compare evidence-declared relationships with the authoritative graph.

    The function does not invent relationships. It only detects that an explicit
    relationship supplied by authoritative evidence is absent from the graph.
    """
    validate_graph(graph)
    known = {n["id"] for n in graph["nodes"]}
    existing = {(e["from"], e["to"], e["relation"]) for e in graph["edges"]}
    missing = []
    for rel in relationships:
        source, target, relation = rel.get("from"), rel.get("to"), rel.get("relation")
        if source not in known or target not in known:
            raise ValueError(f"declared relationship references unknown node: {source}->{target}")
        key = (source, target, relation)
        if key not in existing:
            missing.append(deepcopy(rel))
    return missing


def invalidation_plan(graph: dict, changed_node_ids: list[str] | set[str]) -> dict:
    """Build deterministic change-impact invalidation evidence."""
    impacted = transitive_dependents(graph, changed_node_ids)
    return {
        "changed_nodes": sorted(set(changed_node_ids)),
        "impacted_nodes": impacted,
        "stale_evidence": stale_evidence(graph, changed_node_ids),
    }
