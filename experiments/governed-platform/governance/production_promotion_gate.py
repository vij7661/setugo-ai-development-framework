from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

TESTING = "TESTING"
RELEASE_CANDIDATE = "RELEASE_CANDIDATE"
PRODUCTION = "PRODUCTION"


class PromotionDenied(ValueError):
    pass


def canonical_digest(obj: Dict[str, Any]) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _require_nonempty(obj: Dict[str, Any], *fields: str) -> None:
    missing = [f for f in fields if not isinstance(obj.get(f), str) or not obj[f].strip()]
    if missing:
        raise PromotionDenied("MISSING_REQUIRED:" + ",".join(missing))


def _without_digest(obj: Dict[str, Any], digest_field: str) -> Dict[str, Any]:
    return {k: v for k, v in obj.items() if k != digest_field}


def verify_self_digest(obj: Dict[str, Any], digest_field: str) -> None:
    _require_nonempty(obj, digest_field)
    expected = canonical_digest(_without_digest(obj, digest_field))
    if obj[digest_field] != expected:
        raise PromotionDenied(f"INVALID_{digest_field.upper()}")


def make_bound_evidence(kind: str, source_commit_sha: str, artifact_digest: str, evidence_id: str) -> Dict[str, Any]:
    body = {
        "kind": kind,
        "source_commit_sha": source_commit_sha,
        "artifact_digest": artifact_digest,
        "evidence_id": evidence_id,
    }
    body["evidence_digest"] = canonical_digest(body)
    return body


def verify_bound_evidence(evidence: Dict[str, Any], *, kind: str, source_commit_sha: str, artifact_digest: str) -> None:
    _require_nonempty(evidence, "kind", "source_commit_sha", "artifact_digest", "evidence_id", "evidence_digest")
    if evidence["kind"] != kind:
        raise PromotionDenied(f"WRONG_EVIDENCE_KIND:{kind}")
    if evidence["source_commit_sha"] != source_commit_sha:
        raise PromotionDenied(f"STALE_EVIDENCE_SHA:{kind}")
    if evidence["artifact_digest"] != artifact_digest:
        raise PromotionDenied(f"STALE_EVIDENCE_ARTIFACT:{kind}")
    expected = canonical_digest(_without_digest(evidence, "evidence_digest"))
    if evidence["evidence_digest"] != expected:
        raise PromotionDenied(f"INVALID_EVIDENCE_DIGEST:{kind}")


def build_release_candidate_manifest(
    *,
    promotion_id: str,
    source_commit_sha: str,
    artifact_digest: str,
    artifact_type: str,
    build_provenance_digest: str,
    testing_run_ids: list[str],
    testing_evidence: Dict[str, Any],
    review_evidence: Dict[str, Any],
    final_adjudication_evidence: Dict[str, Any],
    requested_from_environment: str = TESTING,
    requested_to_environment: str = RELEASE_CANDIDATE,
    model_claim: Optional[str] = None,
) -> Dict[str, Any]:
    if requested_from_environment != TESTING or requested_to_environment != RELEASE_CANDIDATE:
        raise PromotionDenied("INVALID_ORDERED_TRANSITION")
    for v, name in [
        (promotion_id, "promotion_id"),
        (source_commit_sha, "source_commit_sha"),
        (artifact_digest, "artifact_digest"),
        (artifact_type, "artifact_type"),
        (build_provenance_digest, "build_provenance_digest"),
    ]:
        if not isinstance(v, str) or not v.strip():
            raise PromotionDenied(f"MISSING_REQUIRED:{name}")
    if not testing_run_ids or not all(isinstance(x, str) and x.strip() for x in testing_run_ids):
        raise PromotionDenied("MISSING_REQUIRED:testing_run_ids")

    verify_bound_evidence(testing_evidence, kind="TESTING", source_commit_sha=source_commit_sha, artifact_digest=artifact_digest)
    verify_bound_evidence(review_evidence, kind="REVIEW", source_commit_sha=source_commit_sha, artifact_digest=artifact_digest)
    verify_bound_evidence(final_adjudication_evidence, kind="FINAL_ADJUDICATION", source_commit_sha=source_commit_sha, artifact_digest=artifact_digest)

    body = {
        "schema_version": 1,
        "promotion_id": promotion_id,
        "source_commit_sha": source_commit_sha,
        "artifact_digest": artifact_digest,
        "artifact_type": artifact_type,
        "build_provenance_digest": build_provenance_digest,
        "testing_run_ids": list(testing_run_ids),
        "testing_evidence_digest": testing_evidence["evidence_digest"],
        "review_evidence_digest": review_evidence["evidence_digest"],
        "final_adjudication_digest": final_adjudication_evidence["evidence_digest"],
        "from_environment": TESTING,
        "to_environment": RELEASE_CANDIDATE,
        "prior_promotion_digest": None,
        "model_claim": model_claim,
        "authority_effect": "RELEASE_CANDIDATE_ELIGIBLE_ONLY",
    }
    body["manifest_digest"] = canonical_digest(body)
    return body


