"""V24-I10 reviewer-safe proof projection and audit-record construction."""
from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Any,Mapping
AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
FORBIDDEN_CLEAN_REVIEW_KEYS={"prior_reviewer_findings","prior_reviewer_disposition","prior_review_conclusion","expected_review_outcome","majority_review_state"}
ALLOWED_COMPLETENESS={"COMPLETE_BY_INDEPENDENT_DERIVATION","CONSERVATIVE_SUPERSET_QUALIFIED","INCOMPLETE","SHARED_SOURCE_CIRCULAR","STALE","INSUFFICIENT_EVIDENCE","NOT_APPLICABLE"}
def dg(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _subject_catalog(b:Mapping[str,Any],p:list[str])->dict[str,bool]:
 catalog=b.get("completeness_subject_catalog")
 if not isinstance(catalog,list) or not catalog:
  p.append("COMPLETENESS_SUBJECT_CATALOG_REQUIRED");return {}
 if b.get("completeness_subject_catalog_digest")!=dg(catalog):p.append("COMPLETENESS_SUBJECT_CATALOG_DIGEST_INVALID")
 out={}
 for row in catalog:
  if not isinstance(row,Mapping):p.append("COMPLETENESS_SUBJECT_CATALOG_ROW_MALFORMED");continue
  sid=row.get("subject_id")
  if not isinstance(sid,str) or not sid:p.append("COMPLETENESS_SUBJECT_CATALOG_ID_INVALID");continue
  if sid in out:p.append(f"COMPLETENESS_SUBJECT_CATALOG_DUPLICATE:{sid}")
  if not isinstance(row.get("load_bearing"),bool):p.append(f"COMPLETENESS_SUBJECT_CATALOG_LOAD_BEARING_REQUIRED:{sid}")
  if row.get("source_kind")!="AUTHORITATIVE_SUBJECT_CATALOG":p.append(f"COMPLETENESS_SUBJECT_CATALOG_SOURCE_INVALID:{sid}")
  if not row.get("evidence_digest"):p.append(f"COMPLETENESS_SUBJECT_CATALOG_EVIDENCE_REQUIRED:{sid}")
  if row.get("candidate_self_derived") is not False:p.append(f"COMPLETENESS_SUBJECT_CATALOG_SELF_DERIVED_FORBIDDEN:{sid}")
  out[sid]=row.get("load_bearing") is True
 return out

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
 for key in sorted(FORBIDDEN_CLEAN_REVIEW_KEYS & set(review)):p.append(f"CLEAN_REVIEW_CONTAMINATION:{key}")
 catalog=_subject_catalog(b,p)
 completeness=b.get("completeness_subject_results") if isinstance(b.get("completeness_subject_results"),list) else []
 subject_out=[];seen=set()
 for r in completeness:
  if not isinstance(r,Mapping):p.append("COMPLETENESS_REVIEW_RESULT_MALFORMED");continue
  sid=r.get("subject_id");state=r.get("classification")
  if sid not in catalog:p.append(f"COMPLETENESS_REVIEW_SUBJECT_UNDERIVED:{sid}")
  if sid in seen:p.append(f"COMPLETENESS_REVIEW_SUBJECT_DUPLICATE:{sid}")
  seen.add(sid)
  if state not in ALLOWED_COMPLETENESS:p.append(f"COMPLETENESS_REVIEW_CLASS_INVALID:{sid}:{state}")
  subject_out.append({"subject_id":sid,"classification":state,"evidence_refs":deepcopy(r.get("evidence_refs",[])),"load_bearing":catalog.get(sid,False)})
 for sid in sorted(set(catalog)-seen):p.append(f"COMPLETENESS_REVIEW_SUBJECT_MISSING:{sid}")
 blocking={"INCOMPLETE","SHARED_SOURCE_CIRCULAR","STALE","INSUFFICIENT_EVIDENCE"}
 if any(r.get("classification") in blocking and catalog.get(r.get("subject_id"),False) for r in completeness if isinstance(r,Mapping)):p.append("LOAD_BEARING_COMPLETENESS_REVIEW_BLOCKING")
 p=sorted(set(p))
 proof={"mandatory_fields":out,"completeness_subject_results":subject_out,"review_context_digest":dg({k:v for k,v in review.items() if k not in FORBIDDEN_CLEAN_REVIEW_KEYS}),"review_authority_effect":AUTHORITY_EFFECT}
 return {"state":"REVIEWER_SAFE_PROOF_READY" if not p else "REVIEWER_SAFE_PROOF_INCOMPLETE","qualified":False,"problems":p,"proof":proof,"proof_digest":dg(proof),"authority_effect":AUTHORITY_EFFECT}

def build_audit_record(b:Mapping[str,Any])->dict[str,Any]:
 p=[]
 required=("candidate_commit","governance_generation_id","decision_digest","application_record_digest","admission_ledger_digest","completeness_ledger_digest","normative_catalog_digest","endpoint_precedence_digest","proof_view_digest")
 for k in required:
  if not b.get(k):p.append(f"AUDIT_BINDING_REQUIRED:{k}")
 if b.get("authority_effect") not in {None,AUTHORITY_EFFECT}:p.append("AUDIT_RECORD_CANNOT_GRANT_AUTHORITY")
 failures=b.get("historical_failure_records")
 if not isinstance(failures,list) or not failures:
  failures=[];p.append("AUDIT_HISTORICAL_FAILURE_RECORDS_REQUIRED")
 else:
  if b.get("historical_failure_set_digest")!=dg(failures):p.append("AUDIT_HISTORICAL_FAILURE_SET_DIGEST_INVALID")
  seen=set()
  for row in failures:
   if not isinstance(row,Mapping):p.append("AUDIT_HISTORICAL_FAILURE_RECORD_MALFORMED");continue
   fid=row.get("failure_id")
   if not isinstance(fid,str) or not fid:p.append("AUDIT_HISTORICAL_FAILURE_ID_INVALID");continue
   if fid in seen:p.append(f"AUDIT_HISTORICAL_FAILURE_DUPLICATE:{fid}")
   seen.add(fid)
   if row.get("state")!="PRESERVED":p.append(f"AUDIT_HISTORICAL_FAILURE_NOT_PRESERVED:{fid}")
   if not row.get("record_digest") or not row.get("evidence_ref"):p.append(f"AUDIT_HISTORICAL_FAILURE_BINDING_INCOMPLETE:{fid}")
 record={k:deepcopy(b.get(k)) for k in required};record["historical_failure_records"]=deepcopy(failures);record["historical_failure_set_digest"]=b.get("historical_failure_set_digest");record["historical_failures_preserved"]=bool(failures) and not any(x.startswith("AUDIT_HISTORICAL_FAILURE_") for x in p);record["authority_effect"]=AUTHORITY_EFFECT
 p=sorted(set(p));record["audit_record_digest"]=dg(record)
 return {"state":"AUDIT_RECORD_READY" if not p else "AUDIT_RECORD_INCOMPLETE","qualified":False,"problems":p,"record":record,"authority_effect":AUTHORITY_EFFECT}
