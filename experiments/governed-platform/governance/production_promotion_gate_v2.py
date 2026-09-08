from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import production_promotion_gate as v1

TESTING = v1.TESTING
RELEASE_CANDIDATE = v1.RELEASE_CANDIDATE
PRODUCTION = v1.PRODUCTION
PromotionDenied = v1.PromotionDenied
canonical_digest = v1.canonical_digest
make_bound_evidence = v1.make_bound_evidence
verify_bound_evidence = v1.verify_bound_evidence
build_release_candidate_manifest = v1.build_release_candidate_manifest
verify_self_digest = v1.verify_self_digest


def _canon_bytes(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


@dataclass(frozen=True)
class PromotionAuthorityRegistry:
    """Deterministic reference trust boundary.

    The HMAC key represents platform-owned authority unavailable to untrusted
    caller/model input. This is not a production KMS/HSM claim.
    """

    authority_namespace: str
    _key: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.authority_namespace, str) or not self.authority_namespace.strip():
            raise ValueError("authority_namespace required")
        if not isinstance(self._key, (bytes, bytearray)) or len(self._key) < 16:
            raise ValueError("authority key must be at least 16 bytes")

    def _sign(self, body: Dict[str, Any]) -> str:
        return "hmac-sha256:" + hmac.new(bytes(self._key), _canon_bytes(body), hashlib.sha256).hexdigest()

    def _issue(self, record_type: str, body: Dict[str, Any]) -> Dict[str, Any]:
        record = {"record_type": record_type, "authority_namespace": self.authority_namespace, **body}
        record["authority_signature"] = self._sign(record)
        return record

    def verify(self, record: Dict[str, Any], expected_type: str) -> bool:
        if not isinstance(record, dict) or record.get("record_type") != expected_type:
            return False
        if record.get("authority_namespace") != self.authority_namespace:
            return False
        supplied = record.get("authority_signature")
        if not isinstance(supplied, str):
            return False
        body = {k: v for k, v in record.items() if k != "authority_signature"}
        return hmac.compare_digest(supplied, self._sign(body))

    def issue_head_attestation(self, *, source_commit_sha: str, observed_at: str) -> Dict[str, Any]:
        if not isinstance(source_commit_sha, str) or len(source_commit_sha) != 40:
            raise PromotionDenied("HEAD_ATTESTATION_SHA_INVALID")
        return self._issue("HEAD_ATTESTATION", {
            "source_commit_sha": source_commit_sha,
            "observed_at": observed_at,
        })

    def issue_credential_attestation(self, *, credential_id: str, domain: str, environment: str) -> Dict[str, Any]:
        if domain not in {"testing", "production"}:
            raise PromotionDenied("CREDENTIAL_DOMAIN_INVALID")
        if environment not in {TESTING, RELEASE_CANDIDATE, PRODUCTION}:
            raise PromotionDenied("CREDENTIAL_ENVIRONMENT_INVALID")
        if not isinstance(credential_id, str) or not credential_id.strip():
            raise PromotionDenied("CREDENTIAL_ID_REQUIRED")
        return self._issue("CREDENTIAL_ATTESTATION", {
            "credential_id": credential_id,
            "domain": domain,
            "environment": environment,
        })

    def issue_production_authorization(
        self,
        *,
        authorization_id: str,
        release_candidate_manifest: Dict[str, Any],
        authorization_evidence: Dict[str, Any],
        expires_at: Optional[str],
    ) -> Dict[str, Any]:
        verify_self_digest(release_candidate_manifest, "manifest_digest")
        if release_candidate_manifest.get("to_environment") != RELEASE_CANDIDATE:
            raise PromotionDenied("AUTHORIZATION_REQUIRES_RELEASE_CANDIDATE")
        sha = release_candidate_manifest["source_commit_sha"]
        artifact = release_candidate_manifest["artifact_digest"]
        verify_bound_evidence(
            authorization_evidence,
            kind="PRODUCTION_AUTHORIZATION",
            source_commit_sha=sha,
            artifact_digest=artifact,
        )
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            raise PromotionDenied("AUTHORIZATION_ID_REQUIRED")
        return self._issue("PRODUCTION_AUTHORIZATION", {
            "authorization_id": authorization_id,
            "promotion_id": release_candidate_manifest["promotion_id"],
            "source_commit_sha": sha,
            "artifact_digest": artifact,
            "release_candidate_manifest_digest": release_candidate_manifest["manifest_digest"],
            "authorized_environment": PRODUCTION,
            "authorization_evidence_digest": authorization_evidence["evidence_digest"],
            "expires_at": expires_at,
        })

    def issue_production_receipt(
        self,
        *,
        decision: Dict[str, Any],
        deployed_at: str,
    ) -> Dict[str, Any]:
        if decision.get("eligible_for_production") is not True or decision.get("effective_environment") != PRODUCTION:
            raise PromotionDenied("PRODUCTION_RECEIPT_REQUIRES_ELIGIBLE_DECISION")
        for field in ("source_commit_sha", "artifact_digest", "decision_digest"):
            if not isinstance(decision.get(field), str) or not decision[field].strip():
                raise PromotionDenied("PRODUCTION_RECEIPT_DECISION_INCOMPLETE")
        return self._issue("PRODUCTION_RECEIPT", {
            "source_commit_sha": decision["source_commit_sha"],
            "artifact_digest": decision["artifact_digest"],
            "decision_digest": decision["decision_digest"],
            "deployed_at": deployed_at,
        })


