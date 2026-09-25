"""R8 v15-r1 Slice 43: structural SRTT-4 RuleRegistry validation with deterministic closure only."""
from __future__ import annotations
import json,re
from collections.abc import Mapping
from typing import Any,Dict,Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

ROOT_FIELDS:Tuple[str,...]=("schema","status","authority_effect","domain_fixed","outside_table_rule","rules")
DOMAIN_FIELDS=("source_entry_state",)
OUTSIDE_FIELDS=("rule_id","predicate","result","source_trace")
RULE_FIELDS=("rule_id","precedence","predicate","result","source_trace")
RULE_RE=re.compile(r"^SRTT15-R(?:0[1-9]|1[01])$")
RESULTS={"SEMANTIC_SCOPE_REVOKED","SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED","MAPPING_NOT_APPLICABLE","REPLACEMENT_ELIGIBLE","SEMANTIC_SCOPE_REPLACEMENT_INVALID"}

class SRTT4RuleRegistryError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact(v:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(v,Mapping) or len(v)!=len(fields) or set(v.keys())!=set(fields):
        raise SRTT4RuleRegistryError(code,f"{label} field set invalid")
    return v

def _string(v:Any,label:str)->None:
    if not isinstance(v,str) or not v:
        raise SRTT4RuleRegistryError("SRTT_RULE_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":v},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise SRTT4RuleRegistryError("SRTT_RULE_GCP_INVALID",f"{label}: {exc}") from exc

def _trace(v:Any,label:str)->None:
    if not isinstance(v,list) or not v:
        raise SRTT4RuleRegistryError("SRTT_RULE_TRACE_INVALID",f"{label} must be non-empty array")
    for i,x in enumerate(v): _string(x,f"{label}[{i}]")

def validate_srtt4_rule_registry(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,ROOT_FIELDS,"SRTT_RULE_ROOT_FIELDS_INVALID","root")
    if record["schema"]!="r8-v15-srtt-4-rule-registry/v1" or not isinstance(record["schema"],str):
        raise SRTT4RuleRegistryError("SRTT_RULE_SCHEMA_INVALID","schema const invalid")
    _string(record["status"],"status")
    if record["authority_effect"]!="NONE" or not isinstance(record["authority_effect"],str):
        raise SRTT4RuleRegistryError("SRTT_RULE_AUTHORITY_INVALID","authority_effect must be NONE")
    domain=_exact(record["domain_fixed"],DOMAIN_FIELDS,"SRTT_RULE_DOMAIN_FIELDS_INVALID","domain_fixed")
    if domain["source_entry_state"]!="REVOKED" or not isinstance(domain["source_entry_state"],str):
        raise SRTT4RuleRegistryError("SRTT_RULE_DOMAIN_INVALID","source_entry_state must be REVOKED")
    outside=_exact(record["outside_table_rule"],OUTSIDE_FIELDS,"SRTT_RULE_OUTSIDE_FIELDS_INVALID","outside_table_rule")
    if outside["rule_id"]!="SRTT15-R00" or not isinstance(outside["rule_id"],str):
        raise SRTT4RuleRegistryError("SRTT_RULE_OUTSIDE_ID_INVALID","outside rule id invalid")
    _string(outside["predicate"],"outside_table_rule.predicate")
    if outside["result"]!="NOT_A_REPLACEMENT_BRANCH" or not isinstance(outside["result"],str):
        raise SRTT4RuleRegistryError("SRTT_RULE_OUTSIDE_RESULT_INVALID","outside result invalid")
    _trace(outside["source_trace"],"outside_table_rule.source_trace")
    rules=record["rules"]
    if not isinstance(rules,list) or len(rules)!=11:
        raise SRTT4RuleRegistryError("SRTT_RULE_COUNT_INVALID","rules must contain exactly 11 items")
    ids=[]; precedences=[]
    for i,item in enumerate(rules):
        item=_exact(item,RULE_FIELDS,"SRTT_RULE_FIELDS_INVALID",f"rules[{i}]")
        rid=item["rule_id"]
        if not isinstance(rid,str) or RULE_RE.fullmatch(rid) is None:
            raise SRTT4RuleRegistryError("SRTT_RULE_ID_INVALID",f"rules[{i}].rule_id invalid")
        ids.append(rid)
        p=item["precedence"]
        if isinstance(p,bool) or not isinstance(p,int) or p<1 or p>11:
            raise SRTT4RuleRegistryError("SRTT_RULE_PRECEDENCE_INVALID",f"rules[{i}].precedence invalid")
        precedences.append(p)
        _string(item["predicate"],f"rules[{i}].predicate")
        if not isinstance(item["result"],str) or item["result"] not in RESULTS:
            raise SRTT4RuleRegistryError("SRTT_RULE_RESULT_INVALID",f"rules[{i}].result invalid")
        _trace(item["source_trace"],f"rules[{i}].source_trace")
    expected={f"SRTT15-R{i:02d}" for i in range(1,12)}
    if set(ids)!=expected or len(set(ids))!=11:
        raise SRTT4RuleRegistryError("SRTT_RULE_ID_CLOSURE_INVALID","rule ids must be exactly R01..R11 once each")
    if set(precedences)!=set(range(1,12)) or len(set(precedences))!=11:
        raise SRTT4RuleRegistryError("SRTT_RULE_PRECEDENCE_CLOSURE_INVALID","precedence must be exactly 1..11 once each")
    return {
      "locally_valid":True,
      "validation_scope":"LOCAL_SRTT4_RULE_REGISTRY_STRUCTURE_AND_CLOSURE_ONLY",
      "authority_effect":"NONE",
      "rule_id_closure_verified":True,
      "precedence_closure_verified":True,
      "predicate_semantics_verified":False,
      "decision_recomputation_performed":False,
      "currentness_verified":False,
      "replacement_authority_granted":False,
      "terminal_authority":False
    }
