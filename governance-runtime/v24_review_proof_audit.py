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
 catalog=b.get("authoritative_subject_catalog") if isinstance(b.get("authoritative_subject_catalog"),list) else []
 if b.get("authoritative_subject_catalog_state")!="QUALIFIED":p.append("AUTHORITATIVE_SUBJECT_CATALOG_NOT_QUALIFIED")
 if not catalog:p.append("AUTHORITATIVE_SUBJECT_CATALOG_REQUIRED")
 supplied_catalog_digest=b.get("authoritative_subject_catalog_digest")
 if supplied_catalog_digest!=dg(catalog):p.append("AUTHORITATIVE_SUBJECT_CATALOG_DIGEST_INVALID")
 by_subject={}
 for row in catalog:
  if not isinstance(row,Mapping):p.append("AUTHORITATIVE_SUBJECT_CATALOG_ROW_MALFORMED");continue
  sid=row.get("subject_id")
  if not isinstance(sid,str) or not sid:p.append("AUTHORITATIVE_SUBJECT_ID_INVALID");continue
  if sid in by_subject:p.append(f"AUTHORITATIVE_SUBJECT_DUPLICATE:{sid}")
  if not isinstance(row.get("load_bearing"),bool):p.append(f"AUTHORITATIVE_SUBJECT_LOAD_BEARING_REQUIRED:{sid}")
  if not row.get("subject_class") or not row.get("classification_evidence_digest"):p.append(f"AUTHORITATIVE_SUBJECT_BINDING_INCOMPLETE:{sid}")
  by_subject[sid]=row

 subject_out=[]; blocking={"INCOMPLETE","SHARED_SOURCE_CIRCULAR","STALE","INSUFFICIENT_EVIDENCE"}
 seen_results=set()
 for r in completeness:
  if not isinstance(r,Mapping):p.append("COMPLETENESS_REVIEW_RESULT_MALFORMED");continue
  sid=r.get("subject_id");state=r.get("classification")
  if not isinstance(sid,str) or not sid:p.append("COMPLETENESS_REVIEW_SUBJECT_ID_INVALID");continue
  if sid in seen_results:p.append(f"COMPLETENESS_REVIEW_SUBJECT_DUPLICATE:{sid}")
  seen_results.add(sid)
  if sid not in by_subject:p.append(f"COMPLETENESS_REVIEW_SUBJECT_UNDERIVED:{sid}")
  if state not in ALLOWED_COMPLETENESS:p.append(f"COMPLETENESS_REVIEW_CLASS_INVALID:{sid}:{state}")
  derived_load_bearing=bool(by_subject.get(sid,{}).get("load_bearing",False))
  if "load_bearing" in r and r.get("load_bearing")!=derived_load_bearing:p.append(f"COMPLETENESS_REVIEW_CALLER_LOAD_BEARING_MISMATCH:{sid}")
  if state in blocking and derived_load_bearing:p.append("LOAD_BEARING_COMPLETENESS_REVIEW_BLOCKING")
  subject_out.append({"subject_id":sid,"classification":state,"evidence_refs":deepcopy(r.get("evidence_refs",[])),"load_bearing":derived_load_bearing})
 for sid,row in by_subject.items():
  if row.get("load_bearing") is True and sid not in seen_results:p.append(f"LOAD_BEARING_COMPLETENESS_REVIEW_RESULT_MISSING:{sid}")

 p=sorted(set(p))
 proof={"mandatory_fields":out,"completeness_subject_results":subject_out,"review_context_digest":dg({k:v for k,v in review.items() if k not in FORBIDDEN_CLEAN_REVIEW_KEYS}),"review_authority_effect":AUTHORITY_EFFECT}
 return {"state":"REVIEWER_SAFE_PROOF_READY" if not p else "REVIEWER_SAFE_PROOF_INCOMPLETE","qualified":False,"problems":p,"proof":proof,"proof_digest":dg(proof),"authority_effect":AUTHORITY_EFFECT}

def build_audit_record(b:Mapping[str,Any])->dict[str,Any]:
 p=[]
 required=("candidate_commit","governance_generation_id","decision_digest","application_record_digest","admission_ledger_digest","completeness_ledger_digest","normative_catalog_digest","endpoint_precedence_digest","proof_view_digest")
 for k in required:
  if not b.get(k):p.append(f"AUDIT_BINDING_REQUIRED:{k}")
 if b.get("authority_effect") not in {None,AUTHORITY_EFFECT}:p.append("AUDIT_RECORD_CANNOT_GRANT_AUTHORITY")
 failures=b.get("historical_failure_records") if isinstance(b.get("historical_failure_records"),list) else []
 if not failures:p.append("AUDIT_HISTORICAL_FAILURE_RECORDS_REQUIRED")
 for i,row in enumerate(failures):
  if not isinstance(row,Mapping):p.append(f"AUDIT_HISTORICAL_FAILURE_RECORD_MALFORMED:{i}");continue
  if not row.get("failure_id") or not row.get("record_digest"):p.append(f"AUDIT_HISTORICAL_FAILURE_RECORD_BINDING_REQUIRED:{i}")
 if b.get("historical_failure_record_set_digest")!=dg(failures):p.append("AUDIT_HISTORICAL_FAILURE_RECORD_SET_DIGEST_INVALID")
 if b.get("historical_failures_preserved") is not True:p.append("AUDIT_HISTORICAL_FAILURE_PRESERVATION_REQUIRED")
 record={k:deepcopy(b.get(k)) for k in required}
 record["historical_failure_records"]=[deepcopy(x) for x in failures]
 record["historical_failure_record_set_digest"]=dg(failures)
 record["historical_failures_preserved"]=bool(failures) and b.get("historical_failures_preserved") is True
 record["authority_effect"]=AUTHORITY_EFFECT
 p=sorted(set(p));record["audit_record_digest"]=dg(record)
 return {"state":"AUDIT_RECORD_READY" if not p else "AUDIT_RECORD_INCOMPLETE","qualified":False,"problems":p,"record":record,"authority_effect":AUTHORITY_EFFECT}