def build_production_authorization(
    *,
    authorization_id: str,
    release_candidate_manifest: Dict[str, Any],
    authorization_evidence_digest: str,
    expires_at: Optional[str],
) -> Dict[str, Any]:
    verify_self_digest(release_candidate_manifest, "manifest_digest")
    if release_candidate_manifest.get("to_environment") != RELEASE_CANDIDATE:
        raise PromotionDenied("AUTHORIZATION_REQUIRES_RELEASE_CANDIDATE")
    for v, name in [
        (authorization_id, "authorization_id"),
        (authorization_evidence_digest, "authorization_evidence_digest"),
    ]:
        if not isinstance(v, str) or not v.strip():
            raise PromotionDenied(f"MISSING_REQUIRED:{name}")
    body = {
        "schema_version": 1,
        "authorization_id": authorization_id,
        "promotion_id": release_candidate_manifest["promotion_id"],
        "source_commit_sha": release_candidate_manifest["source_commit_sha"],
        "artifact_digest": release_candidate_manifest["artifact_digest"],
        "release_candidate_manifest_digest": release_candidate_manifest["manifest_digest"],
        "authorized_environment": PRODUCTION,
        "authorization_evidence_digest": authorization_evidence_digest,
        "expires_at": expires_at,
    }
    body["authorization_digest"] = canonical_digest(body)
    return body


def _expired(expires_at: Optional[str], now_iso: str) -> bool:
    if expires_at is None:
        return False
    exp = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    now = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now >= exp


def evaluate_production_promotion(
    *,
    release_candidate_manifest: Dict[str, Any],
    production_authorization: Optional[Dict[str, Any]],
    source_commit_sha: str,
    artifact_digest: str,
    current_head_sha: str,
    credential_domain: str,
    now_iso: str,
    requested_environment: str = PRODUCTION,
    model_claim: Optional[str] = None,
) -> Dict[str, Any]:
    reasons: list[str] = []
    try:
        verify_self_digest(release_candidate_manifest, "manifest_digest")
    except PromotionDenied as exc:
        reasons.append(str(exc))

    if requested_environment != PRODUCTION:
        reasons.append("REQUESTED_ENVIRONMENT_NOT_PRODUCTION")
    if release_candidate_manifest.get("from_environment") != TESTING or release_candidate_manifest.get("to_environment") != RELEASE_CANDIDATE:
        reasons.append("INVALID_ORDERED_TRANSITION")
    if release_candidate_manifest.get("source_commit_sha") != source_commit_sha:
        reasons.append("SOURCE_SHA_SUBSTITUTION")
    if release_candidate_manifest.get("artifact_digest") != artifact_digest:
        reasons.append("ARTIFACT_DIGEST_SUBSTITUTION")
    if current_head_sha != source_commit_sha:
        reasons.append("HEAD_DRIFT")
    if credential_domain != "production":
        reasons.append("NON_PRODUCTION_CREDENTIAL_DOMAIN")

    if production_authorization is None:
        reasons.append("MISSING_PRODUCTION_AUTHORIZATION")
    else:
        try:
            verify_self_digest(production_authorization, "authorization_digest")
        except PromotionDenied as exc:
            reasons.append(str(exc))
        if production_authorization.get("authorized_environment") != PRODUCTION:
            reasons.append("AUTHORIZATION_WRONG_ENVIRONMENT")
        if production_authorization.get("promotion_id") != release_candidate_manifest.get("promotion_id"):
            reasons.append("AUTHORIZATION_PROMOTION_MISMATCH")
        if production_authorization.get("source_commit_sha") != source_commit_sha:
            reasons.append("AUTHORIZATION_SHA_MISMATCH")
        if production_authorization.get("artifact_digest") != artifact_digest:
            reasons.append("AUTHORIZATION_ARTIFACT_MISMATCH")
        if production_authorization.get("release_candidate_manifest_digest") != release_candidate_manifest.get("manifest_digest"):
            reasons.append("AUTHORIZATION_RC_MANIFEST_MISMATCH")
        try:
            if _expired(production_authorization.get("expires_at"), now_iso):
                reasons.append("AUTHORIZATION_EXPIRED")
        except Exception:
            reasons.append("AUTHORIZATION_EXPIRY_MALFORMED")

    decision = {
        "schema_version": 1,
        "source_commit_sha": source_commit_sha,
        "artifact_digest": artifact_digest,
        "requested_environment": requested_environment,
        "effective_environment": PRODUCTION if not reasons else RELEASE_CANDIDATE,
        "eligible_for_production": not reasons,
        "denial_reasons": sorted(set(reasons)),
        "model_claim": model_claim,
        "model_claim_has_authority": False,
        "release_candidate_manifest_digest": release_candidate_manifest.get("manifest_digest"),
        "production_authorization_digest": None if production_authorization is None else production_authorization.get("authorization_digest"),
    }
    decision["decision_digest"] = canonical_digest(decision)
    return decision


def evaluate_rollback(*, target_artifact_digest: str, prior_production_authorizations: list[Dict[str, Any]]) -> Dict[str, Any]:
    authorized = False
    matched_auth = None
    for auth in prior_production_authorizations:
        try:
            verify_self_digest(auth, "authorization_digest")
        except PromotionDenied:
            continue
        if auth.get("authorized_environment") == PRODUCTION and auth.get("artifact_digest") == target_artifact_digest:
            authorized = True
            matched_auth = auth["authorization_digest"]
            break
    result = {
        "target_artifact_digest": target_artifact_digest,
        "rollback_eligible": authorized,
        "matched_production_authorization_digest": matched_auth,
    }
    result["decision_digest"] = canonical_digest(result)
    return result
