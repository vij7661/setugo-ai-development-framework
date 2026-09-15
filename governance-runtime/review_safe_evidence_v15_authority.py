#!/usr/bin/env python3
"""V15 role-authority registry and ancestry-closure validators.

Construction-only. No authority effect.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    CURRENTNESS_STATES,
    canonical_hash,
    validate_independently_rooted_proof,
)

REQUIRED_ROLE_CLASSES = frozenset({
    "EVIDENCE_CAPTURE_AUTHORITY",
    "EVIDENCE_UNIVERSE_DERIVATION_AUTHORITY",
    "UNIVERSE_CHALLENGE_AUTHORITY",
    "EVIDENCE_CLASSIFICATION_AUTHORITY",
    "OBLIGATION_MATERIALITY_AUTHORITY",
    "N_A_PROOF_AUTHORITY",
    "N_A_PROOF_VERIFIER",
    "PROJECTION_COMPILER",
    "PROJECTION_VERIFIER",
    "DISCLOSURE_COMPLETENESS_VERIFIER",
    "HIDDEN_EVIDENCE_MONITOR_CERTIFICATE_VERIFIER",
    "SNAPSHOT_WRITER",
    "SNAPSHOT_WITNESS_AUTHORITY",
    "REVIEWER_QUALIFICATION_AUTHORITY",
    "REVIEW_SET_AUTHORITY",
    "ADJUDICATION_AUTHORITY",
    "HIDDEN_EVIDENCE_REOPEN_MONITOR_AUTHORITY",
    "GOVERNANCE_GENERATION_WITNESS_AUTHORITY",
    "EFFECT_GATEWAY_AUTHORITY",
})

MANDATORY_SEPARATION_PAIRS = (
    ("PROJECTION_COMPILER", "PROJECTION_VERIFIER"),
    ("EVIDENCE_CLASSIFICATION_AUTHORITY", "OBLIGATION_MATERIALITY_AUTHORITY"),
    ("EVIDENCE_UNIVERSE_DERIVATION_AUTHORITY", "UNIVERSE_CHALLENGE_AUTHORITY"),
    ("N_A_PROOF_AUTHORITY", "N_A_PROOF_VERIFIER"),
    ("SNAPSHOT_WRITER", "SNAPSHOT_WITNESS_AUTHORITY"),
    ("HIDDEN_EVIDENCE_REOPEN_MONITOR_AUTHORITY", "HIDDEN_EVIDENCE_MONITOR_CERTIFICATE_VERIFIER"),
    ("REVIEWER_QUALIFICATION_AUTHORITY", "ADJUDICATION_AUTHORITY"),
    ("REVIEW_SET_AUTHORITY", "ADJUDICATION_AUTHORITY"),
    ("ADJUDICATION_AUTHORITY", "EFFECT_GATEWAY_AUTHORITY"),
)


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


def validate_role_record(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("ROLE_AUTHORITY_SCHEMA_INVALID")
    for key in ("role_id", "role_class", "control_domain_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"ROLE_AUTHORITY_FIELD_REQUIRED:{key}")
    if record.get("role_class") not in REQUIRED_ROLE_CLASSES:
        p.append(f"ROLE_AUTHORITY_CLASS_INVALID:{record.get('role_class')}")
    if record.get("currentness_state") not in CURRENTNESS_STATES:
        p.append("ROLE_AUTHORITY_CURRENTNESS_INVALID")
    if record.get("authority_origin") != "REVIEW_GOVERNANCE_ROOT":
        p.append("ROLE_AUTHORITY_ORIGIN_INVALID")
    if record.get("candidate_controlled") is not False:
        p.append("ROLE_AUTHORITY_CANDIDATE_CONTROL_FORBIDDEN")
    if not _sha256(record.get("appointment_record_digest")):
        p.append("ROLE_AUTHORITY_APPOINTMENT_DIGEST_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("ROLE_AUTHORITY_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("ROLE_AUTHORITY_RECORD_DIGEST_MISMATCH")
    return _result(p, "ROLE_AUTHORITY_RECORD_VALID", "ROLE_AUTHORITY_RECORD_INVALID")


def validate_review_governance_root(root: Mapping[str, Any],
                                    independence_proofs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    if root.get("schema_version") != 1:
        p.append("REVIEW_ROOT_SCHEMA_INVALID")
    for key in ("root_id", "generation_id", "genesis_record_digest"):
        if not _nonempty(root.get(key)):
            p.append(f"REVIEW_ROOT_FIELD_REQUIRED:{key}")
    if root.get("terminal_residual_trust_declared") is not True:
        p.append("REVIEW_ROOT_RESIDUAL_TRUST_DECLARATION_REQUIRED")
    if root.get("self_qualified_by_descendant_machinery") is not False:
        p.append("REVIEW_ROOT_DESCENDANT_SELF_QUALIFICATION_FORBIDDEN")
    if root.get("candidate_controlled") is not False:
        p.append("REVIEW_ROOT_CANDIDATE_CONTROL_FORBIDDEN")
    if root.get("authority_effect") != AUTHORITY_EFFECT:
        p.append("REVIEW_ROOT_AUTHORITY_EFFECT_INVALID")
    members = root.get("threshold_members")
    if not isinstance(members, list) or len(members) < 2:
        members = []
        p.append("REVIEW_ROOT_THRESHOLD_MEMBERS_REQUIRED")
    threshold = root.get("threshold")
    if not isinstance(threshold, int) or threshold < 2 or threshold > len(members):
        p.append("REVIEW_ROOT_THRESHOLD_INVALID")
    domains: list[str] = []
    ids: set[str] = set()
    for i, member in enumerate(members):
        if not isinstance(member, Mapping):
            p.append(f"REVIEW_ROOT_MEMBER_MALFORMED:{i}")
            continue
        aid = member.get("authority_id")
        domain = member.get("control_domain_id")
        if not _nonempty(aid):
            p.append(f"REVIEW_ROOT_MEMBER_ID_REQUIRED:{i}")
        elif aid in ids:
            p.append(f"REVIEW_ROOT_MEMBER_ID_DUPLICATE:{aid}")
        else:
            ids.add(aid)
        if not _nonempty(domain):
            p.append(f"REVIEW_ROOT_MEMBER_DOMAIN_REQUIRED:{i}")
        else:
            domains.append(domain)
        if member.get("currentness_state") != "CURRENT":
            p.append(f"REVIEW_ROOT_MEMBER_NOT_CURRENT:{aid}")
    if len(domains) != len(set(domains)):
        p.append("REVIEW_ROOT_THRESHOLD_CONTROL_DOMAIN_DUPLICATE")

    proof_map: dict[frozenset[str], Mapping[str, Any]] = {}
    for i, proof in enumerate(independence_proofs):
        checked = validate_independently_rooted_proof(proof)
        if not checked["valid"]:
            p.extend(f"ROOT_PROOF[{i}]:{x}" for x in checked["problems"])
        a, b = proof.get("subject_a"), proof.get("subject_b")
        if isinstance(a, str) and isinstance(b, str):
            proof_map[frozenset((a, b))] = proof
    for a, b in combinations(sorted(set(domains)), 2):
        proof = proof_map.get(frozenset((a, b)))
        if proof is None:
            p.append(f"REVIEW_ROOT_THRESHOLD_INDEPENDENCE_PROOF_MISSING:{a}:{b}")
        elif proof.get("result") != "INDEPENDENT":
            p.append(f"REVIEW_ROOT_THRESHOLD_INDEPENDENCE_UNPROVEN:{a}:{b}:{proof.get('result')}")
    supplied = root.get("record_digest")
    if not _sha256(supplied):
        p.append("REVIEW_ROOT_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(root, "record_digest"):
        p.append("REVIEW_ROOT_RECORD_DIGEST_MISMATCH")
    out = _result(p, "REVIEW_GOVERNANCE_ROOT_VALID", "REVIEW_GOVERNANCE_ROOT_INVALID")
    out["threshold_member_count"] = len(members)
    return out


def validate_role_authority_registry(bundle: Mapping[str, Any],
                                     independence_proofs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("ROLE_REGISTRY_SCHEMA_INVALID")
    if not _nonempty(bundle.get("generation_id")):
        p.append("ROLE_REGISTRY_GENERATION_REQUIRED")
    if not _nonempty(bundle.get("root_id")):
        p.append("ROLE_REGISTRY_ROOT_ID_REQUIRED")
    if bundle.get("authority_effect") != AUTHORITY_EFFECT:
        p.append("ROLE_REGISTRY_AUTHORITY_EFFECT_INVALID")
    roles = bundle.get("roles")
    if not isinstance(roles, list):
        roles = []
        p.append("ROLE_REGISTRY_ROLE_SET_REQUIRED")
    by_class: dict[str, list[Mapping[str, Any]]] = {}
    role_ids: set[str] = set()
    for i, role in enumerate(roles):
        if not isinstance(role, Mapping):
            p.append(f"ROLE_REGISTRY_ROLE_MALFORMED:{i}")
            continue
        checked = validate_role_record(role)
        if not checked["valid"]:
            p.extend(f"ROLE[{i}]:{x}" for x in checked["problems"])
        rid = role.get("role_id")
        if isinstance(rid, str):
            if rid in role_ids:
                p.append(f"ROLE_REGISTRY_ROLE_ID_DUPLICATE:{rid}")
            role_ids.add(rid)
        rc = role.get("role_class")
        if isinstance(rc, str):
            by_class.setdefault(rc, []).append(role)
        if role.get("generation_id") != bundle.get("generation_id"):
            p.append(f"ROLE_REGISTRY_GENERATION_MISMATCH:{rid}")
    for role_class in sorted(REQUIRED_ROLE_CLASSES - set(by_class)):
        p.append(f"ROLE_REGISTRY_REQUIRED_CLASS_MISSING:{role_class}")
    for role_class in sorted(REQUIRED_ROLE_CLASSES & set(by_class)):
        current = [r for r in by_class[role_class] if r.get("currentness_state") == "CURRENT"]
        if not current:
            p.append(f"ROLE_REGISTRY_NO_CURRENT_AUTHORITY:{role_class}")

    proof_map: dict[frozenset[str], Mapping[str, Any]] = {}
    for i, proof in enumerate(independence_proofs):
        checked = validate_independently_rooted_proof(proof)
        if not checked["valid"]:
            p.extend(f"SEPARATION_PROOF[{i}]:{x}" for x in checked["problems"])
        a, b = proof.get("subject_a"), proof.get("subject_b")
        if isinstance(a, str) and isinstance(b, str):
            proof_map[frozenset((a, b))] = proof

    for class_a, class_b in MANDATORY_SEPARATION_PAIRS:
        roles_a = [r for r in by_class.get(class_a, []) if r.get("currentness_state") == "CURRENT"]
        roles_b = [r for r in by_class.get(class_b, []) if r.get("currentness_state") == "CURRENT"]
        for ra in roles_a:
            for rb in roles_b:
                da, db = ra.get("control_domain_id"), rb.get("control_domain_id")
                if da == db and isinstance(da, str):
                    p.append(f"ROLE_REGISTRY_CONTROL_DOMAIN_COLLAPSE:{class_a}:{class_b}:{da}")
                    continue
                proof = proof_map.get(frozenset((str(da), str(db))))
                if proof is None:
                    p.append(f"ROLE_REGISTRY_SEPARATION_PROOF_MISSING:{class_a}:{class_b}:{da}:{db}")
                elif proof.get("result") != "INDEPENDENT":
                    p.append(f"ROLE_REGISTRY_INDEPENDENCE_UNPROVEN:{class_a}:{class_b}:{da}:{db}:{proof.get('result')}")

    supplied = bundle.get("registry_digest")
    if not _sha256(supplied):
        p.append("ROLE_REGISTRY_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "registry_digest"):
        p.append("ROLE_REGISTRY_DIGEST_MISMATCH")

    out = _result(p, "ROLE_AUTHORITY_REGISTRY_VALID", "ROLE_AUTHORITY_REGISTRY_INVALID")
    out["required_role_class_count"] = len(REQUIRED_ROLE_CLASSES)
    out["present_role_class_count"] = len(set(by_class) & REQUIRED_ROLE_CLASSES)
    return out


def authority_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_ROLE_AUTHORITY_AND_ANCESTRY_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
