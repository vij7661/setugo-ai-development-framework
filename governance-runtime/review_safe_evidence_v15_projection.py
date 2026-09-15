#!/usr/bin/env python3
"""V15 obligation/materiality, reviewer-safe projection, and disclosure completeness.

Construction-stage implementation only. No authority effect.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    canonical_hash,
    validate_independently_rooted_proof,
)

PROJECTION_MODES = frozenset({"EXACT", "STRUCTURED_REDACTION"})
DISCLOSURE_STATES = frozenset({"COMPLETE_REVIEWABLE_VIEW", "INSUFFICIENT_TO_ASSESS"})


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _sealed_digest(record: Mapping[str, Any], field: str) -> str:
    return canonical_hash({k: v for k, v in record.items() if k != field})


def _result(problems: list[str], ok: str, bad: str) -> dict[str, Any]:
    p = sorted(set(problems))
    return {
        "state": ok if not p else bad,
        "valid": not p,
        "qualified": False,
        "problems": p,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_obligation_record(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("OBLIGATION_SCHEMA_INVALID")
    for key in (
        "obligation_id", "dimension_id", "proposition_id", "generation_id",
        "materiality_authority_id", "materiality_control_domain_id", "currentness_rule",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"OBLIGATION_FIELD_REQUIRED:{key}")
    if record.get("candidate_controlled") is not False:
        p.append("OBLIGATION_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("currentness_state") != "CURRENT":
        p.append("OBLIGATION_NOT_CURRENT")

    load = record.get("load_bearing_fields")
    nonload = record.get("non_load_bearing_fields")
    relations = record.get("load_bearing_relations")
    required_evidence = record.get("required_evidence_ids")
    for label, value, allow_empty in (
        ("LOAD_BEARING_FIELDS", load, False),
        ("NON_LOAD_BEARING_FIELDS", nonload, True),
        ("LOAD_BEARING_RELATIONS", relations, True),
        ("REQUIRED_EVIDENCE_IDS", required_evidence, False),
    ):
        if not isinstance(value, list) or (not allow_empty and not value) or not all(_nonempty(x) for x in value):
            p.append(f"OBLIGATION_{label}_INVALID")
    if isinstance(load, list) and isinstance(nonload, list) and set(load) & set(nonload):
        p.append("OBLIGATION_FIELD_MATERIALITY_OVERLAP")
    if isinstance(load, list) and len(load) != len(set(load)):
        p.append("OBLIGATION_LOAD_BEARING_FIELD_DUPLICATE")
    if isinstance(nonload, list) and len(nonload) != len(set(nonload)):
        p.append("OBLIGATION_NON_LOAD_BEARING_FIELD_DUPLICATE")
    if isinstance(relations, list) and len(relations) != len(set(relations)):
        p.append("OBLIGATION_RELATION_DUPLICATE")

    semantic = record.get("semantic_contract")
    if not isinstance(semantic, Mapping):
        p.append("OBLIGATION_SEMANTIC_CONTRACT_REQUIRED")
    else:
        for key in ("cardinality", "ordering", "units", "qualifiers", "provenance"):
            if not _nonempty(semantic.get(key)):
                p.append(f"OBLIGATION_SEMANTIC_FIELD_REQUIRED:{key}")

    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("OBLIGATION_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("OBLIGATION_RECORD_DIGEST_MISMATCH")
    return _result(p, "EVIDENCE_OBLIGATION_RECORD_VALID", "EVIDENCE_OBLIGATION_RECORD_INVALID")


def validate_obligation_graph(bundle: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("OBLIGATION_GRAPH_SCHEMA_INVALID")
    for key in ("graph_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"OBLIGATION_GRAPH_FIELD_REQUIRED:{key}")
    rows = bundle.get("obligations")
    if not isinstance(rows, list) or not rows:
        rows = []
        p.append("OBLIGATION_GRAPH_RECORDS_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    dimensions: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"OBLIGATION_GRAPH_RECORD_MALFORMED:{i}")
            continue
        checked = validate_obligation_record(row)
        if not checked["valid"]:
            p.extend(f"OBLIGATION[{i}]:{x}" for x in checked["problems"])
        oid = row.get("obligation_id")
        if isinstance(oid, str):
            if oid in by_id:
                p.append(f"OBLIGATION_GRAPH_ID_DUPLICATE:{oid}")
            else:
                by_id[oid] = row
        dim = row.get("dimension_id")
        if isinstance(dim, str):
            dimensions.add(dim)
        if row.get("generation_id") != bundle.get("generation_id"):
            p.append(f"OBLIGATION_GRAPH_GENERATION_MISMATCH:{oid}")
    required_dimensions = bundle.get("mandatory_dimensions")
    if not isinstance(required_dimensions, list) or not required_dimensions or not all(_nonempty(x) for x in required_dimensions):
        p.append("OBLIGATION_GRAPH_MANDATORY_DIMENSIONS_REQUIRED")
        required_dimensions = []
    for dim in sorted(set(required_dimensions) - dimensions):
        p.append(f"OBLIGATION_GRAPH_DIMENSION_UNCOVERED:{dim}")
    supplied = bundle.get("graph_digest")
    if not _sha256(supplied):
        p.append("OBLIGATION_GRAPH_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "graph_digest"):
        p.append("OBLIGATION_GRAPH_DIGEST_MISMATCH")
    out = _result(p, "EVIDENCE_OBLIGATION_GRAPH_VALID", "EVIDENCE_OBLIGATION_GRAPH_INVALID")
    out["obligation_count"] = len(by_id)
    out["dimension_count"] = len(dimensions)
    return out


def validate_raw_projection_source(raw: Mapping[str, Any], *, obligation: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if not _nonempty(raw.get("evidence_id")):
        p.append("PROJECTION_RAW_EVIDENCE_ID_REQUIRED")
    content = raw.get("content")
    relations = raw.get("relations")
    if not isinstance(content, Mapping):
        p.append("PROJECTION_RAW_CONTENT_MAPPING_REQUIRED")
        content = {}
    if not isinstance(relations, Mapping):
        p.append("PROJECTION_RAW_RELATIONS_MAPPING_REQUIRED")
        relations = {}
    if raw.get("content_digest") != canonical_hash(content):
        p.append("PROJECTION_RAW_CONTENT_DIGEST_MISMATCH")
    if raw.get("relations_digest") != canonical_hash(relations):
        p.append("PROJECTION_RAW_RELATIONS_DIGEST_MISMATCH")
    required_ids = obligation.get("required_evidence_ids", [])
    if isinstance(required_ids, list) and raw.get("evidence_id") not in required_ids:
        p.append(f"PROJECTION_RAW_EVIDENCE_NOT_REQUIRED:{raw.get('evidence_id')}")
    return _result(p, "PROJECTION_RAW_SOURCE_VALID", "PROJECTION_RAW_SOURCE_INVALID")


def validate_projection_record(record: Mapping[str, Any], *, raw: Mapping[str, Any],
                               obligation: Mapping[str, Any],
                               verifier_independence_proof: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("PROJECTION_SCHEMA_INVALID")
    for key in (
        "projection_id", "obligation_id", "raw_evidence_id", "candidate_id", "snapshot_id",
        "generation_id", "compiler_id", "compiler_control_domain_id", "verifier_id",
        "verifier_control_domain_id", "obligation_graph_digest",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"PROJECTION_FIELD_REQUIRED:{key}")
    mode = record.get("mode")
    if mode not in PROJECTION_MODES:
        p.append("PROJECTION_MODE_INVALID")
    if record.get("candidate_controlled") is not False:
        p.append("PROJECTION_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("raw_access_attested") is not True:
        p.append("PROJECTION_VERIFIER_RAW_ACCESS_REQUIRED")
    if record.get("materiality_recomputed") is not True:
        p.append("PROJECTION_MATERIALITY_RECOMPUTE_REQUIRED")
    if record.get("obligation_id") != obligation.get("obligation_id"):
        p.append("PROJECTION_OBLIGATION_MISMATCH")
    if record.get("raw_evidence_id") != raw.get("evidence_id"):
        p.append("PROJECTION_RAW_EVIDENCE_ID_MISMATCH")

    raw_checked = validate_raw_projection_source(raw, obligation=obligation)
    if not raw_checked["valid"]:
        p.extend(f"RAW:{x}" for x in raw_checked["problems"])
    obligation_checked = validate_obligation_record(obligation)
    if not obligation_checked["valid"]:
        p.extend(f"OBLIGATION:{x}" for x in obligation_checked["problems"])

    ip = validate_independently_rooted_proof(verifier_independence_proof)
    if not ip["valid"]:
        p.extend(f"VERIFIER_INDEPENDENCE:{x}" for x in ip["problems"])
    expected_domains = frozenset((str(record.get("compiler_control_domain_id")), str(record.get("verifier_control_domain_id"))))
    actual_domains = frozenset((str(verifier_independence_proof.get("subject_a")), str(verifier_independence_proof.get("subject_b"))))
    if expected_domains != actual_domains:
        p.append("PROJECTION_VERIFIER_INDEPENDENCE_SUBJECT_MISMATCH")
    if verifier_independence_proof.get("result") != "INDEPENDENT":
        p.append("PROJECTION_VERIFIER_INDEPENDENCE_REQUIRED")
    if record.get("compiler_control_domain_id") == record.get("verifier_control_domain_id"):
        p.append("PROJECTION_COMPILER_VERIFIER_DOMAIN_COLLAPSE")

    content = raw.get("content", {}) if isinstance(raw.get("content"), Mapping) else {}
    relations = raw.get("relations", {}) if isinstance(raw.get("relations"), Mapping) else {}
    projected = record.get("projected_content")
    projected_relations = record.get("projected_relations")
    omitted = record.get("omitted_fields")
    if not isinstance(projected, Mapping):
        projected = {}
        p.append("PROJECTION_PROJECTED_CONTENT_REQUIRED")
    if not isinstance(projected_relations, Mapping):
        projected_relations = {}
        p.append("PROJECTION_PROJECTED_RELATIONS_REQUIRED")
    if not isinstance(omitted, list) or not all(_nonempty(x) for x in omitted):
        omitted = []
        p.append("PROJECTION_OMITTED_FIELDS_INVALID")
    if len(omitted) != len(set(omitted)):
        p.append("PROJECTION_OMITTED_FIELD_DUPLICATE")

    load = set(obligation.get("load_bearing_fields", [])) if isinstance(obligation.get("load_bearing_fields"), list) else set()
    nonload = set(obligation.get("non_load_bearing_fields", [])) if isinstance(obligation.get("non_load_bearing_fields"), list) else set()
    load_rel = set(obligation.get("load_bearing_relations", [])) if isinstance(obligation.get("load_bearing_relations"), list) else set()

    if mode == "EXACT":
        if canonical_hash(projected) != canonical_hash(content):
            p.append("PROJECTION_EXACT_CONTENT_MISMATCH")
        if canonical_hash(projected_relations) != canonical_hash(relations):
            p.append("PROJECTION_EXACT_RELATIONS_MISMATCH")
        if omitted:
            p.append("PROJECTION_EXACT_OMISSION_FORBIDDEN")
    elif mode == "STRUCTURED_REDACTION":
        if set(omitted) - nonload:
            for field in sorted(set(omitted) - nonload):
                p.append(f"PROJECTION_LOAD_OR_UNKNOWN_FIELD_OMISSION_FORBIDDEN:{field}")
        for field in sorted(load):
            if field not in content:
                p.append(f"PROJECTION_RAW_LOAD_BEARING_FIELD_MISSING:{field}")
            elif field not in projected:
                p.append(f"PROJECTION_LOAD_BEARING_FIELD_OMITTED:{field}")
            elif projected[field] != content[field]:
                p.append(f"PROJECTION_LOAD_BEARING_FIELD_CHANGED:{field}")
        for field, value in projected.items():
            if field not in content:
                p.append(f"PROJECTION_GENERATED_FIELD_FORBIDDEN:{field}")
            elif value != content[field]:
                p.append(f"PROJECTION_RETAINED_VALUE_CHANGED:{field}")
        expected_fields = set(content) - set(omitted)
        if set(projected) != expected_fields:
            p.append("PROJECTION_FIELD_SET_MISMATCH")
        for rel in sorted(load_rel):
            if rel not in relations:
                p.append(f"PROJECTION_RAW_LOAD_BEARING_RELATION_MISSING:{rel}")
            elif rel not in projected_relations:
                p.append(f"PROJECTION_LOAD_BEARING_RELATION_OMITTED:{rel}")
            elif projected_relations[rel] != relations[rel]:
                p.append(f"PROJECTION_LOAD_BEARING_RELATION_CHANGED:{rel}")
        for rel, value in projected_relations.items():
            if rel not in relations:
                p.append(f"PROJECTION_GENERATED_RELATION_FORBIDDEN:{rel}")
            elif value != relations[rel]:
                p.append(f"PROJECTION_RETAINED_RELATION_CHANGED:{rel}")

    if record.get("projected_content_digest") != canonical_hash(projected):
        p.append("PROJECTION_CONTENT_DIGEST_MISMATCH")
    if record.get("projected_relations_digest") != canonical_hash(projected_relations):
        p.append("PROJECTION_RELATIONS_DIGEST_MISMATCH")
    supplied = record.get("projection_digest")
    if not _sha256(supplied):
        p.append("PROJECTION_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "projection_digest"):
        p.append("PROJECTION_DIGEST_MISMATCH")

    out = _result(p, "REVIEWER_SAFE_PROJECTION_VALID", "REVIEWER_SAFE_PROJECTION_INVALID")
    out["reviewable"] = out["valid"]
    return out


def validate_disclosure_catalog(catalog: Mapping[str, Any], *, obligations: Sequence[Mapping[str, Any]],
                                projections: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    insuff: list[str] = []
    if catalog.get("schema_version") != 1:
        p.append("DISCLOSURE_CATALOG_SCHEMA_INVALID")
    for key in ("catalog_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(catalog.get(key)):
            p.append(f"DISCLOSURE_CATALOG_FIELD_REQUIRED:{key}")
    views = catalog.get("views")
    if not isinstance(views, list):
        views = []
        p.append("DISCLOSURE_CATALOG_VIEWS_REQUIRED")
    by_obligation: dict[str, list[Mapping[str, Any]]] = {}
    view_ids: set[str] = set()
    for i, view in enumerate(views):
        if not isinstance(view, Mapping):
            p.append(f"DISCLOSURE_VIEW_MALFORMED:{i}")
            continue
        vid = view.get("view_id")
        oid = view.get("obligation_id")
        if not _nonempty(vid) or not _nonempty(oid):
            p.append(f"DISCLOSURE_VIEW_IDENTITY_REQUIRED:{i}")
            continue
        if vid in view_ids:
            p.append(f"DISCLOSURE_VIEW_ID_DUPLICATE:{vid}")
        view_ids.add(str(vid))
        by_obligation.setdefault(str(oid), []).append(view)
        state = view.get("state")
        if state not in DISCLOSURE_STATES:
            p.append(f"DISCLOSURE_VIEW_STATE_INVALID:{vid}")
        if view.get("presealed") is not True:
            p.append(f"DISCLOSURE_VIEW_NOT_PRESEALED:{vid}")
        projection_ids = view.get("projection_ids")
        if not isinstance(projection_ids, list) or not projection_ids or not all(_nonempty(x) for x in projection_ids):
            p.append(f"DISCLOSURE_VIEW_PROJECTIONS_REQUIRED:{vid}")
            projection_ids = []
        for pid in projection_ids:
            pr = projections.get(pid)
            if pr is None or not pr.get("valid"):
                p.append(f"DISCLOSURE_VIEW_PROJECTION_INVALID:{vid}:{pid}")
        if state == "INSUFFICIENT_TO_ASSESS":
            insuff.append(str(oid))
    obligation_ids = [str(o.get("obligation_id")) for o in obligations if isinstance(o, Mapping) and _nonempty(o.get("obligation_id"))]
    for oid in sorted(set(obligation_ids)):
        rows = by_obligation.get(oid, [])
        minimum = [v for v in rows if v.get("minimum_view") is True]
        if len(minimum) != 1:
            p.append(f"DISCLOSURE_MINIMUM_VIEW_COUNT_INVALID:{oid}:{len(minimum)}")
        elif minimum[0].get("state") == "INSUFFICIENT_TO_ASSESS":
            insuff.append(oid)
        elif minimum[0].get("state") != "COMPLETE_REVIEWABLE_VIEW":
            p.append(f"DISCLOSURE_MINIMUM_VIEW_STATE_INVALID:{oid}")
    for oid in sorted(set(by_obligation) - set(obligation_ids)):
        p.append(f"DISCLOSURE_VIEW_UNDERIVED_OBLIGATION:{oid}")
    supplied = catalog.get("catalog_digest")
    if not _sha256(supplied):
        p.append("DISCLOSURE_CATALOG_DIGEST_INVALID")
    elif supplied != _sealed_digest(catalog, "catalog_digest"):
        p.append("DISCLOSURE_CATALOG_DIGEST_MISMATCH")
    out = _result(p, "DISCLOSURE_CATALOG_VALID", "DISCLOSURE_CATALOG_INVALID")
    out["insufficient_obligations"] = sorted(set(insuff))
    out["review_ready"] = out["valid"] and not out["insufficient_obligations"]
    return out


def validate_disclosure_completeness_certificate(record: Mapping[str, Any], *,
                                                  catalog_result: Mapping[str, Any],
                                                  expected_obligation_ids: Sequence[str]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("DISCLOSURE_CERTIFICATE_SCHEMA_INVALID")
    for key in ("certificate_id", "candidate_id", "snapshot_id", "generation_id",
                "verifier_id", "verifier_control_domain_id"):
        if not _nonempty(record.get(key)):
            p.append(f"DISCLOSURE_CERTIFICATE_FIELD_REQUIRED:{key}")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("DISCLOSURE_CERTIFICATE_VERIFIER_INDEPENDENCE_REQUIRED")
    if not catalog_result.get("valid"):
        p.append("DISCLOSURE_CERTIFICATE_CATALOG_INVALID")
    coverage = record.get("obligation_states")
    if not isinstance(coverage, Mapping):
        coverage = {}
        p.append("DISCLOSURE_CERTIFICATE_OBLIGATION_STATES_REQUIRED")
    expected = set(expected_obligation_ids)
    if set(coverage) != expected:
        p.append("DISCLOSURE_CERTIFICATE_OBLIGATION_SET_MISMATCH")
    for oid, state in coverage.items():
        if state not in DISCLOSURE_STATES:
            p.append(f"DISCLOSURE_CERTIFICATE_STATE_INVALID:{oid}")
    catalog_insuff = set(catalog_result.get("insufficient_obligations", []))
    for oid in expected:
        expected_state = "INSUFFICIENT_TO_ASSESS" if oid in catalog_insuff else "COMPLETE_REVIEWABLE_VIEW"
        if coverage.get(oid) != expected_state:
            p.append(f"DISCLOSURE_CERTIFICATE_STATE_MISMATCH:{oid}:{expected_state}")
    if record.get("catalog_digest") != record.get("bound_catalog_digest"):
        p.append("DISCLOSURE_CERTIFICATE_CATALOG_BINDING_MISMATCH")
    supplied = record.get("certificate_digest")
    if not _sha256(supplied):
        p.append("DISCLOSURE_CERTIFICATE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "certificate_digest"):
        p.append("DISCLOSURE_CERTIFICATE_DIGEST_MISMATCH")
    out = _result(p, "DISCLOSURE_COMPLETENESS_CERTIFICATE_VALID", "DISCLOSURE_COMPLETENESS_CERTIFICATE_INVALID")
    out["review_ready"] = out["valid"] and all(coverage.get(oid) == "COMPLETE_REVIEWABLE_VIEW" for oid in expected)
    return out


def projection_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_OBLIGATION_PROJECTION_DISCLOSURE_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
