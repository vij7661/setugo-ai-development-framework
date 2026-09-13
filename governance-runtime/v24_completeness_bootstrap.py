"""V24-I4 completeness qualification and bootstrap-lineage construction."""
from __future__ import annotations
import hashlib, json
from typing import Any, Mapping
AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
INDEPENDENT_SOURCE_KINDS={"INDEPENDENT_RUNTIME_OBSERVATION","REPOSITORY_EVIDENCE","EXTERNAL_CONTROL_PLANE_EVIDENCE","INDEPENDENT_GOVERNANCE_DERIVATION"}
def _d(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate_completeness_bundle(b:Mapping[str,Any])->dict[str,Any]:
 p=[];gen=b.get("governance_generation_id")
 genesis=b.get("genesis_record")
 if not isinstance(genesis,Mapping):genesis={};p.append("GENESIS_RECORD_REQUIRED")
 bootstrap=genesis.get("bootstrap_completeness_authority_set")
 if not isinstance(bootstrap,Mapping):bootstrap={};p.append("BOOTSTRAP_AUTHORITY_SET_REQUIRED")
 members=bootstrap.get("members")
 if not isinstance(members,list) or not members:members=[];p.append("BOOTSTRAP_AUTHORITY_MEMBER_SET_REQUIRED")
 threshold=bootstrap.get("threshold")
 if not isinstance(threshold,int) or threshold<1 or threshold>len(members):p.append("BOOTSTRAP_THRESHOLD_INVALID")
 ids=set();subject_classes=set()
 for m in members:
  if not isinstance(m,Mapping):p.append("BOOTSTRAP_MEMBER_MALFORMED");continue
  mid=m.get("authority_id");domain=m.get("control_domain_id")
  if not isinstance(mid,str) or not mid:p.append("BOOTSTRAP_MEMBER_ID_INVALID");continue
  if mid in ids:p.append(f"BOOTSTRAP_MEMBER_DUPLICATE:{mid}")
  ids.add(mid)
  if not isinstance(domain,str) or not domain:p.append(f"BOOTSTRAP_MEMBER_DOMAIN_REQUIRED:{mid}")
  powers=m.get("subject_classes")
  if not isinstance(powers,list) or not powers:p.append(f"BOOTSTRAP_MEMBER_SUBJECT_CLASSES_REQUIRED:{mid}")
  else:subject_classes.update(x for x in powers if isinstance(x,str))
  if m.get("ordinary_operational_root_only") is True:p.append(f"BOOTSTRAP_OPERATIONAL_ROOT_RELABEL_FORBIDDEN:{mid}")
 if bootstrap.get("terminal_residual_trust_declared") is not True:p.append("BOOTSTRAP_RESIDUAL_TRUST_DECLARATION_REQUIRED")
 if bootstrap.get("self_qualified_by_descendant_machinery") is True:p.append("BOOTSTRAP_SELF_QUALIFICATION_FORBIDDEN")
 if bootstrap.get("generation_id")!=gen:p.append("BOOTSTRAP_GENERATION_MISMATCH")
 contracts=bootstrap.get("source_contracts")
 if not isinstance(contracts,list) or not contracts:contracts=[];p.append("BOOTSTRAP_SOURCE_CONTRACTS_REQUIRED")
 covered=set()
 for c in contracts:
  if not isinstance(c,Mapping):p.append("BOOTSTRAP_SOURCE_CONTRACT_MALFORMED");continue
  cls=c.get("subject_class");covered.add(cls);sources=c.get("allowed_source_kinds")
  if not isinstance(sources,list) or not sources:p.append(f"BOOTSTRAP_SOURCE_KIND_REQUIRED:{cls}")
  else:
   if "CANDIDATE_SELF" in sources:p.append(f"BOOTSTRAP_CANDIDATE_SELF_SOURCE_FORBIDDEN:{cls}")
   for source in sorted(set(sources)-INDEPENDENT_SOURCE_KINDS):p.append(f"BOOTSTRAP_SOURCE_KIND_UNQUALIFIED:{cls}:{source}")
 for cls in sorted(subject_classes-covered):p.append(f"BOOTSTRAP_SOURCE_CONTRACT_COVERAGE_MISSING:{cls}")
 records=b.get("completeness_records")
 if not isinstance(records,list):records=[];p.append("COMPLETENESS_RECORD_SET_REQUIRED")
 required=b.get("required_subjects")
 if not isinstance(required,list):required=[];p.append("REQUIRED_SUBJECT_SET_REQUIRED")
 elif not required:p.append("REQUIRED_SUBJECT_SET_EMPTY")
 elif any(not isinstance(x,str) or not x for x in required):p.append("REQUIRED_SUBJECT_ID_INVALID")
 elif len(set(required))!=len(required):p.append("REQUIRED_SUBJECT_ID_DUPLICATE")
 universe=b.get("required_subject_universe_evidence")
 if not isinstance(universe,Mapping):universe={};p.append("REQUIRED_SUBJECT_UNIVERSE_EVIDENCE_REQUIRED")
 else:
  uids=universe.get("subject_ids")
  if not isinstance(uids,list) or not uids:p.append("REQUIRED_SUBJECT_UNIVERSE_EMPTY");uids=[]
  if list(uids)!=sorted(uids) or len(set(uids))!=len(uids):p.append("REQUIRED_SUBJECT_UNIVERSE_NOT_CANONICAL")
  if set(uids)!=set(required):p.append("REQUIRED_SUBJECT_UNIVERSE_MISMATCH")
  if universe.get("subject_set_digest")!=_d(sorted(required)):p.append("REQUIRED_SUBJECT_UNIVERSE_DIGEST_INVALID")
  if universe.get("source_kind") not in INDEPENDENT_SOURCE_KINDS:p.append("REQUIRED_SUBJECT_UNIVERSE_SOURCE_UNQUALIFIED")
  if universe.get("candidate_self_derived") is not False:p.append("REQUIRED_SUBJECT_UNIVERSE_SELF_DERIVED_FORBIDDEN")
  if not universe.get("source_evidence_digest") or not universe.get("derivation_authority_id"):p.append("REQUIRED_SUBJECT_UNIVERSE_BINDING_INCOMPLETE")
 by_subject={}
 for r in records:
  if not isinstance(r,Mapping):p.append("COMPLETENESS_RECORD_MALFORMED");continue
  sid=r.get("subject_id");by_subject.setdefault(sid,[]).append(r)
  if r.get("generation_id")!=gen:p.append(f"COMPLETENESS_RECORD_GENERATION_MISMATCH:{sid}")
  if not r.get("authority_universe_digest") or not r.get("independent_derivation_digest") or not r.get("source_evidence_digest"):p.append(f"COMPLETENESS_RECORD_EVIDENCE_INCOMPLETE:{sid}")
  if r.get("state") not in {"CURRENT","STALE","REVOKED","INSUFFICIENT_EVIDENCE"}:p.append(f"COMPLETENESS_RECORD_STATE_INVALID:{sid}")
  if r.get("derivation_authority_id") not in ids and not r.get("ordinary_iuda_lineage_parent_id"):p.append(f"IUDA_LINEAGE_ROOT_UNRESOLVED:{sid}")
  if r.get("derivation_authority_id")==r.get("subject_owner_id"):p.append(f"COMPLETENESS_SELF_QUALIFICATION_FORBIDDEN:{sid}")
 for sid in required:
  current=[r for r in by_subject.get(sid,[]) if r.get("state")=="CURRENT"]
  if len(current)!=1:p.append(f"CURRENT_COMPLETENESS_RECORD_COUNT_INVALID:{sid}:{len(current)}")
 for sid in sorted(set(by_subject)-set(required)):p.append(f"COMPLETENESS_RECORD_UNDERIVED_SUBJECT:{sid}")
 lineage=b.get("ordinary_iuda_lineage")
 if not isinstance(lineage,list):lineage=[];p.append("ORDINARY_IUDA_LINEAGE_SET_REQUIRED")
 parent={x.get("authority_id"):x.get("parent_authority_id") for x in lineage if isinstance(x,Mapping)}
 for aid in parent:
  seen=set();cur=aid
  while cur not in ids:
   if cur in seen or cur is None:p.append(f"IUDA_LINEAGE_NOT_ROOTED_IN_BOOTSTRAP:{aid}");break
   seen.add(cur);cur=parent.get(cur)
 p=sorted(set(p))
 return {"state":"COMPLETENESS_BOOTSTRAP_CONSTRUCTION_VALID" if not p else "COMPLETENESS_BOOTSTRAP_INCOMPLETE","qualified":False,"problems":p,"bundle_digest":_d(b),"authority_effect":AUTHORITY_EFFECT}