def evaluate_production_promotion(
    *,
    registry: PromotionAuthorityRegistry,
    release_candidate_manifest: Dict[str, Any],
    production_authorization: Optional[Dict[str, Any]],
    head_attestation: Optional[Dict[str, Any]],
    credential_attestation: Optional[Dict[str, Any]],
    source_commit_sha: str,
    artifact_digest: str,
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

    if head_attestation is None or not registry.verify(head_attestation, "HEAD_ATTESTATION"):
        reasons.append("INVALID_OR_MISSING_HEAD_ATTESTATION")
    elif head_attestation.get("source_commit_sha") != source_commit_sha:
        reasons.append("HEAD_DRIFT")

    if credential_attestation is None or not registry.verify(credential_attestation, "CREDENTIAL_ATTESTATION"):
        reasons.append("INVALID_OR_MISSING_CREDENTIAL_ATTESTATION")
    else:
        if credential_attestation.get("domain") != "production":
            reasons.append("NON_PRODUCTION_CREDENTIAL_DOMAIN")
        if credential_attestation.get("environment") != PRODUCTION:
            reasons.append("CREDENTIAL_WRONG_ENVIRONMENT")

    if production_authorization is None or not registry.verify(production_authorization, "PRODUCTION_AUTHORIZATION"):
        reasons.append("INVALID_OR_MISSING_PRODUCTION_AUTHORIZATION")
    else:
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
        "schema_version": 2,
        "source_commit_sha": source_commit_sha,
        "artifact_digest": artifact_digest,
        "requested_environment": requested_environment,
        "effective_environment": PRODUCTION if not reasons else RELEASE_CANDIDATE,
        "eligible_for_production": not reasons,
        "denial_reasons": sorted(set(reasons)),
        "model_claim": model_claim,
        "model_claim_has_authority": False,
        "authority_namespace": registry.authority_namespace,
        "release_candidate_manifest_digest": release_candidate_manifest.get("manifest_digest"),
        "production_authorization_signature": None if production_authorization is None else production_authorization.get("authority_signature"),
        "head_attestation_signature": None if head_attestation is None else head_attestation.get("authority_signature"),
        "credential_attestation_signature": None if credential_attestation is None else credential_attestation.get("authority_signature"),
    }
    decision["decision_digest"] = canonical_digest(decision)
    return decision


def evaluate_rollback(
    *,
    registry: PromotionAuthorityRegistry,
    target_artifact_digest: str,
    prior_production_receipts: list[Dict[str, Any]],
) -> Dict[str, Any]:
    matched = None
    for receipt in prior_production_receipts:
        if registry.verify(receipt, "PRODUCTION_RECEIPT") and receipt.get("artifact_digest") == target_artifact_digest:
            matched = receipt.get("authority_signature")
            break
    result = {
        "schema_version": 2,
        "target_artifact_digest": target_artifact_digest,
        "rollback_eligible": matched is not None,
        "matched_production_receipt_signature": matched,
        "authority_namespace": registry.authority_namespace,
    }
    result["decision_digest"] = canonical_digest(result)
    return result
