"""V24-I6 admission, application-record, and independent-witness construction."""
from __future__ import annotations

import hashlib, json
from typing import Any, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def digest(v: Any) -> str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def validate_i6_bundle(b: Mapping[str,Any]) -> dict[str,Any]:
    p=[]; gen=b.get("governance_generation_id")
    admissions=b.get("admission_records") if isinstance(b.get("admission_records"),list) else []
    decisions=b.get("kernel_decisions") if isinstance(b.get("kernel_decisions"),list) else []
    apps=b.get("application_records") if isinstance(b.get("application_records"),list) else []
    witnesses=b.get("witnesses") if isinstance(b.get("witnesses"),list) else []
    policy=b.get("witness_policy") if isinstance(b.get("witness_policy"),Mapping) else {}
    if not isinstance(b.get("admission_records"),list): p.append("ADMISSION_RECORD_SET_REQUIRED")
    if not isinstance(b.get("kernel_decisions"),list): p.append("KERNEL_DECISION_SET_REQUIRED")
    if not isinstance(b.get("application_records"),list): p.append("APPLICATION_RECORD_SET_REQUIRED")
    by_adm={}; prev=None
    for r in admissions:
        aid=r.get("admission_id") if isinstance(r,Mapping) else None
        if not isinstance(aid,str) or not aid: p.append("ADMISSION_ID_INVALID"); continue
        if aid in by_adm: p.append(f"ADMISSION_ID_DUPLICATE:{aid}")
        by_adm[aid]=r
        for k in ("universe_contract_digest","semantic_class","instance_id","qualification_evidence_digest","policy_digest"):
            if not r.get(k): p.append(f"ADMISSION_FIELD_MISSING:{aid}:{k}")
        if r.get("generation_id")!=gen: p.append(f"ADMISSION_GENERATION_MISMATCH:{aid}")
        if r.get("state") not in {"CURRENT","REVOKED","SUPERSEDED","STALE"}: p.append(f"ADMISSION_STATE_INVALID:{aid}")
        # ordered input is the append-only logical ledger; predecessor link must match previous digest.
        if prev is None:
            if r.get("predecessor_record_digest") not in {None,"GENESIS"}: p.append(f"ADMISSION_GENESIS_PREDECESSOR_INVALID:{aid}")
        elif r.get("predecessor_record_digest")!=prev: p.append(f"ADMISSION_PREDECESSOR_MISMATCH:{aid}")
        prev=digest({k:v for k,v in r.items() if k!="record_digest"})
        if r.get("record_digest")!=prev: p.append(f"ADMISSION_RECORD_DIGEST_INVALID:{aid}")
    by_dec={}
    for d in decisions:
        did=d.get("decision_id") if isinstance(d,Mapping) else None
        if not isinstance(did,str) or not did: p.append("DECISION_ID_INVALID"); continue
        if did in by_dec: p.append(f"DECISION_ID_DUPLICATE:{did}")
        by_dec[did]=d
        if d.get("generation_id")!=gen: p.append(f"DECISION_GENERATION_MISMATCH:{did}")
        ids=d.get("admission_record_ids")
        if not isinstance(ids,list) or not ids: p.append(f"DECISION_ADMISSION_BINDING_REQUIRED:{did}"); ids=[]
        for aid in ids:
            r=by_adm.get(aid)
            if r is None or r.get("state")!="CURRENT": p.append(f"DECISION_ADMISSION_NOT_CURRENT:{did}:{aid}")
        if d.get("self_activates_completeness_machinery") is True: p.append(f"DECISION_SELF_ACTIVATION_FORBIDDEN:{did}")
    by_app={}
    for a in apps:
        appid=a.get("application_id") if isinstance(a,Mapping) else None
        if not isinstance(appid,str) or not appid: p.append("APPLICATION_ID_INVALID"); continue
        if appid in by_app: p.append(f"APPLICATION_ID_DUPLICATE:{appid}")
        by_app[appid]=a
        did=a.get("decision_id"); d=by_dec.get(did)
        if d is None: p.append(f"APPLICATION_DECISION_UNKNOWN:{appid}:{did}"); continue
        for field in ("decision_digest","transition_digest","sink_set_digest","pre_state_digest","post_state_digest","guarded_writer_id","atomic_fencing_result"):
            if not a.get(field): p.append(f"APPLICATION_FIELD_MISSING:{appid}:{field}")
        if a.get("generation_id")!=gen: p.append(f"APPLICATION_GENERATION_MISMATCH:{appid}")
        if a.get("decision_digest")!=d.get("decision_digest"): p.append(f"APPLICATION_DECISION_DIGEST_MISMATCH:{appid}")
        if a.get("transition_digest")!=d.get("transition_digest"): p.append(f"APPLICATION_TRANSITION_MISMATCH:{appid}")
        if a.get("sink_set_digest")!=d.get("sink_set_digest"): p.append(f"APPLICATION_SINK_SET_MISMATCH:{appid}")
        if a.get("admission_ledger_digest")!=b.get("current_admission_ledger_digest"): p.append(f"APPLICATION_STALE_ADMISSION_LEDGER:{appid}")
        if a.get("completeness_ledger_digest")!=b.get("current_completeness_ledger_digest"): p.append(f"APPLICATION_STALE_COMPLETENESS_LEDGER:{appid}")
    for did,d in by_dec.items():
        if d.get("state")=="APPLIED":
            matches=[a for a in apps if a.get("decision_id")==did]
            if len(matches)!=1: p.append(f"APPLIED_DECISION_APPLICATION_RECORD_COUNT_INVALID:{did}:{len(matches)}")
    # independent witness quorum
    root_domains=set(b.get("root_threshold_capable_operational_domains",[])) if isinstance(b.get("root_threshold_capable_operational_domains"),list) else set()
    operator=policy.get("ledger_operator_control_domain_id")
    required=int(policy.get("required_count",0)) if isinstance(policy.get("required_count"),int) else 0
    if required<2: p.append("WITNESS_REQUIRED_COUNT_TOO_LOW")
    current=[]
    for w in witnesses:
        if not isinstance(w,Mapping): p.append("WITNESS_MALFORMED"); continue
        if w.get("state")!="CURRENT": continue
        if w.get("generation_id")!=gen: p.append(f"WITNESS_GENERATION_MISMATCH:{w.get('witness_id')}")
        if not w.get("control_domain_id"): p.append(f"WITNESS_CONTROL_DOMAIN_REQUIRED:{w.get('witness_id')}")
        current.append(w)
    domains={w.get("control_domain_id") for w in current if w.get("control_domain_id")}
    if len(current)<required or len(domains)<required: p.append("WITNESS_QUORUM_INSUFFICIENT")
    independent=[d for d in domains if d!=operator and d not in root_domains]
    if not independent: p.append("WITNESS_INDEPENDENCE_INSUFFICIENT")
    anchor=b.get("ledger_anchor") if isinstance(b.get("ledger_anchor"),Mapping) else {}
    if anchor.get("witnessed_ledger_digest")!=b.get("current_admission_ledger_digest"): p.append("WITNESS_LEDGER_DIGEST_MISMATCH")
    if anchor.get("generation_id")!=gen: p.append("WITNESS_ANCHOR_GENERATION_MISMATCH")
    p=sorted(set(p))
    return {"state":"I6_CONSTRUCTION_VALID" if not p else "I6_CONSTRUCTION_INCOMPLETE","qualified":False,"problems":p,"bundle_digest":digest(b),"authority_effect":AUTHORITY_EFFECT}
