#!/usr/bin/env python3
"""V15 sealed review snapshot, clean-room, reviewer qualification, and response receipt.

Construction-stage implementation only. These validators are fail-closed evidence
mechanisms and never grant runtime, deployment, release, scientific, or terminal authority.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    canonical_hash,
    validate_independently_rooted_proof,
    validate_reviewer_response_coverage,
)

SNAPSHOT_STATES = frozenset({"SEALED", "PREPARING", "RECONCILIATION_REQUIRED", "SUPERSEDED"})
CLEAN_CONTEXT_ASSURANCE = frozenset({
    "INDEPENDENTLY_VERIFIABLE_PROVIDER_ISOLATION",
    "AIR_GAPPED_CLEAN_ROOM",
    "UNAVAILABLE",
})
REVIEW_TRANSPORT_CLASSES = frozenset({
    "PLATFORM_AUTHENTICATED_API",
    "AIR_GAPPED_MANUAL_CLEAN_ROOM",
    "MANUAL_PASTE_EXTERNAL_EVIDENCE_ONLY",
})


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _sha40(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v)


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


def validate_sealed_review_snapshot(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("REVIEW_SNAPSHOT_SCHEMA_INVALID")
    for key in (
        "snapshot_id", "candidate_id", "generation_id", "writer_id",
        "writer_control_domain_id", "candidate_control_domain_id",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"REVIEW_SNAPSHOT_FIELD_REQUIRED:{key}")
    if not _sha40(record.get("candidate_commit")):
        p.append("REVIEW_SNAPSHOT_CANDIDATE_COMMIT_INVALID")
    for key in (
        "candidate_tree_digest", "content_root_digest", "raw_evidence_root_digest",
        "obligation_graph_digest", "disclosure_catalog_digest", "monitor_certificate_digest",
        "currentness_vector_digest",
    ):
        if not _sha256(record.get(key)):
            p.append(f"REVIEW_SNAPSHOT_SHA256_INVALID:{key}")
    if record.get("state") != "SEALED":
        p.append("REVIEW_SNAPSHOT_NOT_SEALED")
    if record.get("atomic_seal") is not True:
        p.append("REVIEW_SNAPSHOT_ATOMIC_SEAL_REQUIRED")
    if record.get("mixed_state_detected") is not False:
        p.append("REVIEW_SNAPSHOT_MIXED_STATE_FORBIDDEN")
    if record.get("rollback_or_fork_detected") is not False:
        p.append("REVIEW_SNAPSHOT_ROLLBACK_OR_FORK_FORBIDDEN")
    if record.get("reconciliation_required") is not False:
        p.append("REVIEW_SNAPSHOT_UNRECONCILED")
    if record.get("currentness_state") != "CURRENT":
        p.append("REVIEW_SNAPSHOT_NOT_CURRENT")
    seq = record.get("sealed_sequence")
    if not isinstance(seq, int) or seq < 1:
        p.append("REVIEW_SNAPSHOT_SEALED_SEQUENCE_INVALID")
    if record.get("writer_control_domain_id") == record.get("candidate_control_domain_id"):
        p.append("REVIEW_SNAPSHOT_WRITER_CANDIDATE_DOMAIN_COLLAPSE")
    predecessor = record.get("predecessor_snapshot_digest")
    if predecessor not in {None, "GENESIS"} and not _sha256(predecessor):
        p.append("REVIEW_SNAPSHOT_PREDECESSOR_INVALID")
    supplied = record.get("snapshot_digest")
    if not _sha256(supplied):
        p.append("REVIEW_SNAPSHOT_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "snapshot_digest"):
        p.append("REVIEW_SNAPSHOT_DIGEST_MISMATCH")
    out = _finish(p, "SEALED_REVIEW_SNAPSHOT_VALID", "SEALED_REVIEW_SNAPSHOT_INVALID")
    out["reviewable"] = out["valid"]
    return out


def validate_snapshot_witness_bundle(
    bundle: Mapping[str, Any],
    *,
    snapshot: Mapping[str, Any],
    independence_proofs: Sequence[Mapping[str, Any]],
    forbidden_control_domains: Sequence[str] = (),
) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("SNAPSHOT_WITNESS_SCHEMA_INVALID")
    checked_snapshot = validate_sealed_review_snapshot(snapshot)
    if not checked_snapshot["valid"]:
        p.extend(f"SNAPSHOT:{x}" for x in checked_snapshot["problems"])
    for key in ("bundle_id", "snapshot_id", "generation_id", "anchor_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"SNAPSHOT_WITNESS_FIELD_REQUIRED:{key}")
    if bundle.get("snapshot_id") != snapshot.get("snapshot_id"):
        p.append("SNAPSHOT_WITNESS_SNAPSHOT_ID_MISMATCH")
    if bundle.get("snapshot_digest") != snapshot.get("snapshot_digest"):
        p.append("SNAPSHOT_WITNESS_SNAPSHOT_DIGEST_MISMATCH")
    if bundle.get("generation_id") != snapshot.get("generation_id"):
        p.append("SNAPSHOT_WITNESS_GENERATION_MISMATCH")
    if not _sha256(bundle.get("anchor_digest")):
        p.append("SNAPSHOT_WITNESS_ANCHOR_DIGEST_INVALID")
    if bundle.get("anchor_currentness_state") != "CURRENT":
        p.append("SNAPSHOT_WITNESS_ANCHOR_NOT_CURRENT")

    threshold = bundle.get("threshold_control_domains")
    if not isinstance(threshold, int) or threshold < 2:
        p.append("SNAPSHOT_WITNESS_THRESHOLD_INVALID")
        threshold = 2
    rows = bundle.get("witnesses")
    if not isinstance(rows, list) or not rows:
        rows = []
        p.append("SNAPSHOT_WITNESS_RECORDS_REQUIRED")
    domains: set[str] = set()
    identities: set[str] = set()
    forbidden = set(forbidden_control_domains)
    forbidden.update({
        str(snapshot.get("candidate_control_domain_id")),
        str(snapshot.get("writer_control_domain_id")),
    })
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"SNAPSHOT_WITNESS_RECORD_MALFORMED:{i}")
            continue
        wid = row.get("witness_id")
        domain = row.get("control_domain_id")
        if not _nonempty(wid) or not _nonempty(domain):
            p.append(f"SNAPSHOT_WITNESS_IDENTITY_REQUIRED:{i}")
            continue
        if wid in identities:
            p.append(f"SNAPSHOT_WITNESS_ID_DUPLICATE:{wid}")
        identities.add(str(wid))
        domains.add(str(domain))
        if domain in forbidden:
            p.append(f"SNAPSHOT_WITNESS_FORBIDDEN_CONTROL_DOMAIN:{wid}:{domain}")
        if row.get("candidate_controlled") is not False:
            p.append(f"SNAPSHOT_WITNESS_CANDIDATE_CONTROL_FORBIDDEN:{wid}")
        if row.get("currentness_state") != "CURRENT":
            p.append(f"SNAPSHOT_WITNESS_NOT_CURRENT:{wid}")
        if row.get("snapshot_id") != snapshot.get("snapshot_id"):
            p.append(f"SNAPSHOT_WITNESS_SNAPSHOT_MISMATCH:{wid}")
        if row.get("snapshot_digest") != snapshot.get("snapshot_digest"):
            p.append(f"SNAPSHOT_WITNESS_DIGEST_MISMATCH:{wid}")
        if row.get("anchor_digest") != bundle.get("anchor_digest"):
            p.append(f"SNAPSHOT_WITNESS_ANCHOR_MISMATCH:{wid}")
        supplied = row.get("record_digest")
        if not _sha256(supplied):
            p.append(f"SNAPSHOT_WITNESS_RECORD_DIGEST_INVALID:{wid}")
        elif supplied != _sealed_digest(row, "record_digest"):
            p.append(f"SNAPSHOT_WITNESS_RECORD_DIGEST_MISMATCH:{wid}")
    if len(domains) < threshold:
        p.append(f"SNAPSHOT_WITNESS_DOMAIN_QUORUM_INSUFFICIENT:{len(domains)}:{threshold}")

    proof_map: dict[frozenset[str], Mapping[str, Any]] = {}
    for proof in independence_proofs:
        if not isinstance(proof, Mapping):
            continue
        pair = frozenset((str(proof.get("subject_a")), str(proof.get("subject_b"))))
        if len(pair) == 2:
            proof_map[pair] = proof
    ds = sorted(domains)
    for i, a in enumerate(ds):
        for b in ds[i + 1:]:
            proof = proof_map.get(frozenset((a, b)))
            if proof is None:
                p.append(f"SNAPSHOT_WITNESS_INDEPENDENCE_PROOF_MISSING:{a}:{b}")
                continue
            checked = validate_independently_rooted_proof(proof)
            if not checked["valid"] or proof.get("result") != "INDEPENDENT":
                p.append(f"SNAPSHOT_WITNESS_INDEPENDENCE_UNPROVEN:{a}:{b}")

    supplied = bundle.get("bundle_digest")
    if not _sha256(supplied):
        p.append("SNAPSHOT_WITNESS_BUNDLE_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "bundle_digest"):
        p.append("SNAPSHOT_WITNESS_BUNDLE_DIGEST_MISMATCH")
    out = _finish(p, "SNAPSHOT_WITNESS_BUNDLE_VALID", "SNAPSHOT_WITNESS_BUNDLE_INVALID")
    out["control_domain_count"] = len(domains)
    out["witness_count"] = len(identities)
    out["reviewable"] = out["valid"]
    return out


def validate_clean_room_session_attestation(record: Mapping[str, Any], *, snapshot: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("CLEAN_ROOM_SCHEMA_INVALID")
    for key in (
        "session_id", "reviewer_id", "provider_id", "model_id", "transport_id",
        "context_isolation_method", "snapshot_id",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"CLEAN_ROOM_FIELD_REQUIRED:{key}")
    for key in ("snapshot_digest", "content_root_digest", "package_digest"):
        if not _sha256(record.get(key)):
            p.append(f"CLEAN_ROOM_SHA256_INVALID:{key}")
    if record.get("snapshot_id") != snapshot.get("snapshot_id"):
        p.append("CLEAN_ROOM_SNAPSHOT_ID_MISMATCH")
    if record.get("snapshot_digest") != snapshot.get("snapshot_digest"):
        p.append("CLEAN_ROOM_SNAPSHOT_DIGEST_MISMATCH")
    if record.get("content_root_digest") != snapshot.get("content_root_digest"):
        p.append("CLEAN_ROOM_CONTENT_ROOT_MISMATCH")
    if record.get("fresh_session") is not True:
        p.append("CLEAN_ROOM_FRESH_SESSION_REQUIRED")
    if record.get("prior_project_review_findings_absent") is not True:
        p.append("CLEAN_ROOM_PRIOR_FINDINGS_ABSENCE_REQUIRED")
    if record.get("post_review_finding_artifacts_excluded") is not True:
        p.append("CLEAN_ROOM_POST_REVIEW_FINDING_EXCLUSION_REQUIRED")
    if record.get("provider_identity_authenticated") is not True:
        p.append("CLEAN_ROOM_PROVIDER_IDENTITY_AUTHENTICATION_REQUIRED")
    if record.get("currentness_state") != "CURRENT":
        p.append("CLEAN_ROOM_NOT_CURRENT")
    assurance = record.get("provider_context_isolation_assurance")
    if assurance not in CLEAN_CONTEXT_ASSURANCE:
        p.append("CLEAN_ROOM_CONTEXT_ASSURANCE_INVALID")
    transport = record.get("transport_class")
    if transport not in REVIEW_TRANSPORT_CLASSES:
        p.append("CLEAN_ROOM_TRANSPORT_CLASS_INVALID")
    if transport == "MANUAL_PASTE_EXTERNAL_EVIDENCE_ONLY" and record.get("provider_context_isolation_assurance") != "UNAVAILABLE":
        p.append("CLEAN_ROOM_MANUAL_PASTE_CANNOT_CLAIM_PROVIDER_ISOLATION")
    supplied = record.get("attestation_digest")
    if not _sha256(supplied):
        p.append("CLEAN_ROOM_ATTESTATION_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "attestation_digest"):
        p.append("CLEAN_ROOM_ATTESTATION_DIGEST_MISMATCH")

    out = _finish(p, "CLEAN_ROOM_SESSION_ATTESTATION_VALID", "CLEAN_ROOM_SESSION_ATTESTATION_INVALID")
    promotable_assurance = assurance in {
        "INDEPENDENTLY_VERIFIABLE_PROVIDER_ISOLATION",
        "AIR_GAPPED_CLEAN_ROOM",
    }
    out["promotable"] = bool(out["valid"] and promotable_assurance and transport != "MANUAL_PASTE_EXTERNAL_EVIDENCE_ONLY")
    if out["valid"] and not out["promotable"]:
        out["nonpromotable_reason"] = "CONTEXT_ISOLATION_NOT_INDEPENDENTLY_VERIFIABLE"
    return out


def validate_reviewer_qualification(record: Mapping[str, Any], *, current_sequence: int) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("REVIEWER_QUALIFICATION_SCHEMA_INVALID")
    for key in (
        "qualification_id", "reviewer_id", "provider_id", "model_id", "role",
        "authority_id", "authority_control_domain_id", "reviewer_control_domain_id",
        "generation_id",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"REVIEWER_QUALIFICATION_FIELD_REQUIRED:{key}")
    if record.get("role") != "INDEPENDENT_REVIEWER":
        p.append("REVIEWER_QUALIFICATION_ROLE_INVALID")
    if record.get("candidate_controlled") is not False:
        p.append("REVIEWER_QUALIFICATION_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("provider_identity_authenticated") is not True:
        p.append("REVIEWER_QUALIFICATION_PROVIDER_IDENTITY_REQUIRED")
    if record.get("authority_independence_result") != "INDEPENDENT":
        p.append("REVIEWER_QUALIFICATION_AUTHORITY_INDEPENDENCE_REQUIRED")
    if record.get("reviewer_control_domain_id") == record.get("authority_control_domain_id"):
        p.append("REVIEWER_QUALIFICATION_AUTHORITY_DOMAIN_COLLAPSE")
    if record.get("currentness_state") != "CURRENT":
        p.append("REVIEWER_QUALIFICATION_NOT_CURRENT")
    issued = record.get("issued_sequence")
    expires = record.get("expires_sequence")
    if not isinstance(issued, int) or issued < 1:
        p.append("REVIEWER_QUALIFICATION_ISSUED_SEQUENCE_INVALID")
    if not isinstance(expires, int) or not isinstance(issued, int) or expires <= issued:
        p.append("REVIEWER_QUALIFICATION_EXPIRY_INVALID")
    elif current_sequence > expires:
        p.append("REVIEWER_QUALIFICATION_EXPIRED")
    for key in ("policy_digest", "qualification_evidence_digest"):
        if not _sha256(record.get(key)):
            p.append(f"REVIEWER_QUALIFICATION_SHA256_INVALID:{key}")
    supplied = record.get("qualification_digest")
    if not _sha256(supplied):
        p.append("REVIEWER_QUALIFICATION_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "qualification_digest"):
        p.append("REVIEWER_QUALIFICATION_DIGEST_MISMATCH")
    out = _finish(p, "REVIEWER_QUALIFICATION_CURRENT", "REVIEWER_QUALIFICATION_INVALID")
    out["current"] = out["valid"]
    return out


def validate_authenticated_review_response_receipt(
    receipt: Mapping[str, Any],
    *,
    snapshot: Mapping[str, Any],
    clean_room_attestation: Mapping[str, Any],
    reviewer_qualification: Mapping[str, Any],
    mandatory_dimensions: Sequence[str],
    current_sequence: int,
) -> dict[str, Any]:
    p: list[str] = []
    snap = validate_sealed_review_snapshot(snapshot)
    if not snap["valid"]:
        p.extend(f"SNAPSHOT:{x}" for x in snap["problems"])
    clean = validate_clean_room_session_attestation(clean_room_attestation, snapshot=snapshot)
    if not clean["valid"]:
        p.extend(f"CLEAN_ROOM:{x}" for x in clean["problems"])
    elif not clean["promotable"]:
        p.append("REVIEW_RECEIPT_CLEAN_ROOM_NONPROMOTABLE")
    qual = validate_reviewer_qualification(reviewer_qualification, current_sequence=current_sequence)
    if not qual["valid"]:
        p.extend(f"REVIEWER_QUALIFICATION:{x}" for x in qual["problems"])

    coverage = validate_reviewer_response_coverage(receipt, mandatory_dimensions=mandatory_dimensions)
    if not coverage["valid"]:
        p.extend(f"COVERAGE:{x}" for x in coverage["problems"])

    if receipt.get("snapshot_id") != snapshot.get("snapshot_id"):
        p.append("REVIEW_RECEIPT_SNAPSHOT_ID_MISMATCH")
    if receipt.get("snapshot_digest") != snapshot.get("snapshot_digest"):
        p.append("REVIEW_RECEIPT_SNAPSHOT_DIGEST_MISMATCH")
    if receipt.get("content_root_digest") != snapshot.get("content_root_digest"):
        p.append("REVIEW_RECEIPT_CONTENT_ROOT_MISMATCH")
    if receipt.get("reviewer_id") != reviewer_qualification.get("reviewer_id"):
        p.append("REVIEW_RECEIPT_REVIEWER_MISMATCH")
    if receipt.get("reviewer_id") != clean_room_attestation.get("reviewer_id"):
        p.append("REVIEW_RECEIPT_CLEAN_ROOM_REVIEWER_MISMATCH")
    if receipt.get("session_id") != clean_room_attestation.get("session_id"):
        p.append("REVIEW_RECEIPT_SESSION_MISMATCH")
    if receipt.get("provider_id") != reviewer_qualification.get("provider_id"):
        p.append("REVIEW_RECEIPT_PROVIDER_MISMATCH")
    if receipt.get("provider_id") != clean_room_attestation.get("provider_id"):
        p.append("REVIEW_RECEIPT_CLEAN_ROOM_PROVIDER_MISMATCH")
    if receipt.get("model_id") != reviewer_qualification.get("model_id"):
        p.append("REVIEW_RECEIPT_MODEL_MISMATCH")
    if receipt.get("model_id") != clean_room_attestation.get("model_id"):
        p.append("REVIEW_RECEIPT_CLEAN_ROOM_MODEL_MISMATCH")
    if receipt.get("transport_class") != clean_room_attestation.get("transport_class"):
        p.append("REVIEW_RECEIPT_TRANSPORT_CLASS_MISMATCH")
    if receipt.get("qualification_digest") != reviewer_qualification.get("qualification_digest"):
        p.append("REVIEW_RECEIPT_QUALIFICATION_BINDING_MISMATCH")
    if receipt.get("clean_room_attestation_digest") != clean_room_attestation.get("attestation_digest"):
        p.append("REVIEW_RECEIPT_CLEAN_ROOM_BINDING_MISMATCH")
    if receipt.get("currentness_state") != "CURRENT":
        p.append("REVIEW_RECEIPT_NOT_CURRENT")
    received = receipt.get("received_sequence")
    if not isinstance(received, int) or received < 1 or received > current_sequence:
        p.append("REVIEW_RECEIPT_SEQUENCE_INVALID")
    if receipt.get("authenticated_transport_receipt") is not True:
        p.append("REVIEW_RECEIPT_AUTHENTICATED_TRANSPORT_REQUIRED")
    if receipt.get("exact_response_bytes_bound") is not True:
        p.append("REVIEW_RECEIPT_EXACT_RESPONSE_BINDING_REQUIRED")

    supplied = receipt.get("receipt_digest")
    if not _sha256(supplied):
        p.append("REVIEW_RECEIPT_DIGEST_INVALID")
    elif supplied != _sealed_digest(receipt, "receipt_digest"):
        p.append("REVIEW_RECEIPT_DIGEST_MISMATCH")
    out = _finish(p, "AUTHENTICATED_REVIEW_RESPONSE_RECEIPT_VALID", "AUTHENTICATED_REVIEW_RESPONSE_RECEIPT_INVALID")
    out["review_evidence_ready"] = out["valid"]
    return out


def review_execution_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_REVIEW_EXECUTION_BOUNDARY_CONSTRUCTION_READY",
        "implemented_surfaces": [20, 21, 22, 23, 24],
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
