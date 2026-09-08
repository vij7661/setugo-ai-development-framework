from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import production_promotion_gate as v1

TESTING=v1.TESTING; RELEASE_CANDIDATE=v1.RELEASE_CANDIDATE; PRODUCTION=v1.PRODUCTION
PromotionDenied=v1.PromotionDenied
canonical_digest=v1.canonical_digest
make_bound_evidence=v1.make_bound_evidence
verify_bound_evidence=v1.verify_bound_evidence
verify_self_digest=v1.verify_self_digest
build_release_candidate_manifest=v1.build_release_candidate_manifest


def _canon(obj: Dict[str, Any]) -> bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def _dt(s: str) -> datetime:
    d=datetime.fromisoformat(s.replace("Z","+00:00")); return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

class PromotionAuthorityRegistry:
    def __init__(self, namespace: str, key: bytes, *, epoch: int, current_time: str, current_head_sha: str):
        if not namespace or len(key)<16 or epoch<1 or len(current_head_sha)!=40: raise ValueError("invalid authority registry")
        self.namespace=namespace; self.__key=bytes(key); self.epoch=epoch
        self.current_time=current_time; self.current_head_sha=current_head_sha
        self._revoked_credentials:set[str]=set()
    def _sig(self, body): return "hmac-sha256:"+hmac.new(self.__key,_canon(body),hashlib.sha256).hexdigest()
    def _issue(self, typ, body, *, bind_epoch=True):
        r={"record_type":typ,"authority_namespace":self.namespace,**body}
        if bind_epoch: r["authority_epoch"]=self.epoch
        r["authority_signature"]=self._sig(r); return r
    def verify_signature(self, r, typ):
        if not isinstance(r,dict) or r.get("record_type")!=typ or r.get("authority_namespace")!=self.namespace: return False
        sig=r.get("authority_signature"); body={k:v for k,v in r.items() if k!="authority_signature"}
        return isinstance(sig,str) and hmac.compare_digest(sig,self._sig(body))
    def verify_current(self,r,typ): return self.verify_signature(r,typ) and r.get("authority_epoch")==self.epoch
    def advance_state(self, *, new_epoch:int, current_time:str, current_head_sha:str):
        if new_epoch<=self.epoch: raise PromotionDenied("AUTHORITY_EPOCH_NOT_MONOTONIC")
        if len(current_head_sha)!=40: raise PromotionDenied("HEAD_SHA_INVALID")
        if _dt(current_time)<_dt(self.current_time): raise PromotionDenied("AUTHORITY_TIME_ROLLBACK")
        self.epoch=new_epoch; self.current_time=current_time; self.current_head_sha=current_head_sha
    def revoke_credential(self, credential_id:str): self._revoked_credentials.add(credential_id)
    def issue_head_attestation(self):
        return self._issue("HEAD_ATTESTATION",{"source_commit_sha":self.current_head_sha,"observed_at":self.current_time})
    def issue_credential_attestation(self, *, credential_id:str, domain:str, environment:str, expires_at:Optional[str]):
        if domain not in {"testing","production"}: raise PromotionDenied("CREDENTIAL_DOMAIN_INVALID")
        if environment not in {TESTING,RELEASE_CANDIDATE,PRODUCTION}: raise PromotionDenied("CREDENTIAL_ENVIRONMENT_INVALID")
        return self._issue("CREDENTIAL_ATTESTATION",{"credential_id":credential_id,"domain":domain,"environment":environment,"expires_at":expires_at})
    def issue_production_authorization(self, *, authorization_id:str, release_candidate_manifest:Dict[str,Any], authorization_evidence:Dict[str,Any], expires_at:Optional[str]):
        verify_self_digest(release_candidate_manifest,"manifest_digest")
        sha=release_candidate_manifest["source_commit_sha"]; art=release_candidate_manifest["artifact_digest"]
        verify_bound_evidence(authorization_evidence,kind="PRODUCTION_AUTHORIZATION",source_commit_sha=sha,artifact_digest=art)
        return self._issue("PRODUCTION_AUTHORIZATION",{
            "authorization_id":authorization_id,"promotion_id":release_candidate_manifest["promotion_id"],
            "source_commit_sha":sha,"artifact_digest":art,"release_candidate_manifest_digest":release_candidate_manifest["manifest_digest"],
            "authorized_environment":PRODUCTION,"authorization_evidence_digest":authorization_evidence["evidence_digest"],"expires_at":expires_at})
    def credential_current(self,r):
        if not self.verify_current(r,"CREDENTIAL_ATTESTATION"): return False,"INVALID_OR_STALE_CREDENTIAL_ATTESTATION"
        if r.get("credential_id") in self._revoked_credentials: return False,"CREDENTIAL_REVOKED"
        exp=r.get("expires_at")
        if exp is not None and _dt(self.current_time)>=_dt(exp): return False,"CREDENTIAL_EXPIRED"
        return True,None
    def issue_production_receipt(self, *, decision:Dict[str,Any], deployed_at:str):
        if not decision.get("eligible_for_production") or decision.get("effective_environment")!=PRODUCTION: raise PromotionDenied("PRODUCTION_RECEIPT_REQUIRES_ELIGIBLE_DECISION")
        return self._issue("PRODUCTION_RECEIPT",{"source_commit_sha":decision["source_commit_sha"],"artifact_digest":decision["artifact_digest"],"decision_digest":decision["decision_digest"],"deployed_at":deployed_at},bind_epoch=False)


