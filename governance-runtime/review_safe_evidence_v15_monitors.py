#!/usr/bin/env python3
"""V15 hidden-evidence monitor quorum and coverage certificates.

Construction-only; no authority effect.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping, Sequence

from review_safe_evidence_v15 import AUTHORITY_EFFECT, canonical_hash, validate_independently_rooted_proof

MONITOR_RESULTS = frozenset({"NO_REOPEN_FOUND", "REOPEN_REQUIRED"})


def _nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _sealed_digest(record: Mapping[str, Any], field: str) -> str:
    return canonical_hash({k: v for k, v in record.items() if k != field})


def _result(problems: list[str], ok: str, bad: str) -> dict[str, Any]:
    p = sorted(set(problems))
    return {"state": ok if not p else bad, "valid": not p, "qualified": False,
            "problems": p, "authority_effect": AUTHORITY_EFFECT}


def validate_monitor_record(record: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("HIDDEN_MONITOR_RECORD_SCHEMA_INVALID")
    for key in (
        "monitor_id", "monitor_control_domain_id", "implementation_id",
        "implementation_control_domain_id", "algorithm_id", "obligation_id",
        "candidate_id", "snapshot_id", "generation_id",
    ):
        if not _nonempty(record.get(key)):
            p.append(f"HIDDEN_MONITOR_FIELD_REQUIRED:{key}")
    for key in ("raw_evidence_root_digest", "algorithm_digest", "observation_digest"):
        if not _sha256(record.get(key)):
            p.append(f"HIDDEN_MONITOR_SHA256_INVALID:{key}")
    if record.get("result") not in MONITOR_RESULTS:
        p.append("HIDDEN_MONITOR_RESULT_INVALID")
    if record.get("currentness_state") != "CURRENT":
        p.append("HIDDEN_MONITOR_NOT_CURRENT")
    if record.get("candidate_controlled") is not False:
        p.append("HIDDEN_MONITOR_CANDIDATE_CONTROL_FORBIDDEN")
    seq = record.get("observed_sequence")
    if not isinstance(seq, int) or seq < 1:
        p.append("HIDDEN_MONITOR_SEQUENCE_INVALID")
    supplied = record.get("record_digest")
    if not _sha256(supplied):
        p.append("HIDDEN_MONITOR_RECORD_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "record_digest"):
        p.append("HIDDEN_MONITOR_RECORD_DIGEST_MISMATCH")
    return _result(p, "HIDDEN_MONITOR_RECORD_VALID", "HIDDEN_MONITOR_RECORD_INVALID")


def _proof_index(proofs: Sequence[Mapping[str, Any]], problems: list[str]) -> dict[frozenset[str], Mapping[str, Any]]:
    index: dict[frozenset[str], Mapping[str, Any]] = {}
    for i, proof in enumerate(proofs):
        checked = validate_independently_rooted_proof(proof)
        if not checked["valid"]:
            problems.extend(f"MONITOR_INDEPENDENCE_PROOF[{i}]:{x}" for x in checked["problems"])
        a, b = proof.get("subject_a"), proof.get("subject_b")
        if isinstance(a, str) and isinstance(b, str):
            key = frozenset((a, b))
            if key in index:
                problems.append(f"MONITOR_INDEPENDENCE_PROOF_DUPLICATE:{a}:{b}")
            else:
                index[key] = proof
    return index


def validate_hidden_monitor_bundle(bundle: Mapping[str, Any], *,
                                  expected_obligations: Sequence[str],
                                  independence_proofs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    p: list[str] = []
    if bundle.get("schema_version") != 1:
        p.append("HIDDEN_MONITOR_BUNDLE_SCHEMA_INVALID")
    for key in ("bundle_id", "candidate_id", "snapshot_id", "generation_id"):
        if not _nonempty(bundle.get(key)):
            p.append(f"HIDDEN_MONITOR_BUNDLE_FIELD_REQUIRED:{key}")
    if not _sha256(bundle.get("raw_evidence_root_digest")):
        p.append("HIDDEN_MONITOR_BUNDLE_RAW_ROOT_INVALID")
    threshold = bundle.get("threshold_control_domains")
    if not isinstance(threshold, int) or threshold < 2:
        p.append("HIDDEN_MONITOR_THRESHOLD_INVALID")
        threshold = 0
    monitors = bundle.get("monitors")
    if not isinstance(monitors, list) or len(monitors) < 3:
        monitors = [] if not isinstance(monitors, list) else monitors
        p.append("HIDDEN_MONITOR_AT_LEAST_THREE_IDENTITIES_REQUIRED")
    ids: set[str] = set()
    domains: set[str] = set()
    implementation_ids: set[str] = set()
    implementation_domains: set[str] = set()
    for i, m in enumerate(monitors):
        if not isinstance(m, Mapping):
            p.append(f"HIDDEN_MONITOR_DESCRIPTOR_MALFORMED:{i}")
            continue
        mid, domain = m.get("monitor_id"), m.get("control_domain_id")
        impl, impl_domain = m.get("implementation_id"), m.get("implementation_control_domain_id")
        if not _nonempty(mid) or not _nonempty(domain) or not _nonempty(impl) or not _nonempty(impl_domain):
            p.append(f"HIDDEN_MONITOR_DESCRIPTOR_FIELDS_REQUIRED:{i}")
            continue
        if mid in ids:
            p.append(f"HIDDEN_MONITOR_ID_DUPLICATE:{mid}")
        ids.add(str(mid)); domains.add(str(domain)); implementation_ids.add(str(impl)); implementation_domains.add(str(impl_domain))
        if m.get("currentness_state") != "CURRENT":
            p.append(f"HIDDEN_MONITOR_DESCRIPTOR_NOT_CURRENT:{mid}")
        if m.get("candidate_controlled") is not False:
            p.append(f"HIDDEN_MONITOR_DESCRIPTOR_CANDIDATE_CONTROL_FORBIDDEN:{mid}")
    if threshold > len(domains):
        p.append("HIDDEN_MONITOR_THRESHOLD_EXCEEDS_INDEPENDENT_DOMAIN_COUNT")
    if len(domains) < 2:
        p.append("HIDDEN_MONITOR_INDEPENDENT_DOMAIN_COUNT_INSUFFICIENT")
    if len(implementation_ids) < 2 or len(implementation_domains) < 2:
        p.append("HIDDEN_MONITOR_IMPLEMENTATION_DIVERSITY_INSUFFICIENT")

    proof_index = _proof_index(independence_proofs, p)
    for a, b in combinations(sorted(domains), 2):
        proof = proof_index.get(frozenset((a, b)))
        if proof is None:
            p.append(f"HIDDEN_MONITOR_DOMAIN_INDEPENDENCE_PROOF_MISSING:{a}:{b}")
        elif proof.get("result") != "INDEPENDENT":
            p.append(f"HIDDEN_MONITOR_DOMAIN_INDEPENDENCE_UNPROVEN:{a}:{b}:{proof.get('result')}")
    for a, b in combinations(sorted(implementation_domains), 2):
        proof = proof_index.get(frozenset((a, b)))
        if proof is None:
            p.append(f"HIDDEN_MONITOR_IMPLEMENTATION_INDEPENDENCE_PROOF_MISSING:{a}:{b}")
        elif proof.get("result") != "INDEPENDENT":
            p.append(f"HIDDEN_MONITOR_IMPLEMENTATION_INDEPENDENCE_UNPROVEN:{a}:{b}:{proof.get('result')}")

    records = bundle.get("records")
    if not isinstance(records, list):
        records = []
        p.append("HIDDEN_MONITOR_RECORD_SET_REQUIRED")
    by_key: dict[tuple[str, str], Mapping[str, Any]] = {}
    reopen_obligations: set[str] = set()
    for i, record in enumerate(records):
        if not isinstance(record, Mapping):
            p.append(f"HIDDEN_MONITOR_RECORD_MALFORMED:{i}")
            continue
        checked = validate_monitor_record(record)
        if not checked["valid"]:
            p.extend(f"MONITOR_RECORD[{i}]:{x}" for x in checked["problems"])
        mid, oid = record.get("monitor_id"), record.get("obligation_id")
        if isinstance(mid, str) and isinstance(oid, str):
            key = (mid, oid)
            if key in by_key:
                p.append(f"HIDDEN_MONITOR_RECORD_DUPLICATE:{mid}:{oid}")
            else:
                by_key[key] = record
        if record.get("candidate_id") != bundle.get("candidate_id") or record.get("snapshot_id") != bundle.get("snapshot_id") or record.get("generation_id") != bundle.get("generation_id"):
            p.append(f"HIDDEN_MONITOR_RECORD_CONTEXT_MISMATCH:{mid}:{oid}")
        if record.get("raw_evidence_root_digest") != bundle.get("raw_evidence_root_digest"):
            p.append(f"HIDDEN_MONITOR_RECORD_RAW_ROOT_MISMATCH:{mid}:{oid}")
        descriptor = next((m for m in monitors if isinstance(m, Mapping) and m.get("monitor_id") == mid), None)
        if descriptor is None:
            p.append(f"HIDDEN_MONITOR_RECORD_UNKNOWN_MONITOR:{mid}")
        else:
            if record.get("monitor_control_domain_id") != descriptor.get("control_domain_id"):
                p.append(f"HIDDEN_MONITOR_RECORD_DOMAIN_MISMATCH:{mid}:{oid}")
            if record.get("implementation_id") != descriptor.get("implementation_id") or record.get("implementation_control_domain_id") != descriptor.get("implementation_control_domain_id"):
                p.append(f"HIDDEN_MONITOR_RECORD_IMPLEMENTATION_MISMATCH:{mid}:{oid}")
        if record.get("result") == "REOPEN_REQUIRED" and isinstance(oid, str):
            reopen_obligations.add(oid)

    expected = set(expected_obligations)
    if not expected or not all(_nonempty(x) for x in expected):
        p.append("HIDDEN_MONITOR_EXPECTED_OBLIGATIONS_INVALID")
    for oid in sorted(expected):
        for mid in sorted(ids):
            if (mid, oid) not in by_key:
                p.append(f"HIDDEN_MONITOR_SILENCE_BLOCKING:{mid}:{oid}")
    for mid, oid in sorted(set(by_key) - {(m, o) for m in ids for o in expected}):
        p.append(f"HIDDEN_MONITOR_UNEXPECTED_RECORD:{mid}:{oid}")

    supplied = bundle.get("bundle_digest")
    if not _sha256(supplied):
        p.append("HIDDEN_MONITOR_BUNDLE_DIGEST_INVALID")
    elif supplied != _sealed_digest(bundle, "bundle_digest"):
        p.append("HIDDEN_MONITOR_BUNDLE_DIGEST_MISMATCH")

    out = _result(p, "HIDDEN_EVIDENCE_MONITOR_BUNDLE_VALID", "HIDDEN_EVIDENCE_MONITOR_BUNDLE_INVALID")
    out["reopen_required_obligations"] = sorted(reopen_obligations)
    out["promotion_blocked"] = (not out["valid"]) or bool(reopen_obligations)
    out["monitor_identity_count"] = len(ids)
    out["control_domain_count"] = len(domains)
    out["implementation_count"] = len(implementation_ids)
    return out


def validate_hidden_evidence_coverage_certificate(record: Mapping[str, Any], *,
                                                  monitor_result: Mapping[str, Any],
                                                  expected_obligations: Sequence[str]) -> dict[str, Any]:
    p: list[str] = []
    if record.get("schema_version") != 1:
        p.append("HIDDEN_COVERAGE_CERTIFICATE_SCHEMA_INVALID")
    for key in ("certificate_id", "candidate_id", "snapshot_id", "generation_id",
                "verifier_id", "verifier_control_domain_id"):
        if not _nonempty(record.get(key)):
            p.append(f"HIDDEN_COVERAGE_CERTIFICATE_FIELD_REQUIRED:{key}")
    for key in ("monitor_bundle_digest", "raw_evidence_root_digest", "obligation_set_digest"):
        if not _sha256(record.get(key)):
            p.append(f"HIDDEN_COVERAGE_CERTIFICATE_SHA256_INVALID:{key}")
    if record.get("verifier_independence_result") != "INDEPENDENT":
        p.append("HIDDEN_COVERAGE_CERTIFICATE_VERIFIER_INDEPENDENCE_REQUIRED")
    if not monitor_result.get("valid"):
        p.append("HIDDEN_COVERAGE_CERTIFICATE_MONITOR_BUNDLE_INVALID")
    expected = sorted(set(expected_obligations))
    if record.get("obligation_set_digest") != canonical_hash(expected):
        p.append("HIDDEN_COVERAGE_CERTIFICATE_OBLIGATION_SET_MISMATCH")
    recorded = record.get("obligation_results")
    if not isinstance(recorded, Mapping) or set(recorded) != set(expected):
        recorded = {} if not isinstance(recorded, Mapping) else recorded
        p.append("HIDDEN_COVERAGE_CERTIFICATE_OBLIGATION_RESULTS_MISMATCH")
    reopen = set(monitor_result.get("reopen_required_obligations", []))
    for oid in expected:
        expected_result = "REOPEN_REQUIRED" if oid in reopen else "NO_REOPEN_FOUND"
        if recorded.get(oid) != expected_result:
            p.append(f"HIDDEN_COVERAGE_CERTIFICATE_RESULT_MISMATCH:{oid}:{expected_result}")
    if record.get("currentness_state") != "CURRENT":
        p.append("HIDDEN_COVERAGE_CERTIFICATE_NOT_CURRENT")
    supplied = record.get("certificate_digest")
    if not _sha256(supplied):
        p.append("HIDDEN_COVERAGE_CERTIFICATE_DIGEST_INVALID")
    elif supplied != _sealed_digest(record, "certificate_digest"):
        p.append("HIDDEN_COVERAGE_CERTIFICATE_DIGEST_MISMATCH")
    out = _result(p, "HIDDEN_EVIDENCE_COVERAGE_CERTIFICATE_VALID", "HIDDEN_EVIDENCE_COVERAGE_CERTIFICATE_INVALID")
    out["promotion_blocked"] = (not out["valid"]) or any(v == "REOPEN_REQUIRED" for v in recorded.values())
    return out


def monitor_construction_frontier() -> dict[str, Any]:
    return {"state": "V15_HIDDEN_MONITOR_CONSTRUCTION_READY", "qualified": False,
            "implementation_qualification": "NOT_CLAIMED", "authority_effect": AUTHORITY_EFFECT}
