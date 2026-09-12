"""V24-I10 reviewer-safe proof projection and audit-record construction."""
from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Any,Mapping
AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
FORBIDDEN_CLEAN_REVIEW_KEYS={"prior_reviewer_findings","prior_reviewer_disposition","prior_review_conclusion","expected_review_outcome","majority_review_state"}
ALLOWED_COMPLETENESS={"COMPLETE_BY_INDEPENDENT_DERIVATION","CONSERVATIVE_SUPERSET_QUALIFIED","INCOMPLETE","SHARED_SOURCE_CIRCULAR","STALE","INSUFFICIENT_EVIDENCE","NOT_APPLICABLE"}
def dg(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def build_reviewer_safe_proof(b:Mapping[str,Any])->dict[str,Any]:
 p=[]
 if b.get("proof_manifest_state")!="QUALIFIED":p.append("PROOF_VIEW_APPLICABILITY_INCOMPLETE")
 fields=b.get("mandatory_fields") if isinstance(b.get("mandatory_fields"),list) else []
 sources=b.get("source_values") if isinstance(b.get("source_values"),Mapping) else {}
 out={}
 for f in fields:
  if not isinstance(f,Mapping):p.append("PROOF_FIELD_DESCRIPTOR_MALFORMED");continue
  fid=f.get("field_id");src=f.get("source_binding");red=f.get("redaction_class")
  if not isinstance(fid,str) or not fid:p.append("PROOF_FIELD_ID_INVALID");continue
  value=sources.get(src,"NOT_PRESENT")
  if value=="NOT_PRESENT":p.append(f"PROOF_MANDATORY_FIELD_NOT_PRESENT:{fid}")
  if red=="VISIBLE":out[fid]=deepcopy(value)
  elif red=="SECRET_SAFE_IDENTITY_ONLY":
   if isinstance(value,Mapping):out[fid]={k:deepcopy(value[k]) for k in ("identity","version","state","qualification_result") if k in value}
   else:out[fid]="NOT_PRESENT";p.append(f"PROOF_SECRET_SAFE_IDENTITY_UNAVAILABLE:{fid}")
  else:p.append(f"PROOF_REDACTION_CLASS_INVALID:{fid}:{red}")
 review=b.get("clean_review_context") if isinstance(b.get("clean_review_context"),Mapping) else {}
 leaked=sorted(FORBIDDEN_CLEAN_REVIEW_KEYS & set(review))
 for key in leaked:p.append(f"CLEAN_REVIEW_CONTAMINATION:{key}")
 completeness=b.get("completeness_subject_results") if isinstance(b.get("completeness_subject_results"),list) else []
 subject_out=[]
 for r in completeness:
  if not isinstance(r,Mapping):p.append("COMPLETENESS_REVIEW_RESULT_MALFORMED");continue
  state=r.get("classification")
  if state not in ALLOWED_COMPLETENESS:p.append(f"COMPLETENESS_REVIEW_CLASS_INVALID:{r.get('subject_id')}:{state}")
  subject_out.append({"subject_id":r.get("subject_id"),"classification":state,"evidence_refs":deepcopy(r.get("evidence_refs",[]))})
 blocking={"INCOMPLETE","SHARED_SOURCE_CIRCULAR","STALE","INSUFFICIENT_EVIDENCE"}
 if any(x.get("classification") in blocking and x.get("load_bearing",True) for x in completeness if isinstance(x,Mapping)):p.append("LOAD_BEARING_COMPLETENESS_REVIEW_BLOCKING")
 p=sorted(set(p))
 proof={"mandatory_fields":out,"completeness_subject_results":subject_out,"review_context_digest":dg({k:v for k,v in review.items() if k not in FORBIDDEN_CLEAN_REVIEW_KEYS}),"review_authority_effect":AUTHORITY_EFFECT}
 return {"state":"REVIEWER_SAFE_PROOF_READY" if not p else "REVIEWER_SAFE_PROOF_INCOMPLETE","qualified":False,"problems":p,"proof":proof,"proof_digest":dg(proof),"authority_effect":AUTHORITY_EFFECT}

def build_audit_record(b:Mapping[str,Any])->dict[str,Any]:
 p=[]
 required=("candidate_commit","governance_generation_id","decision_digest","application_record_digest","admission_ledger_digest","completeness_ledger_digest","normative_catalog_digest","endpoint_precedence_digest","proof_view_digest")
 for k in required:
  if not b.get(k):p.append(f"AUDIT_BINDING_REQUIRED:{k}")
 if b.get("authority_effect") not in {None,AUTHORITY_EFFECT}:p.append("AUDIT_RECORD_CANNOT_GRANT_AUTHORITY")
 record={k:deepcopy(b.get(k)) for k in required};record["historical_failures_preserved"]=bool(b.get("historical_failures_preserved",False));record["authority_effect"]=AUTHORITY_EFFECT
 if not record["historical_failures_preserved"]:p.append("AUDIT_HISTORICAL_FAILURE_PRESERVATION_REQUIRED")
 p=sorted(set(p));record["audit_record_digest"]=dg(record)
 return {"state":"AUDIT_RECORD_READY" if not p else "AUDIT_RECORD_INCOMPLETE","qualified":False,"problems":p,"record":record,"authority_effect":AUTHORITY_EFFECT}
