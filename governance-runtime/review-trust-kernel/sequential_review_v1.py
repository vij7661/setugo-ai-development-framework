from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Dict


HIGH_RISK_CLASSES = {
    "PROMOTION_AUTHORITY",
    "TRUST_KERNEL",
    "SECURITY",
    "IDENTITY",
    "PERSISTENCE",
    "MONEY",
    "IRREVERSIBLE_STATE",
}

ALLOWED_R2_KEYS = {
    "review_id",
    "disposition",
    "findings",
    "evidence_ids",
    "uncertainties",
    "model_identity",
    "provider_identity",
    "runtime_identity",
}

FORBIDDEN_MIDDLE_KEYS = {
    "r1_opinion",
    "r1_recommendation",
    "promotion_recommendation",
    "override_disposition",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def route_identity(policy: Dict[str, Any]) -> str:
    relevant = {
        "risk_class": policy.get("risk_class"),
        "promotion_authoritative": bool(policy.get("promotion_authoritative", False)),
        "policy_requires_dual_review": bool(policy.get("policy_requires_dual_review", False)),
        "material_uncertainty_requires_r3": bool(policy.get("material_uncertainty_requires_r3", False)),
    }
    return sha256_json(relevant)


def requires_r3(policy: Dict[str, Any], r2_result: Dict[str, Any]) -> bool:
    """Return the frozen policy decision for whether R3 is required.

    R2 disposition must not bypass mandatory high-risk review. For lower-risk
    requests, only preregistered policy inputs may require R3.
    """
    risk_class = str(policy.get("risk_class", "LOW"))
    if bool(policy.get("promotion_authoritative", False)):
        return True
    if risk_class in HIGH_RISK_CLASSES:
        return True
    if bool(policy.get("policy_requires_dual_review", False)):
        return True
    if bool(policy.get("material_uncertainty_requires_r3", False)) and bool(r2_result.get("uncertainties")):
        return True
    return False


def normalize_r2_result(r2_result: Dict[str, Any]) -> Dict[str, Any]:
    """Create a deterministic, lossless normalized handoff for governed R2 fields."""
    missing = [key for key in ("review_id", "disposition", "findings") if key not in r2_result]
    if missing:
        raise ValueError(f"R2 result missing mandatory fields: {','.join(sorted(missing))}")

    forbidden = sorted(FORBIDDEN_MIDDLE_KEYS.intersection(r2_result.keys()))
    if forbidden:
        raise ValueError(f"R1-middle opinion/recommendation fields forbidden: {','.join(forbidden)}")

    unknown = sorted(set(r2_result.keys()) - ALLOWED_R2_KEYS)
    if unknown:
        raise ValueError(f"Unregistered R2 material fields cannot be silently dropped: {','.join(unknown)}")

    return {key: deepcopy(r2_result[key]) for key in sorted(r2_result.keys())}


def build_frozen_handoff(
    *,
    review_request: Dict[str, Any],
    frozen_packet: Dict[str, Any],
    policy: Dict[str, Any],
    r2_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the R1-middle handoff without changing evidence or adding an opinion."""
    required_packet = {
        "candidate_sha",
        "base_sha",
        "evidence_manifest_hash",
        "corpus_hash",
    }
    missing = sorted(required_packet - set(frozen_packet.keys()))
    if missing:
        raise ValueError(f"Frozen packet missing identity fields: {','.join(missing)}")

    normalized = normalize_r2_result(r2_result)
    handoff = {
        "schema_version": 1,
        "review_request_hash": sha256_json(review_request),
        "candidate_sha": frozen_packet["candidate_sha"],
        "base_sha": frozen_packet["base_sha"],
        "evidence_manifest_hash": frozen_packet["evidence_manifest_hash"],
        "corpus_hash": frozen_packet["corpus_hash"],
        "frozen_packet_hash": sha256_json(frozen_packet),
        "routing_policy_hash": route_identity(policy),
        "r3_required": requires_r3(policy, r2_result),
        "r2_raw_hash": sha256_json(r2_result),
        "r2_normalized": normalized,
        "r2_normalized_hash": sha256_json(normalized),
    }
    handoff["handoff_hash"] = sha256_json(handoff)
    return handoff


def verify_frozen_handoff(
    handoff: Dict[str, Any],
    *,
    review_request: Dict[str, Any],
    frozen_packet: Dict[str, Any],
    policy: Dict[str, Any],
    r2_result: Dict[str, Any],
) -> bool:
    expected = build_frozen_handoff(
        review_request=review_request,
        frozen_packet=frozen_packet,
        policy=policy,
        r2_result=r2_result,
    )
    return handoff == expected
