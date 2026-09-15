#!/usr/bin/env python3
"""V15 review-safe evidence governance core validators.

Construction-stage implementation only. These validators encode canonical
fail-closed trust primitives from the independently bounded V15 design.
They do not grant runtime, release, deployment, scientific, or terminal authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

CURRENTNESS_STATES = frozenset({"CURRENT", "STALE", "REVOKED", "SUPERSEDED", "UNKNOWN"})
INDEPENDENCE_RESULTS = frozenset({"INDEPENDENT", "NOT_INDEPENDENT", "INDEPENDENCE_UNPROVEN"})
GOVERNED_PROOF_RESULTS = frozenset({"SUPPORTED", "CONTRADICTED", "INSUFFICIENT"})
REVIEW_DIMENSION_STATUSES = frozenset({"SUPPORTED", "DEFECT_FOUND", "INSUFFICIENT"})
BLOCKER_STATES = frozenset({"OPEN_BLOCKER", "RESOLVED_IN_REOPENED_REVIEW"})
BLOCKER_SEVERITIES = frozenset({"CRITICAL", "HIGH"})
CHALLENGE_TYPES = frozenset({"UNIVERSE_NEGATIVE_SPACE", "NOT_APPLICABLE", "OBSERVATION_APPLICABILITY"})
CHALLENGE_RESULTS = frozenset({
    "NO_NEW_OBLIGATION_FOUND",
    "OBLIGATION_ADDED",
    "NOT_APPLICABLE_SUPPORTED",
    "NOT_APPLICABLE_REJECTED",
    "INSUFFICIENT",
})
INFLUENCE_CLASSES = frozenset({
    "ADMIN", "REPOSITORY", "DEPLOYMENT", "CREDENTIAL", "RUNTIME", "SIGNING",
    "STORAGE", "REVIEW_PROVIDER", "RECOVERY_RESET", "OVERRIDE_PARENT",
})


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _sha40(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA40.fullmatch(value))


def _sealed_digest(record: Mapping[str, Any], digest_field: str) -> str:
    material = {k: v for k, v in record.items() if k != digest_field}
    return canonical_hash(material)


@dataclass(frozen=True)
class Validation:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self, state_ok: str, state_bad: str) -> dict[str, Any]:
        return {
            "state": state_ok if self.valid else state_bad,
            "valid": self.valid,
            "qualified": False,
            "problems": list(self.problems),
            "authority_effect": AUTHORITY_EFFECT,
        }


def _finish(problems: Iterable[str]) -> Validation:
    normalized = tuple(sorted(set(problems)))
    return Validation(not normalized, normalized)


def validate_control_domain(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("CONTROL_DOMAIN_SCHEMA_INVALID")
    if not _nonempty(record.get("domain_id")):
        p.append("CONTROL_DOMAIN_ID_REQUIRED")
    if not _nonempty(record.get("generation_id")):
        p.append("CONTROL_DOMAIN_GENERATION_REQUIRED")
    roots = record.get("authority_roots")
    if not isinstance(roots, list) or not roots or not all(_nonempty(x) for x in roots):
        p.append("CONTROL_DOMAIN_AUTHORITY_ROOTS_REQUIRED")
    elif len(roots) != len(set(roots)):
        p.append("CONTROL_DOMAIN_AUTHORITY_ROOT_DUPLICATE")
    if record.get("currentness_state") not in CURRENTNESS_STATES:
        p.append("CONTROL_DOMAIN_CURRENTNESS_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("CONTROL_DOMAIN_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("CONTROL_DOMAIN_RECORD_DIGEST_MISMATCH")
    result = _finish(p).as_dict("CONTROL_DOMAIN_VALID", "CONTROL_DOMAIN_INVALID")
    result["domain_id"] = record.get("domain_id")
    return result


def validate_control_ancestry_edge(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("CONTROL_ANCESTRY_SCHEMA_INVALID")
    child, parent = record.get("child_domain_id"), record.get("parent_root_id")
    if not _nonempty(child):
        p.append("CONTROL_ANCESTRY_CHILD_REQUIRED")
    if not _nonempty(parent):
        p.append("CONTROL_ANCESTRY_PARENT_REQUIRED")
    if child == parent and _nonempty(child):
        p.append("CONTROL_ANCESTRY_SELF_EDGE_FORBIDDEN")
    if record.get("influence_class") not in INFLUENCE_CLASSES:
        p.append("CONTROL_ANCESTRY_INFLUENCE_CLASS_INVALID")
    if not _sha256(record.get("evidence_digest")):
        p.append("CONTROL_ANCESTRY_EVIDENCE_DIGEST_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("CONTROL_ANCESTRY_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("CONTROL_ANCESTRY_RECORD_DIGEST_MISMATCH")
    return _finish(p).as_dict("CONTROL_ANCESTRY_EDGE_VALID", "CONTROL_ANCESTRY_EDGE_INVALID")


def validate_residual_trust_root(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("RESIDUAL_TRUST_SCHEMA_INVALID")
    for key in ("root_id", "control_domain_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"RESIDUAL_TRUST_FIELD_REQUIRED:{key}")
    scope = record.get("scope")
    if not isinstance(scope, list) or not scope or not all(_nonempty(x) for x in scope):
        p.append("RESIDUAL_TRUST_SCOPE_REQUIRED")
    limitations = record.get("accepted_limitations")
    if not isinstance(limitations, list):
        p.append("RESIDUAL_TRUST_LIMITATIONS_REQUIRED")
    if record.get("currentness_state") not in {"CURRENT", "STALE", "REVOKED"}:
        p.append("RESIDUAL_TRUST_CURRENTNESS_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("RESIDUAL_TRUST_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("RESIDUAL_TRUST_RECORD_DIGEST_MISMATCH")
    return _finish(p).as_dict("RESIDUAL_TRUST_ROOT_VALID", "RESIDUAL_TRUST_ROOT_INVALID")


def validate_independently_rooted_proof(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("INDEPENDENCE_PROOF_SCHEMA_INVALID")
    for key in ("proof_id", "subject_a", "subject_b", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"INDEPENDENCE_PROOF_FIELD_REQUIRED:{key}")
    if record.get("subject_a") == record.get("subject_b") and _nonempty(record.get("subject_a")):
        p.append("INDEPENDENCE_PROOF_SAME_SUBJECT_FORBIDDEN")
    if not _sha256(record.get("ancestry_graph_digest")):
        p.append("INDEPENDENCE_PROOF_ANCESTRY_DIGEST_INVALID")
    shared = record.get("shared_load_bearing_ancestors")
    if not isinstance(shared, list) or not all(_nonempty(x) for x in shared):
        p.append("INDEPENDENCE_PROOF_SHARED_ANCESTORS_INVALID")
        shared = []
    result = record.get("result")
    if result not in INDEPENDENCE_RESULTS:
        p.append("INDEPENDENCE_PROOF_RESULT_INVALID")
    if result == "INDEPENDENT" and shared:
        p.append("INDEPENDENCE_PROOF_INDEPENDENT_WITH_SHARED_ANCESTOR")
    if result == "NOT_INDEPENDENT" and not shared:
        p.append("INDEPENDENCE_PROOF_NOT_INDEPENDENT_WITHOUT_SHARED_ANCESTOR")
    roots = record.get("declared_residual_roots")
    if not isinstance(roots, list) or not roots or not all(_nonempty(x) for x in roots):
        p.append("INDEPENDENCE_PROOF_RESIDUAL_ROOTS_REQUIRED")
    supplied = record.get("proof_digest")
    if not _sha256(supplied):
        p.append("INDEPENDENCE_PROOF_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "proof_digest"):
        p.append("INDEPENDENCE_PROOF_DIGEST_MISMATCH")
    out = _finish(p).as_dict("INDEPENDENCE_PROOF_VALID", "INDEPENDENCE_PROOF_INVALID")
    out["independence_result"] = result if result in INDEPENDENCE_RESULTS else "INDEPENDENCE_UNPROVEN"
    return out


def validate_governed_proof(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("GOVERNED_PROOF_SCHEMA_INVALID")
    for key in ("proof_id", "subject_id", "candidate_id", "snapshot_id", "generation_id",
                "proof_mechanism_id", "verifier_id", "currentness"):
        if not _nonempty(record.get(key)):
            p.append(f"GOVERNED_PROOF_FIELD_REQUIRED:{key}")
    evid = record.get("evidence_digests")
    if not isinstance(evid, list) or not evid or not all(_sha256(x) for x in evid):
        p.append("GOVERNED_PROOF_EVIDENCE_DIGESTS_INVALID")
    if record.get("result") not in GOVERNED_PROOF_RESULTS:
        p.append("GOVERNED_PROOF_RESULT_INVALID")
    if record.get("candidate_self_authored") is not False:
        p.append("GOVERNED_PROOF_SELF_AUTHORED_FORBIDDEN")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("GOVERNED_PROOF_VERIFIER_INDEPENDENCE_REQUIRED")
    supplied = record.get("proof_digest")
    if not _sha256(supplied):
        p.append("GOVERNED_PROOF_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "proof_digest"):
        p.append("GOVERNED_PROOF_DIGEST_MISMATCH")
    return _finish(p).as_dict("GOVERNED_PROOF_VALID", "GOVERNED_PROOF_INVALID")


def validate_challenge_certificate(record: Mapping[str, Any], *, current_sequence: int | None = None) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("CHALLENGE_CERTIFICATE_SCHEMA_INVALID")
    for key in ("certificate_id", "candidate_id", "snapshot_id", "generation_id",
                "mechanism_identity", "verifier_id", "currentness_rule"):
        if not _nonempty(record.get(key)):
            p.append(f"CHALLENGE_CERTIFICATE_FIELD_REQUIRED:{key}")
    if record.get("challenge_type") not in CHALLENGE_TYPES:
        p.append("CHALLENGE_CERTIFICATE_TYPE_INVALID")
    if record.get("result") not in CHALLENGE_RESULTS:
        p.append("CHALLENGE_CERTIFICATE_RESULT_INVALID")
    if not _sha256(record.get("source_root_digest")):
        p.append("CHALLENGE_CERTIFICATE_SOURCE_ROOT_DIGEST_INVALID")
    issued = record.get("issued_sequence")
    expires = record.get("expires_sequence")
    if not isinstance(issued, int) or issued < 1:
        p.append("CHALLENGE_CERTIFICATE_ISSUED_SEQUENCE_INVALID")
    if not isinstance(expires, int) or not isinstance(issued, int) or expires <= issued:
        p.append("CHALLENGE_CERTIFICATE_EXPIRY_INVALID")
    if current_sequence is not None and isinstance(expires, int) and current_sequence > expires:
        p.append("CHALLENGE_CERTIFICATE_EXPIRED")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("CHALLENGE_CERTIFICATE_VERIFIER_INDEPENDENCE_REQUIRED")
    if record.get("candidate_self_authored") is not False:
        p.append("CHALLENGE_CERTIFICATE_SELF_AUTHORED_FORBIDDEN")
    supplied = record.get("certificate_digest")
    if not _sha256(supplied):
        p.append("CHALLENGE_CERTIFICATE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "certificate_digest"):
        p.append("CHALLENGE_CERTIFICATE_DIGEST_MISMATCH")
    return _finish(p).as_dict("CHALLENGE_CERTIFICATE_VALID", "CHALLENGE_CERTIFICATE_INVALID")


def validate_currentness_binding(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("CURRENTNESS_BINDING_SCHEMA_INVALID")
    for key in ("subject_id", "source_version", "verifier_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"CURRENTNESS_BINDING_FIELD_REQUIRED:{key}")
    if not _sha256(record.get("source_digest")):
        p.append("CURRENTNESS_BINDING_SOURCE_DIGEST_INVALID")
    seq = record.get("observed_sequence")
    if not isinstance(seq, int) or seq < 1:
        p.append("CURRENTNESS_BINDING_SEQUENCE_INVALID")
    if record.get("state") not in CURRENTNESS_STATES:
        p.append("CURRENTNESS_BINDING_STATE_INVALID")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("CURRENTNESS_BINDING_VERIFIER_INDEPENDENCE_REQUIRED")
    supplied = record.get("binding_digest")
    if not _sha256(supplied):
        p.append("CURRENTNESS_BINDING_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "binding_digest"):
        p.append("CURRENTNESS_BINDING_DIGEST_MISMATCH")
    return _finish(p).as_dict("CURRENTNESS_BINDING_VALID", "CURRENTNESS_BINDING_INVALID")


def validate_reviewer_response_coverage(record: Mapping[str, Any], *, mandatory_dimensions: Sequence[str]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("REVIEW_RESPONSE_SCHEMA_INVALID")
    for key in ("review_id", "snapshot_id", "reviewer_id", "session_id"):
        if not _nonempty(record.get(key)):
            p.append(f"REVIEW_RESPONSE_FIELD_REQUIRED:{key}")
    for key in ("response_digest", "content_receipt_digest", "receipt_digest"):
        if not _sha256(record.get(key)):
            p.append(f"REVIEW_RESPONSE_SHA256_INVALID:{key}")
    rows = record.get("dimensions")
    if not isinstance(rows, list):
        rows = []
        p.append("REVIEW_RESPONSE_DIMENSIONS_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"REVIEW_RESPONSE_DIMENSION_MALFORMED:{i}")
            continue
        did = row.get("dimension_id")
        if not _nonempty(did):
            p.append(f"REVIEW_RESPONSE_DIMENSION_ID_REQUIRED:{i}")
            continue
        if did in by_id:
            p.append(f"REVIEW_RESPONSE_DIMENSION_DUPLICATE:{did}")
            continue
        by_id[did] = row
        if row.get("status") not in REVIEW_DIMENSION_STATUSES:
            p.append(f"REVIEW_RESPONSE_DIMENSION_STATUS_INVALID:{did}")
        if not _sha256(row.get("assessment_digest")):
            p.append(f"REVIEW_RESPONSE_ASSESSMENT_DIGEST_INVALID:{did}")
    required = set(mandatory_dimensions)
    for did in sorted(required - set(by_id)):
        p.append(f"REVIEW_RESPONSE_MANDATORY_DIMENSION_MISSING:{did}")
    for did in sorted(set(by_id) - required):
        p.append(f"REVIEW_RESPONSE_UNKNOWN_DIMENSION:{did}")
    if record.get("complete") is not True:
        p.append("REVIEW_RESPONSE_NOT_COMPLETE")
    if record.get("disposition") in {"PASS", "BOUNDED_PASS"}:
        for did in sorted(required):
            row = by_id.get(did)
            if row is None or row.get("status") != "SUPPORTED":
                p.append(f"REVIEW_RESPONSE_POSITIVE_WITH_UNSUPPORTED_DIMENSION:{did}")
    supplied = record.get("receipt_digest")
    if _sha256(supplied) and supplied != _sealed_digest(record, "receipt_digest"):
        p.append("REVIEW_RESPONSE_RECEIPT_DIGEST_MISMATCH")
    out = _finish(p).as_dict("REVIEW_RESPONSE_COVERAGE_VALID", "REVIEW_RESPONSE_COVERAGE_INVALID")
    out["mandatory_dimension_count"] = len(required)
    out["covered_dimension_count"] = len(by_id)
    return out


def validate_blocker_record(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("BLOCKER_RECORD_SCHEMA_INVALID")
    for key in ("blocker_id", "review_id", "snapshot_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"BLOCKER_RECORD_FIELD_REQUIRED:{key}")
    if record.get("severity") not in BLOCKER_SEVERITIES:
        p.append("BLOCKER_RECORD_SEVERITY_INVALID")
    if record.get("state") not in BLOCKER_STATES:
        p.append("BLOCKER_RECORD_STATE_INVALID")
    evid = record.get("evidence_digests")
    if not isinstance(evid, list) or not evid or not all(_sha256(x) for x in evid):
        p.append("BLOCKER_RECORD_EVIDENCE_DIGESTS_INVALID")
    seq = record.get("opened_sequence")
    if not isinstance(seq, int) or seq < 1:
        p.append("BLOCKER_RECORD_OPENED_SEQUENCE_INVALID")
    if record.get("state") == "RESOLVED_IN_REOPENED_REVIEW":
        if not _nonempty(record.get("resolution_review_id")):
            p.append("BLOCKER_RECORD_RESOLUTION_REVIEW_REQUIRED")
        if not _sha256(record.get("resolution_evidence_digest")):
            p.append("BLOCKER_RECORD_RESOLUTION_EVIDENCE_REQUIRED")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("BLOCKER_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("BLOCKER_RECORD_DIGEST_MISMATCH")
    return _finish(p).as_dict("BLOCKER_RECORD_VALID", "BLOCKER_RECORD_INVALID")


def validate_fenced_effect_token(record: Mapping[str, Any], *, current_sequence: int,
                                 consumed_token_ids: set[str] | frozenset[str],
                                 expected: Mapping[str, str]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("FENCED_TOKEN_SCHEMA_INVALID")
    for key in ("token_id", "candidate_id", "snapshot_id", "generation_id", "nonce"):
        if not _nonempty(record.get(key)):
            p.append(f"FENCED_TOKEN_FIELD_REQUIRED:{key}")
    for key in ("ledger_head_digest", "currentness_vector_digest", "content_receipt_digest"):
        if not _sha256(record.get(key)):
            p.append(f"FENCED_TOKEN_SHA256_INVALID:{key}")
    if record.get("single_use") is not True:
        p.append("FENCED_TOKEN_SINGLE_USE_REQUIRED")
    token_id = record.get("token_id")
    if isinstance(token_id, str) and token_id in consumed_token_ids:
        p.append("FENCED_TOKEN_REPLAYED")
    expires = record.get("expires_sequence")
    if not isinstance(expires, int) or expires < 1:
        p.append("FENCED_TOKEN_EXPIRY_INVALID")
    elif current_sequence > expires:
        p.append("FENCED_TOKEN_EXPIRED")
    for key in ("candidate_id", "snapshot_id", "generation_id", "ledger_head_digest",
                "currentness_vector_digest", "content_receipt_digest"):
        if key in expected and record.get(key) != expected[key]:
            p.append(f"FENCED_TOKEN_CONTEXT_MISMATCH:{key}")
    supplied = record.get("token_digest")
    if not _sha256(supplied):
        p.append("FENCED_TOKEN_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "token_digest"):
        p.append("FENCED_TOKEN_DIGEST_MISMATCH")
    return _finish(p).as_dict("FENCED_EFFECT_TOKEN_VALID", "FENCED_EFFECT_TOKEN_INVALID")


def validate_control_domain_graph(domains: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    by_id: dict[str, Mapping[str, Any]] = {}
    for i, record in enumerate(domains):
        result = validate_control_domain(record)
        if not result["valid"]:
            p.extend(f"DOMAIN[{i}]:{x}" for x in result["problems"])
        did = record.get("domain_id")
        if isinstance(did, str):
            if did in by_id:
                p.append(f"CONTROL_DOMAIN_DUPLICATE:{did}")
            else:
                by_id[did] = record
    parent_map: dict[str, set[str]] = {did: set() for did in by_id}
    for i, edge_record in enumerate(edges):
        result = validate_control_ancestry_edge(edge_record)
        if not result["valid"]:
            p.extend(f"EDGE[{i}]:{x}" for x in result["problems"])
        child, parent = edge_record.get("child_domain_id"), edge_record.get("parent_root_id")
        if isinstance(child, str):
            if child not in by_id:
                p.append(f"CONTROL_ANCESTRY_UNKNOWN_CHILD:{child}")
            elif isinstance(parent, str):
                parent_map[child].add(parent)
    for did, record in by_id.items():
        declared = set(record.get("authority_roots", [])) if isinstance(record.get("authority_roots"), list) else set()
        if declared != parent_map.get(did, set()):
            p.append(f"CONTROL_DOMAIN_ROOT_SET_MISMATCH:{did}")
    return _finish(p).as_dict("CONTROL_DOMAIN_GRAPH_VALID", "CONTROL_DOMAIN_GRAPH_INVALID")


def assess_independence(*, subject_a: str, subject_b: str,
                        domains: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    graph = validate_control_domain_graph(domains, edges)
    p = list(graph["problems"])
    by_id = {d.get("domain_id"): d for d in domains if isinstance(d, Mapping) and isinstance(d.get("domain_id"), str)}
    if subject_a not in by_id or subject_b not in by_id:
        p.append("INDEPENDENCE_SUBJECT_UNKNOWN")
        result = "INDEPENDENCE_UNPROVEN"
        shared: list[str] = []
    else:
        roots_a = set(by_id[subject_a].get("authority_roots", []))
        roots_b = set(by_id[subject_b].get("authority_roots", []))
        if not roots_a or not roots_b:
            result = "INDEPENDENCE_UNPROVEN"
            shared = []
            p.append("INDEPENDENCE_ROOT_ANCESTRY_INCOMPLETE")
        else:
            shared = sorted(roots_a & roots_b)
            result = "NOT_INDEPENDENT" if shared else "INDEPENDENT"
    out = _finish(p).as_dict("INDEPENDENCE_ASSESSMENT_VALID", "INDEPENDENCE_ASSESSMENT_INVALID")
    out["result"] = result
    out["shared_load_bearing_ancestors"] = shared
    out["promotion_blocked"] = result != "INDEPENDENT" or not out["valid"]
    return out


def promotion_independence_gate(required_pairs: Sequence[tuple[str, str]],
                                proofs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    proof_map: dict[frozenset[str], Mapping[str, Any]] = {}
    for i, proof in enumerate(proofs):
        checked = validate_independently_rooted_proof(proof)
        if not checked["valid"]:
            p.extend(f"PROOF[{i}]:{x}" for x in checked["problems"])
        a, b = proof.get("subject_a"), proof.get("subject_b")
        if isinstance(a, str) and isinstance(b, str):
            key = frozenset((a, b))
            if key in proof_map:
                p.append(f"INDEPENDENCE_GATE_DUPLICATE_PROOF:{a}:{b}")
            else:
                proof_map[key] = proof
    for a, b in required_pairs:
        proof = proof_map.get(frozenset((a, b)))
        if proof is None:
            p.append(f"INDEPENDENCE_GATE_PROOF_MISSING:{a}:{b}")
            continue
        if proof.get("result") != "INDEPENDENT":
            p.append(f"PROMOTION_BLOCKED_INDEPENDENCE_UNPROVEN:{a}:{b}:{proof.get('result')}")
    val = _finish(p)
    out = val.as_dict("PROMOTION_INDEPENDENCE_GATE_PASS", "PROMOTION_INDEPENDENCE_GATE_BLOCKED")
    out["promotion_allowed"] = val.valid
    return out


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_CORE_TRUST_PRIMITIVES_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
