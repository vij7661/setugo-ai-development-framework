"""V24-I3 effective-control and independent capability/deployment construction."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _index(rows: Any, key: str, prefix: str, problems: list[str]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(rows, list):
        problems.append(f"{prefix}_LIST_REQUIRED")
        return {}
    out = {}
    for row in rows:
        if not isinstance(row, Mapping):
            problems.append(f"{prefix}_ROW_MALFORMED")
            continue
        rid = row.get(key)
        if not isinstance(rid, str) or not rid:
            problems.append(f"{prefix}_ID_INVALID")
            continue
        if rid in out:
            problems.append(f"{prefix}_ID_DUPLICATE:{rid}")
        out[rid] = row
    return out


def validate_effective_control_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    p: list[str] = []
    gen = bundle.get("governance_generation_id")
    sources = _index(bundle.get("control_sources"), "source_id", "SOURCE", p)
    rels = _index(bundle.get("relationships"), "relationship_id", "RELATIONSHIP", p)
    capabilities = _index(bundle.get("capability_inventory"), "capability_id", "CAPABILITY", p)
    attestations = _index(bundle.get("capability_attestations"), "attestation_id", "ATTESTATION", p)
    observations = _index(bundle.get("deployment_observations"), "observation_id", "OBSERVATION", p)

    mandatory = bundle.get("mandatory_source_classes")
    if not isinstance(mandatory, list) or not mandatory or not all(isinstance(x, str) and x for x in mandatory):
        p.append("MANDATORY_SOURCE_CLASS_SET_REQUIRED")
        mandatory = []
    present_classes = {x.get("source_class") for x in sources.values()}
    for cls in mandatory:
        if cls not in present_classes:
            p.append(f"MANDATORY_SOURCE_CLASS_MISSING:{cls}")

    for sid, source in sources.items():
        if source.get("generation_id") != gen:
            p.append(f"SOURCE_GENERATION_MISMATCH:{sid}")
        if not source.get("independent_derivation_evidence_digest"):
            p.append(f"SOURCE_INDEPENDENT_DERIVATION_REQUIRED:{sid}")
        if not source.get("control_domain_id"):
            p.append(f"SOURCE_CONTROL_DOMAIN_REQUIRED:{sid}")

    required_pairs = bundle.get("required_relationship_queries")
    if not isinstance(required_pairs, list):
        p.append("REQUIRED_RELATIONSHIP_QUERY_SET_REQUIRED")
        required_pairs = []
    answers: set[tuple[str, str]] = set()
    positive_edges: list[tuple[str, str]] = []
    for rid, rel in rels.items():
        subject = rel.get("subject_id")
        source = rel.get("source_id")
        status = rel.get("status")
        if source not in sources:
            p.append(f"RELATIONSHIP_SOURCE_UNKNOWN:{rid}:{source}")
        if not isinstance(subject, str) or not subject:
            p.append(f"RELATIONSHIP_SUBJECT_INVALID:{rid}")
            continue
        if status not in {"CONTROL_PRESENT", "NO_RELATIONSHIP_EVIDENCE_FOR_BOUND_SCOPE"}:
            p.append(f"RELATIONSHIP_STATUS_INVALID:{rid}")
        if status == "NO_RELATIONSHIP_EVIDENCE_FOR_BOUND_SCOPE" and not rel.get("negative_evidence_digest"):
            p.append(f"RELATIONSHIP_NEGATIVE_EVIDENCE_REQUIRED:{rid}")
        if status == "CONTROL_PRESENT":
            positive_edges.append((source, subject))
        if rel.get("generation_id") != gen:
            p.append(f"RELATIONSHIP_GENERATION_MISMATCH:{rid}")
        answers.add((subject, source))
    for pair in required_pairs:
        if not isinstance(pair, Mapping):
            p.append("RELATIONSHIP_QUERY_MALFORMED")
            continue
        key = (pair.get("subject_id"), pair.get("source_id"))
        if key not in answers:
            p.append(f"RELATIONSHIP_QUERY_UNANSWERED:{key[0]}:{key[1]}")

    claimed_closure = bundle.get("effective_control_closure")
    if not isinstance(claimed_closure, Mapping):
        p.append("EFFECTIVE_CONTROL_CLOSURE_REQUIRED")
    else:
        edges = {tuple(x) for x in claimed_closure.get("control_edges", []) if isinstance(x, list) and len(x) == 2}
        for edge in positive_edges:
            if edge not in edges:
                p.append(f"EFFECTIVE_CONTROL_EDGE_OMITTED:{edge[0]}:{edge[1]}")
        threshold_sets = claimed_closure.get("root_threshold_capable_control_sets")
        if not isinstance(threshold_sets, list) or not threshold_sets:
            p.append("ROOT_THRESHOLD_CAPABLE_CONTROL_SETS_REQUIRED")

    attestation_for_capability: dict[str, list[Mapping[str, Any]]] = {}
    for aid, att in attestations.items():
        cid = att.get("capability_id")
        attestation_for_capability.setdefault(cid, []).append(att)
        if cid not in capabilities:
            p.append(f"ATTESTATION_CAPABILITY_UNKNOWN:{aid}:{cid}")
        if not att.get("independent_attestor_id") or not att.get("attestor_control_domain_id"):
            p.append(f"ATTESTATION_INDEPENDENT_ATTESTOR_REQUIRED:{aid}")
        if not att.get("measured_deployment_digest") or not att.get("measured_configuration_digest"):
            p.append(f"ATTESTATION_MEASUREMENT_REQUIRED:{aid}")
        if att.get("generation_id") != gen:
            p.append(f"ATTESTATION_GENERATION_MISMATCH:{aid}")

    latest_observation: dict[str, Mapping[str, Any]] = {}
    for oid, obs in observations.items():
        cid = obs.get("capability_id")
        if cid not in capabilities:
            p.append(f"OBSERVATION_CAPABILITY_UNKNOWN:{oid}:{cid}")
        latest_observation[cid] = obs

    for cid, cap in capabilities.items():
        if cap.get("generation_id") != gen:
            p.append(f"CAPABILITY_GENERATION_MISMATCH:{cid}")
        owner_domain = cap.get("owner_control_domain_id")
        if not owner_domain:
            p.append(f"CAPABILITY_OWNER_DOMAIN_REQUIRED:{cid}")
        rows = attestation_for_capability.get(cid, [])
        if not rows:
            p.append(f"CAPABILITY_ATTESTATION_MISSING:{cid}")
            continue
        current = [a for a in rows if a.get("state") == "CURRENT"]
        if len(current) != 1:
            p.append(f"CAPABILITY_CURRENT_ATTESTATION_COUNT_INVALID:{cid}:{len(current)}")
            continue
        att = current[0]
        if owner_domain and att.get("attestor_control_domain_id") == owner_domain:
            p.append(f"CAPABILITY_ATTESTOR_NOT_INDEPENDENT:{cid}")
        obs = latest_observation.get(cid)
        if obs is None:
            p.append(f"CAPABILITY_DEPLOYMENT_OBSERVATION_MISSING:{cid}")
        else:
            if obs.get("deployment_digest") != att.get("measured_deployment_digest") or obs.get("configuration_digest") != att.get("measured_configuration_digest"):
                p.append(f"CAPABILITY_ATTESTATION_STALE_DRIFT:{cid}")
            if obs.get("generation_id") != gen:
                p.append(f"OBSERVATION_GENERATION_MISMATCH:{cid}")

    p = sorted(set(p))
    return {
        "state": "EFFECTIVE_CONTROL_CONSTRUCTION_VALID" if not p else "EFFECTIVE_CONTROL_INCOMPLETE",
        "qualified": False,
        "problems": p,
        "counts": {"sources": len(sources), "relationships": len(rels), "capabilities": len(capabilities), "attestations": len(attestations), "observations": len(observations)},
        "bundle_digest": digest(bundle),
        "authority_effect": AUTHORITY_EFFECT,
    }