def evaluate_production_promotion(*, registry:PromotionAuthorityRegistry, release_candidate_manifest:Dict[str,Any], production_authorization:Optional[Dict[str,Any]], head_attestation:Optional[Dict[str,Any]], credential_attestation:Optional[Dict[str,Any]], requested_environment:str=PRODUCTION, model_claim:Optional[str]=None)->Dict[str,Any]:
    reasons=[]
    try: verify_self_digest(release_candidate_manifest,"manifest_digest")
    except PromotionDenied as e: reasons.append(str(e))
    sha=release_candidate_manifest.get("source_commit_sha"); art=release_candidate_manifest.get("artifact_digest")
    if requested_environment!=PRODUCTION: reasons.append("REQUESTED_ENVIRONMENT_NOT_PRODUCTION")
    if release_candidate_manifest.get("from_environment")!=TESTING or release_candidate_manifest.get("to_environment")!=RELEASE_CANDIDATE: reasons.append("INVALID_ORDERED_TRANSITION")
    if head_attestation is None or not registry.verify_current(head_attestation,"HEAD_ATTESTATION"): reasons.append("INVALID_OR_STALE_HEAD_ATTESTATION")
    elif head_attestation.get("source_commit_sha")!=registry.current_head_sha or sha!=registry.current_head_sha: reasons.append("HEAD_DRIFT")
    ok,err=registry.credential_current(credential_attestation) if credential_attestation is not None else (False,"INVALID_OR_STALE_CREDENTIAL_ATTESTATION")
    if not ok: reasons.append(err)
    else:
        if credential_attestation.get("domain")!="production": reasons.append("NON_PRODUCTION_CREDENTIAL_DOMAIN")
        if credential_attestation.get("environment")!=PRODUCTION: reasons.append("CREDENTIAL_WRONG_ENVIRONMENT")
    if production_authorization is None or not registry.verify_current(production_authorization,"PRODUCTION_AUTHORIZATION"): reasons.append("INVALID_OR_STALE_PRODUCTION_AUTHORIZATION")
    else:
        if production_authorization.get("source_commit_sha")!=sha: reasons.append("AUTHORIZATION_SHA_MISMATCH")
        if production_authorization.get("artifact_digest")!=art: reasons.append("AUTHORIZATION_ARTIFACT_MISMATCH")
        if production_authorization.get("release_candidate_manifest_digest")!=release_candidate_manifest.get("manifest_digest"): reasons.append("AUTHORIZATION_RC_MANIFEST_MISMATCH")
        exp=production_authorization.get("expires_at")
        try:
            if exp is not None and _dt(registry.current_time)>=_dt(exp): reasons.append("AUTHORIZATION_EXPIRED")
        except Exception: reasons.append("AUTHORIZATION_EXPIRY_MALFORMED")
    d={"schema_version":3,"source_commit_sha":sha,"artifact_digest":art,"requested_environment":requested_environment,
       "effective_environment":PRODUCTION if not reasons else RELEASE_CANDIDATE,"eligible_for_production":not reasons,
       "denial_reasons":sorted(set(reasons)),"model_claim":model_claim,"model_claim_has_authority":False,
       "authority_namespace":registry.namespace,"authority_epoch":registry.epoch,"authority_time":registry.current_time,"authority_head_sha":registry.current_head_sha,
       "release_candidate_manifest_digest":release_candidate_manifest.get("manifest_digest")}
    d["decision_digest"]=canonical_digest(d); return d

def evaluate_rollback(*,registry:PromotionAuthorityRegistry,target_artifact_digest:str,prior_production_receipts:list[Dict[str,Any]]):
    match=None
    for r in prior_production_receipts:
        if registry.verify_signature(r,"PRODUCTION_RECEIPT") and r.get("artifact_digest")==target_artifact_digest: match=r.get("authority_signature"); break
    d={"schema_version":3,"target_artifact_digest":target_artifact_digest,"rollback_eligible":match is not None,"matched_production_receipt_signature":match,"authority_namespace":registry.namespace}
    d["decision_digest"]=canonical_digest(d); return d
