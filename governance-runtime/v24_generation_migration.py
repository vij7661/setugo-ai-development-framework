"""V24-I8 predecessor migration, generation tagging/read fencing, and no-retro-validation construction."""
from __future__ import annotations
import hashlib,json
from typing import Any,Mapping
AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
def dg(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
ALLOWED={"MIGRATE","REVOKE","SUPERSEDE","QUARANTINE","RETAIN_HISTORICAL_NONAUTHORITATIVE"}

def validate_generation_migration(b:Mapping[str,Any])->dict[str,Any]:
 p=[];current=b.get("current_generation_id");prev=b.get("predecessor_generation_id")
 universe=set(b.get("independently_derived_predecessor_object_ids",[])) if isinstance(b.get("independently_derived_predecessor_object_ids"),list) else set()
 inv=b.get("migration_inventory") if isinstance(b.get("migration_inventory"),list) else []
 byid={}
 for r in inv:
  if not isinstance(r,Mapping):p.append("MIGRATION_RECORD_MALFORMED");continue
  oid=r.get("object_id")
  if not isinstance(oid,str) or not oid:p.append("MIGRATION_OBJECT_ID_INVALID");continue
  if oid in byid:p.append(f"MIGRATION_OBJECT_DUPLICATE:{oid}")
  byid[oid]=r
  if r.get("source_generation_id")!=prev:p.append(f"MIGRATION_SOURCE_GENERATION_MISMATCH:{oid}")
  if r.get("disposition") not in ALLOWED:p.append(f"MIGRATION_DISPOSITION_INVALID:{oid}")
  if not r.get("object_digest") or not r.get("disposition_evidence_digest"):p.append(f"MIGRATION_EVIDENCE_INCOMPLETE:{oid}")
 for oid in sorted(universe-set(byid)):p.append(f"MIGRATION_INVENTORY_OBJECT_MISSING:{oid}")
 for oid in sorted(set(byid)-universe):p.append(f"MIGRATION_INVENTORY_UNDERIVED_OBJECT:{oid}")
 objects=b.get("authority_objects") if isinstance(b.get("authority_objects"),list) else []
 for o in objects:
  if not isinstance(o,Mapping):p.append("AUTHORITY_OBJECT_MALFORMED");continue
  oid=o.get("object_id");g=o.get("generation_id")
  if not g:p.append(f"AUTHORITY_OBJECT_GENERATION_TAG_REQUIRED:{oid}")
  if g!=current:
   disp=byid.get(oid)
   if disp is None:p.append(f"PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED:{oid}")
   elif disp.get("disposition") not in {"MIGRATE","SUPERSEDE"}:p.append(f"PREDECESSOR_AUTHORITY_OBJECT_NOT_USABLE:{oid}:{disp.get('disposition')}")
   elif o.get("migration_record_digest")!=dg(disp):p.append(f"PREDECESSOR_AUTHORITY_OBJECT_DISPOSITION_BINDING_INVALID:{oid}")
 caches=b.get("cache_replica_reads") if isinstance(b.get("cache_replica_reads"),list) else []
 for r in caches:
  if not isinstance(r,Mapping):p.append("CACHE_READ_MALFORMED");continue
  rid=r.get("read_id");og=r.get("object_generation_id")
  if r.get("generation_guard_checked") is not True:p.append(f"CACHE_GENERATION_GUARD_REQUIRED:{rid}")
  if og!=current and r.get("qualifying_disposition_checked") is not True:p.append(f"CACHE_PREDECESSOR_DISPOSITION_REQUIRED:{rid}")
  if r.get("accepted") is True and og!=current and r.get("qualifying_disposition_checked") is not True:p.append(f"CACHE_PREDECESSOR_ACCEPT_BYPASS:{rid}")
 transitions=b.get("generation_transition_records") if isinstance(b.get("generation_transition_records"),list) else []
 for t in transitions:
  if not isinstance(t,Mapping):p.append("GENERATION_TRANSITION_MALFORMED");continue
  tid=t.get("transition_id")
  if t.get("from_generation_id")!=prev or t.get("to_generation_id")!=current:p.append(f"GENERATION_TRANSITION_BINDING_INVALID:{tid}")
  if t.get("migration_inventory_digest")!=dg(inv):p.append(f"GENERATION_TRANSITION_INVENTORY_BINDING_INVALID:{tid}")
  if t.get("state") not in {"PREPARED","COMMITTED","ROLLED_BACK","OUTCOME_UNKNOWN","RECONCILED"}:p.append(f"GENERATION_TRANSITION_STATE_INVALID:{tid}")
  if t.get("state")=="OUTCOME_UNKNOWN" and not t.get("reconciliation_id"):p.append(f"GENERATION_TRANSITION_RECONCILIATION_REQUIRED:{tid}")
 history=b.get("historical_decisions") if isinstance(b.get("historical_decisions"),list) else []
 for h in history:
  if not isinstance(h,Mapping):continue
  hid=h.get("decision_id")
  if h.get("original_result")=="INSUFFICIENT_EVIDENCE" and h.get("later_invalidity_proved") is True and h.get("current_recorded_result")!="INSUFFICIENT_EVIDENCE":p.append(f"RETRO_VALIDATION_FORBIDDEN:{hid}")
  if h.get("later_invalidity_proved") is True and not h.get("historical_invalidity_annotation_digest"):p.append(f"HISTORICAL_INVALIDITY_ANNOTATION_REQUIRED:{hid}")
 p=sorted(set(p));return {"state":"GENERATION_MIGRATION_CONSTRUCTION_VALID" if not p else "GENERATION_MIGRATION_INCOMPLETE","qualified":False,"problems":p,"bundle_digest":dg(b),"authority_effect":AUTHORITY_EFFECT}
