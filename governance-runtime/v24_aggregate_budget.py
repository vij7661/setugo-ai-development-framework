"""V24-I7 aggregation-dimension, persistence, atomic transaction and reconciliation construction."""
from __future__ import annotations
import hashlib,json
from typing import Any,Mapping
AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
def dg(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def validate_aggregate_bundle(b:Mapping[str,Any])->dict[str,Any]:
 p=[]; gen=b.get("governance_generation_id")
 mandatory=set(b.get("independently_derived_mandatory_dimensions",[])) if isinstance(b.get("independently_derived_mandatory_dimensions"),list) else set()
 active=set(b.get("active_policy_dimensions",[])) if isinstance(b.get("active_policy_dimensions"),list) else set()
 if not mandatory:p.append("MANDATORY_AGGREGATION_DIMENSIONS_REQUIRED")
 for d in sorted(mandatory-active):p.append(f"AGGREGATION_DIMENSION_MISSING:{d}")
 effects=b.get("authority_effects") if isinstance(b.get("authority_effects"),list) else []
 for e in effects:
  if not isinstance(e,Mapping):p.append("AUTHORITY_EFFECT_MALFORMED");continue
  eid=e.get("effect_id")
  if e.get("generation_id")!=gen:p.append(f"AUTHORITY_EFFECT_GENERATION_MISMATCH:{eid}")
  if e.get("state")=="EXPIRED" and e.get("cessation_proof_state")!="QUALIFIED":p.append(f"AUTHORITY_EFFECT_ARBITRARY_EXPIRY_FORBIDDEN:{eid}")
  if e.get("still_effective") is True and e.get("aggregation_obligation_active") is not True:p.append(f"PERSISTENT_EFFECT_AGGREGATION_REQUIRED:{eid}")
 txs=b.get("transactions") if isinstance(b.get("transactions"),list) else []
 for tx in txs:
  if not isinstance(tx,Mapping):p.append("AGGREGATE_TRANSACTION_MALFORMED");continue
  tid=tx.get("transaction_id"); keys=tx.get("required_keys") if isinstance(tx.get("required_keys"),list) else []
  records=tx.get("key_records") if isinstance(tx.get("key_records"),list) else []
  if not tid or not keys:p.append(f"AGGREGATE_TRANSACTION_ID_OR_KEYS_REQUIRED:{tid}")
  rec_keys=[r.get("key") for r in records if isinstance(r,Mapping)]
  if set(rec_keys)!=set(keys):p.append(f"AGGREGATE_KEY_SET_INCOMPLETE:{tid}")
  if any(r.get("transaction_id")!=tid for r in records if isinstance(r,Mapping)):p.append(f"AGGREGATE_TRANSACTION_ID_MISMATCH:{tid}")
  committed=[r for r in records if isinstance(r,Mapping) and r.get("state")=="COMMITTED"]
  absent=[r for r in records if isinstance(r,Mapping) and r.get("state")=="AUTHORITATIVE_ABSENT"]
  ids={r.get("committed_identity") for r in committed}
  if len(ids)>1: outcome="RECONCILIATION_CONFLICT"
  elif len(committed)==len(keys) and len(ids)==1 and len(keys)>0: outcome="COMMIT_CONFIRMED_EXISTING"
  elif len(absent)==len(keys) and len(keys)>0: outcome="NO_COMMIT_CONFIRMED"
  else: outcome="INSUFFICIENT_EVIDENCE"
  if tx.get("reconciliation_outcome")!=outcome:p.append(f"AGGREGATE_RECONCILIATION_OUTCOME_MISMATCH:{tid}:{outcome}")
  if outcome not in {"COMMIT_CONFIRMED_EXISTING","NO_COMMIT_CONFIRMED"} and tx.get("authority_transition_state")=="SUCCESS":p.append(f"AGGREGATE_UNRESOLVED_CANNOT_SUCCEED:{tid}")
  if tx.get("generation_id")!=gen:p.append(f"AGGREGATE_TRANSACTION_GENERATION_MISMATCH:{tid}")
 p=sorted(set(p));return {"state":"AGGREGATE_BUDGET_CONSTRUCTION_VALID" if not p else "AGGREGATE_BUDGET_INCOMPLETE","qualified":False,"problems":p,"bundle_digest":dg(b),"authority_effect":AUTHORITY_EFFECT}
