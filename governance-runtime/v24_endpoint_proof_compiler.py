"""V24-I5 deterministic endpoint-precedence and proof-view applicability compilers."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def compile_endpoint_precedence(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    if bundle.get("normative_catalog_qualification_state") != "QUALIFIED":
        problems.append("NORMATIVE_CONTROL_CATALOG_INCOMPLETE")
    predicates = bundle.get("predicate_descriptors")
    if not isinstance(predicates, list) or not predicates:
        predicates = []
        problems.append("PREDICATE_DESCRIPTOR_SET_REQUIRED")
    by_id: dict[str, Mapping[str, Any]] = {}
    order_keys: dict[tuple[int, int], str] = {}
    rows: list[dict[str, Any]] = []
    for row in predicates:
        if not isinstance(row, Mapping):
            problems.append("PREDICATE_DESCRIPTOR_MALFORMED"); continue
        pid=row.get("predicate_id"); phase=row.get("phase"); rank=row.get("within_phase_rank"); severity=row.get("severity_rank"); endpoint=row.get("endpoint")
        if not isinstance(pid,str) or not pid: problems.append("PREDICATE_ID_INVALID"); continue
        if pid in by_id: problems.append(f"PREDICATE_PRIMARY_MAPPING_DUPLICATE:{pid}"); continue
        by_id[pid]=row
        if not isinstance(phase,int) or phase<1: problems.append(f"PREDICATE_PHASE_INVALID:{pid}"); continue
        if not isinstance(rank,int) or rank<1: problems.append(f"PREDICATE_WITHIN_PHASE_RANK_INVALID:{pid}"); continue
        if not isinstance(severity,int) or severity<1: problems.append(f"PREDICATE_SEVERITY_RANK_INVALID:{pid}")
        if not isinstance(endpoint,str) or not endpoint: problems.append(f"PREDICATE_ENDPOINT_MISSING:{pid}")
        key=(phase,rank)
        if key in order_keys: problems.append(f"PREDICATE_ORDER_COLLISION:{phase}:{rank}:{order_keys[key]}:{pid}")
        order_keys[key]=pid
        rows.append({"predicate_id":pid,"phase":phase,"within_phase_rank":rank,"severity_rank":severity,"endpoint":endpoint,"control_id":row.get("control_id")})
    # total contiguous rank per phase; no "most specific" gaps/ties.
    phases=sorted({r["phase"] for r in rows})
    if phases and phases != list(range(min(phases), max(phases)+1)):
        problems.append("CROSS_PHASE_ORDER_NOT_CONTIGUOUS")
    for phase in phases:
        ranks=sorted(r["within_phase_rank"] for r in rows if r["phase"]==phase)
        if ranks != list(range(1,len(ranks)+1)):
            problems.append(f"WITHIN_PHASE_ORDER_NOT_TOTAL:{phase}")
    # explicit subsystem overrides must be equal/stricter and target known generic predicate.
    for r in predicates:
        if not isinstance(r,Mapping) or not r.get("overrides_predicate_id"): continue
        pid=r.get("predicate_id"); target=by_id.get(r.get("overrides_predicate_id"))
        if target is None: problems.append(f"OVERRIDE_TARGET_UNKNOWN:{pid}:{r.get('overrides_predicate_id')}"); continue
        if r.get("severity_rank",10**9) > target.get("severity_rank",-1): problems.append(f"OVERRIDE_WEAKER_THAN_GENERIC:{pid}:{r.get('overrides_predicate_id')}")
    expected=set(bundle.get("active_predicate_ids",[])) if isinstance(bundle.get("active_predicate_ids"),list) else set()
    actual=set(by_id)
    for pid in sorted(expected-actual): problems.append(f"ACTIVE_PREDICATE_UNMAPPED:{pid}")
    for pid in sorted(actual-expected): problems.append(f"PREDICATE_NOT_IN_ACTIVE_UNIVERSE:{pid}")
    problems=sorted(set(problems))
    compiled=sorted(rows,key=lambda r:(r["phase"],r["within_phase_rank"],r["predicate_id"]))
    return {"state":"ENDPOINT_PRECEDENCE_COMPILED" if not problems else "ENDPOINT_PRECEDENCE_TABLE_INCOMPLETE","qualified":False,"problems":problems,"compiled_rows":compiled,"compiled_table_digest":digest(compiled),"authority_effect":AUTHORITY_EFFECT}


def compile_proof_view(bundle: Mapping[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    if bundle.get("normative_catalog_qualification_state") != "QUALIFIED": problems.append("NORMATIVE_CONTROL_CATALOG_INCOMPLETE")
    if bundle.get("endpoint_precedence_state") != "ENDPOINT_PRECEDENCE_CORRECTNESS_QUALIFIED": problems.append("ENDPOINT_PRECEDENCE_CORRECTNESS_NOT_QUALIFIED")
    rules=bundle.get("proof_field_descriptors")
    if not isinstance(rules,list) or not rules: rules=[]; problems.append("PROOF_FIELD_DESCRIPTOR_SET_REQUIRED")
    path=set(bundle.get("exact_decision_path_predicate_ids",[])) if isinstance(bundle.get("exact_decision_path_predicate_ids"),list) else set()
    admitted=set(bundle.get("admitted_applicability_predicate_ids",[])) if isinstance(bundle.get("admitted_applicability_predicate_ids"),list) else set()
    producer=set(bundle.get("producer_requested_field_ids",[])) if isinstance(bundle.get("producer_requested_field_ids"),list) else set()
    applicable_predicates=path|admitted
    by_field={}; compiled=[]
    allowed_redactions=set(bundle.get("kernel_bound_redaction_classes",[])) if isinstance(bundle.get("kernel_bound_redaction_classes"),list) else set()
    for r in rules:
        if not isinstance(r,Mapping): problems.append("PROOF_FIELD_DESCRIPTOR_MALFORMED"); continue
        fid=r.get("field_id"); pid=r.get("predicate_id"); control=r.get("control_id"); source=r.get("source_binding"); redaction=r.get("redaction_class")
        if not isinstance(fid,str) or not fid: problems.append("PROOF_FIELD_ID_INVALID"); continue
        if fid in by_field: problems.append(f"PROOF_FIELD_DUPLICATE:{fid}"); continue
        by_field[fid]=r
        if not all(isinstance(x,str) and x for x in (pid,control,source,redaction)): problems.append(f"PROOF_FIELD_BINDING_INCOMPLETE:{fid}")
        if redaction not in allowed_redactions: problems.append(f"PROOF_REDACTION_CLASS_UNADMITTED:{fid}:{redaction}")
        mandatory=pid in applicable_predicates
        if mandatory and r.get("qualification_or_failure_field") is True and redaction=="OMIT": problems.append(f"PROOF_FAILURE_REDACTION_FORBIDDEN:{fid}")
        if mandatory: compiled.append({"field_id":fid,"predicate_id":pid,"control_id":control,"source_binding":source,"redaction_class":redaction,"mandatory":True})
    # Producer request can only be a subset/view preference; it cannot remove mandatory fields.
    compiled_ids={x["field_id"] for x in compiled}
    if producer and not compiled_ids.issubset(producer): problems.append("PRODUCER_SELECTION_ATTEMPTS_TO_OMIT_MANDATORY_FIELD")
    mapped_predicates={x["predicate_id"] for x in compiled}
    for pid in sorted(applicable_predicates-mapped_predicates): problems.append(f"APPLICABLE_PREDICATE_PROOF_FIELD_MISSING:{pid}")
    problems=sorted(set(problems))
    return {"state":"PROOF_VIEW_APPLICABILITY_COMPILED" if not problems else "PROOF_VIEW_APPLICABILITY_INCOMPLETE","qualified":False,"problems":problems,"mandatory_fields":sorted(compiled,key=lambda x:x["field_id"]),"manifest_digest":digest(compiled),"authority_effect":AUTHORITY_EFFECT}
