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

FORBIDDEN_MIDDLE_KEYS = {
    "r1_opinion",
    "r1_recommendation",
    "promotion_recommendation",
    "override_disposition",
}

REQUIRED_PLATFORM_R2_KEYS = {
    "review_request_id",
    "reviewed_artifact_commit",
    "reviewer",
    "disposition",
    "findings",
    "evidence_assessment",
    "independence_attestation",
    "review_coverage",
}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


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


def validate_platform_r2(
    *,
    review_request: Dict[str, Any],
    r2_result: Dict[str, Any],
) -> None:
    missing = sorted(REQUIRED_PLATFORM_R2_KEYS - set(r2_result.keys()))
    if missing:
        raise ValueError(f"platform R2 missing mandatory fields: {','.join(missing)}")

    forbidden = sorted(FORBIDDEN_MIDDLE_KEYS.intersection(r2_result.keys()))
    if forbidden:
        raise ValueError(f"R1-middle opinion/recommendation fields forbidden: {','.join(forbidden)}")

    request_id = review_request.get("review_request_id")
    if r2_result.get("review_request_id") != request_id:
        raise ValueError("R2 ReviewRequest ID mismatch")

    artifact = review_request.get("artifact")
    if not isinstance(artifact, dict) or not isinstance(artifact.get("commit"), str):
        raise ValueError("ReviewRequest artifact.commit required")
    if r2_result.get("reviewed_artifact_commit") != artifact["commit"]:
        raise ValueError("R2 reviewed candidate mismatch")

    reviewer = r2_result.get("reviewer")
    if not isinstance(reviewer, dict):
        raise ValueError("R2 reviewer object required")
    for field in ("provider", "model"):
        value = reviewer.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"R2 reviewer.{field} required")

    if not isinstance(r2_result.get("findings"), list):
        raise ValueError("R2 findings must be list")
    if not isinstance(r2_result.get("review_coverage"), list) or not r2_result["review_coverage"]:
        raise ValueError("R2 review_coverage must be nonempty list")
    if not isinstance(r2_result.get("evidence_assessment"), str) or not r2_result["evidence_assessment"].strip():
        raise ValueError("R2 evidence_assessment required")
    if not isinstance(r2_result.get("independence_attestation"), str) or not r2_result["independence_attestation"].strip():
        raise ValueError("R2 independence_attestation required")


def build_frozen_platform_handoff(
    *,
    review_request: Dict[str, Any],
    policy: Dict[str, Any],
    r2_result: Dict[str, Any],
    corpus_hash: str,
    evidence_manifest_hash: str,
    provider_api_authenticated: bool,
) -> Dict[str, Any]:
    validate_platform_r2(review_request=review_request, r2_result=r2_result)

    if not isinstance(corpus_hash, str) or not corpus_hash.startswith("sha256:"):
        raise ValueError("corpus_hash must be sha256 identity")
    if not isinstance(evidence_manifest_hash, str) or not evidence_manifest_hash.startswith("sha256:"):
        raise ValueError("evidence_manifest_hash must be sha256 identity")

    artifact = review_request["artifact"]
    r2_raw = deepcopy(r2_result)
    handoff = {
        "schema_version": 2,
        "handoff_type": "AUTHENTICATED_PLATFORM_R2_TO_R3",
        "review_request_id": review_request["review_request_id"],
        "review_request_hash": sha256_json(review_request),
        "candidate_sha": artifact["commit"],
        "evidence_manifest_hash": evidence_manifest_hash,
        "corpus_hash": corpus_hash,
        "routing_policy_hash": route_identity(policy),
        "r3_required": requires_r3(policy, r2_result),
        "provider_api_authenticated": bool(provider_api_authenticated),
        "r2_raw": r2_raw,
        "r2_raw_hash": sha256_json(r2_raw),
        "r1_middle_opinion": None,
        "authority_effect": "R2_EVIDENCE_ONLY_PENDING_R3_AND_FINAL_ADJUDICATION",
    }
    handoff["handoff_hash"] = sha256_json(handoff)
    return handoff


def verify_frozen_platform_handoff(
    handoff: Dict[str, Any],
    *,
    review_request: Dict[str, Any],
    policy: Dict[str, Any],
    r2_result: Dict[str, Any],
    corpus_hash: str,
    evidence_manifest_hash: str,
    provider_api_authenticated: bool,
) -> bool:
    expected = build_frozen_platform_handoff(
        review_request=review_request,
        policy=policy,
        r2_result=r2_result,
        corpus_hash=corpus_hash,
        evidence_manifest_hash=evidence_manifest_hash,
        provider_api_authenticated=provider_api_authenticated,
    )
    return handoff == expected
