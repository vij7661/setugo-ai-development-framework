#!/usr/bin/env python3
"""V15 expected-evidence-universe derivation and negative-space challenge.

Construction-only; no authority effect.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping, Sequence

from review_safe_evidence_v15 import (
    AUTHORITY_EFFECT,
    canonical_hash,
    validate_independently_rooted_proof,
)

DERIVATION_STREAMS = frozenset({"NORMATIVE", "AUTHORITY_SURFACE", "HISTORICAL"})
CHALLENGE_RESULTS = frozenset({"NO_NEW_OBLIGATION_FOUND", "OBLIGATION_ADDED"})


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


def validate_derivation_record(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("UNIVERSE_DERIVATION_SCHEMA_INVALID")
    for key in ("derivation_id", "stream_class", "authority_id", "control_domain_id", "generation_id"):
        if not _nonempty(record.get(key)):
            p.append(f"UNIVERSE_DERIVATION_FIELD_REQUIRED:{key}")
    if record.get("stream_class") not in DERIVATION_STREAMS:
        p.append(f"UNIVERSE_DERIVATION_STREAM_INVALID:{record.get('stream_class')}")
    source_roots = record.get("source_roots")
    if not isinstance(source_roots, list) or not source_roots or not all(_nonempty(x) for x in source_roots):
        p.append("UNIVERSE_DERIVATION_SOURCE_ROOTS_REQUIRED")
    elif len(source_roots) != len(set(source_roots)):
        p.append("UNIVERSE_DERIVATION_SOURCE_ROOT_DUPLICATE")
    obligations = record.get("obligations")
    if not isinstance(obligations, list) or not obligations or not all(_nonempty(x) for x in obligations):
        p.append("UNIVERSE_DERIVATION_OBLIGATIONS_REQUIRED")
    elif len(obligations) != len(set(obligations)):
        p.append("UNIVERSE_DERIVATION_OBLIGATION_DUPLICATE")
    if not _sha256(record.get("source_graph_digest")):
        p.append("UNIVERSE_DERIVATION_SOURCE_GRAPH_DIGEST_INVALID")
    if record.get("candidate_controlled") is not False:
        p.append("UNIVERSE_DERIVATION_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("currentness_state") != "CURRENT":
        p.append("UNIVERSE_DERIVATION_NOT_CURRENT")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("UNIVERSE_DERIVATION_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("UNIVERSE_DERIVATION_RECORD_DIGEST_MISMATCH")
    return _result(p, "UNIVERSE_DERIVATION_RECORD_VALID", "UNIVERSE_DERIVATION_RECORD_INVALID")


def _proof_map(proofs: Sequence[Mapping[str, Any]], problems: list[str]) -> dict[frozenset[str], Mapping[str, Any]]:
    out: dict[frozenset[str], Mapping[str, Any]] = {}
    for i, proof in enumerate(proofs):
        checked = validate_independently_rooted_proof(proof)
        if not checked["valid"]:
            problems.extend(f"UNIVERSE_INDEPENDENCE_PROOF[{i}]:{x}" for x in checked["problems"])
        a, b = proof.get("subject_a"), proof.get("subject_b")
        if isinstance(a, str) and isinstance(b, str):
            key = frozenset((a, b))
            if key in out:
                problems.append(f"UNIVERSE_INDEPENDENCE_PROOF_DUPLICATE:{a}:{b}")
            else:
                out[key] = proof
    return out


def validate_universe_derivation_bundle(bundle: Mapping[str, Any],
                                        independence_proofs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("UNIVERSE_BUNDLE_SCHEMA_INVALID")
    for key in ("candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"UNIVERSE_BUNDLE_FIELD_REQUIRED:{key}")
    rows = bundle.get("derivations")
    if not isinstance(rows, list):
        rows = []
        p.append("UNIVERSE_BUNDLE_DERIVATIONS_REQUIRED")

    by_stream: dict[str, Mapping[str, Any]] = {}
    derivation_digests: list[str] = []
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            p.append(f"UNIVERSE_DERIVATION_MALFORMED:{i}")
            continue
        checked = validate_derivation_record(row)
        if not checked["valid"]:
            p.extend(f"DERIVATION[{i}]:{x}" for x in checked["problems"])
        stream = row.get("stream_class")
        if isinstance(stream, str):
            if stream in by_stream:
                p.append(f"UNIVERSE_DERIVATION_STREAM_DUPLICATE:{stream}")
            else:
                by_stream[stream] = row
        if row.get("generation_id") != bundle.get("generation_id"):
            p.append(f"UNIVERSE_DERIVATION_GENERATION_MISMATCH:{row.get('derivation_id')}")
        if row.get("record_digest") and _sha256(row.get("record_digest")):
            derivation_digests.append(str(row["record_digest"]))

    for missing in sorted(DERIVATION_STREAMS - set(by_stream)):
        p.append(f"UNIVERSE_DERIVATION_STREAM_MISSING:{missing}")

    proof_by_pair = _proof_map(independence_proofs, p)
    domains = [
        str(by_stream[s].get("control_domain_id"))
        for s in sorted(DERIVATION_STREAMS & set(by_stream))
    ]
    if len(domains) != len(set(domains)):
        p.append("UNIVERSE_DERIVATION_CONTROL_DOMAIN_COLLAPSE")
    for a, b in combinations(sorted(set(domains)), 2):
        proof = proof_by_pair.get(frozenset((a, b)))
        if proof is None:
            p.append(f"UNIVERSE_DERIVATION_INDEPENDENCE_PROOF_MISSING:{a}:{b}")
        elif proof.get("result") != "INDEPENDENT":
            p.append(f"UNIVERSE_DERIVATION_INDEPENDENCE_UNPROVEN:{a}:{b}:{proof.get('result')}")

    union: set[str] = set()
    per_stream: dict[str, set[str]] = {}
    roots_per_stream: dict[str, set[str]] = {}
    for stream, row in by_stream.items():
        obligations = set(row.get("obligations", [])) if isinstance(row.get("obligations"), list) else set()
        roots = set(row.get("source_roots", [])) if isinstance(row.get("source_roots"), list) else set()
        per_stream[stream] = obligations
        roots_per_stream[stream] = roots
        union |= obligations

    divergence = {
        obligation: sorted(s for s in DERIVATION_STREAMS if obligation not in per_stream.get(s, set()))
        for obligation in sorted(union)
        if any(obligation not in per_stream.get(s, set()) for s in DERIVATION_STREAMS)
    }

    for obligation in sorted(union):
        asserting = [s for s in DERIVATION_STREAMS if obligation in per_stream.get(s, set())]
        if len(asserting) < 2:
            continue
        common = set.intersection(*(roots_per_stream[s] for s in asserting)) if asserting else set()
        if common:
            p.append(f"UNIVERSE_SHARED_SOURCE_CIRCULARITY:{obligation}:{','.join(sorted(common))}")

    unknown = bundle.get("unclassified_material_surfaces")
    if not isinstance(unknown, list):
        unknown = []
        p.append("UNIVERSE_UNCLASSIFIED_SURFACE_SET_REQUIRED")
    for surface in unknown:
        if not _nonempty(surface):
            p.append("UNIVERSE_UNCLASSIFIED_SURFACE_ID_INVALID")
        else:
            p.append(f"UNIVERSE_UNCLASSIFIED_MATERIAL_SURFACE_BLOCKING:{surface}")

    union_digest = canonical_hash(sorted(union))
    if bundle.get("expected_union_digest") != union_digest:
        p.append("UNIVERSE_AUTHORITATIVE_UNION_DIGEST_MISMATCH")

    supplied = bundle.get("bundle_digest")
    if not _sha256(supplied):
        p.append("UNIVERSE_BUNDLE_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "bundle_digest"):
        p.append("UNIVERSE_BUNDLE_DIGEST_MISMATCH")

    out = _result(p, "EXPECTED_EVIDENCE_UNIVERSE_DERIVED", "EXPECTED_EVIDENCE_UNIVERSE_INVALID")
    out["authoritative_obligations"] = sorted(union)
    out["authoritative_union_digest"] = union_digest
    out["divergence"] = divergence
    out["derivation_record_digests"] = sorted(derivation_digests)
    return out


def validate_universe_challenge(record: Mapping[str, Any],
                                *, authoritative_obligations: Sequence[str]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("UNIVERSE_CHALLENGE_SCHEMA_INVALID")
    for key in ("challenge_id", "candidate_id", "snapshot_id", "generation_id",
                "challenge_authority_id", "challenge_control_domain_id",
                "challenge_algorithm_id", "verifier_id"):
        if not _nonempty(record.get(key)):
            p.append(f"UNIVERSE_CHALLENGE_FIELD_REQUIRED:{key}")
    if record.get("candidate_controlled") is not False:
        p.append("UNIVERSE_CHALLENGE_CANDIDATE_CONTROL_FORBIDDEN")
    if record.get("authority_may_remove_obligations") is not False:
        p.append("UNIVERSE_CHALLENGE_REMOVE_AUTHORITY_FORBIDDEN")
    discovered = record.get("discovered_obligations")
    if not isinstance(discovered, list) or not all(_nonempty(x) for x in discovered):
        p.append("UNIVERSE_CHALLENGE_DISCOVERED_SET_INVALID")
        discovered = []
    if len(discovered) != len(set(discovered)):
        p.append("UNIVERSE_CHALLENGE_DISCOVERED_DUPLICATE")
    removed = record.get("removed_obligations")
    if removed not in ([], None):
        p.append("UNIVERSE_CHALLENGE_REMOVED_OBLIGATION_FORBIDDEN")
    result = record.get("result")
    if result not in CHALLENGE_RESULTS:
        p.append("UNIVERSE_CHALLENGE_RESULT_INVALID")
    if result == "NO_NEW_OBLIGATION_FOUND" and discovered:
        p.append("UNIVERSE_CHALLENGE_NO_NEW_WITH_DISCOVERED")
    if result == "OBLIGATION_ADDED" and not discovered:
        p.append("UNIVERSE_CHALLENGE_ADDED_WITHOUT_DISCOVERED")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("UNIVERSE_CHALLENGE_VERIFIER_INDEPENDENCE_REQUIRED")
    if not _sha256(record.get("source_root_digest")):
        p.append("UNIVERSE_CHALLENGE_SOURCE_ROOT_DIGEST_INVALID")
    if not _sha256(record.get("coverage_digest")):
        p.append("UNIVERSE_CHALLENGE_COVERAGE_DIGEST_INVALID")
    base = set(authoritative_obligations)
    expanded = sorted(base | set(discovered))
    if record.get("expanded_union_digest") != canonical_hash(expanded):
        p.append("UNIVERSE_CHALLENGE_EXPANDED_UNION_DIGEST_MISMATCH")
    supplied = record.get("challenge_digest")
    if not _sha256(supplied):
        p.append("UNIVERSE_CHALLENGE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "challenge_digest"):
        p.append("UNIVERSE_CHALLENGE_DIGEST_MISMATCH")
    out = _result(p, "UNIVERSE_CHALLENGE_VALID", "UNIVERSE_CHALLENGE_INVALID")
    out["expanded_obligations"] = expanded
    out["expanded_union_digest"] = canonical_hash(expanded)
    return out


def validate_universe_completeness_certificate(record: Mapping[str, Any],
                                               *, derivation_result: Mapping[str, Any],
                                               challenge_result: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("UNIVERSE_CERTIFICATE_SCHEMA_INVALID")
    for key in ("certificate_id", "candidate_id", "snapshot_id", "generation_id",
                "certificate_verifier_id"):
        if not _nonempty(record.get(key)):
            p.append(f"UNIVERSE_CERTIFICATE_FIELD_REQUIRED:{key}")
    if not derivation_result.get("valid"):
        p.append("UNIVERSE_CERTIFICATE_DERIVATION_NOT_VALID")
    if not challenge_result.get("valid"):
        p.append("UNIVERSE_CERTIFICATE_CHALLENGE_NOT_VALID")
    expected = challenge_result.get("expanded_union_digest")
    if record.get("authoritative_union_digest") != expected:
        p.append("UNIVERSE_CERTIFICATE_UNION_DIGEST_MISMATCH")
    if record.get("challenge_digest") != record.get("bound_challenge_digest"):
        p.append("UNIVERSE_CERTIFICATE_CHALLENGE_BINDING_MISMATCH")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("UNIVERSE_CERTIFICATE_VERIFIER_INDEPENDENCE_REQUIRED")
    if record.get("unresolved_unknown_count") != 0:
        p.append("UNIVERSE_CERTIFICATE_UNRESOLVED_UNKNOWN_BLOCKING")
    supplied = record.get("certificate_digest")
    if not _sha256(supplied):
        p.append("UNIVERSE_CERTIFICATE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "certificate_digest"):
        p.append("UNIVERSE_CERTIFICATE_DIGEST_MISMATCH")
    return _result(p, "UNIVERSE_COMPLETENESS_CERTIFICATE_VALID", "UNIVERSE_COMPLETENESS_CERTIFICATE_INVALID")


def universe_construction_frontier() -> dict[str, Any]:
    return {
        "state": "V15_EVIDENCE_UNIVERSE_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
    }
