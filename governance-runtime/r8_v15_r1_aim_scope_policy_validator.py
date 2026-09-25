"""R8 v15-r1 Slice 26: local AIMScopePolicy structural validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("aim_scope_policy_id","class_rules","effective_sequence","lifecycle_state","constitutional_authority_evidence_digest","policy_digest")
RULE_FIELDS: Tuple[str,...]=("semantic_class","allowed_any_tuple_components")
SCOPE_COMPONENT_NAMES=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
LIFECYCLE_STATES={"ACTIVE","SUSPENDED","RETIRED","REVOKED"}
INT64_MAX=slice1.INT64_MAX

class AIMScopePolicyError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _gcp_string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_GCP_INVALID",f"{field}: {exc}") from exc

def _validate_rule(rule:Any,index:int)->str:
    if not isinstance(rule,Mapping):
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_RULE_INVALID",f"class_rules[{index}] must be mapping")
    actual=set(rule.keys()); expected=set(RULE_FIELDS)
    if len(rule)!=len(RULE_FIELDS) or actual!=expected:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_RULE_FIELD_SET_INVALID",f"class_rules[{index}] field set invalid")
    _gcp_string(rule["semantic_class"],f"class_rules[{index}].semantic_class")
    comps=rule["allowed_any_tuple_components"]
    if not isinstance(comps,list):
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_COMPONENTS_INVALID",f"class_rules[{index}] components must be list")
    for v in comps:
        if not isinstance(v,str) or v not in SCOPE_COMPONENT_NAMES:
            raise AIMScopePolicyError("AIM_SCOPE_POLICY_COMPONENT_NAME_INVALID",f"class_rules[{index}] contains invalid component")
    if len(set(comps))!=len(comps):
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_COMPONENTS_NOT_UNIQUE",f"class_rules[{index}] components must be unique")
    return rule["semantic_class"]

def validate_aim_scope_policy(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(FIELDS)
    if len(record)!=len(FIELDS) or actual!=expected:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for field in ("aim_scope_policy_id","constitutional_authority_evidence_digest","policy_digest"):
        _gcp_string(record[field],field)
    rules=record["class_rules"]
    if not isinstance(rules,list) or not rules:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_RULES_INVALID","class_rules must be non-empty list")
    semantic_classes=[]
    for i,rule in enumerate(rules):
        semantic_classes.append(_validate_rule(rule,i))
    if len(set(semantic_classes))!=len(semantic_classes):
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_CLASS_NOT_UNIQUE","class_rules semantic_class values must be unique")
    seq=record["effective_sequence"]
    if isinstance(seq,bool) or not isinstance(seq,int) or seq<0 or seq>INT64_MAX:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_SEQUENCE_INVALID","effective_sequence outside frozen Sequence")
    state=record["lifecycle_state"]
    if not isinstance(state,str) or state not in LIFECYCLE_STATES:
        raise AIMScopePolicyError("AIM_SCOPE_POLICY_LIFECYCLE_INVALID","lifecycle_state outside frozen enum")
    return {"locally_valid":True,"class_rule_count":len(rules),"declared_lifecycle_state":state,"validation_scope":"LOCAL_AIM_SCOPE_POLICY_STRUCTURE_ONLY","authority_effect":"NONE","policy_current":False,"policy_effective":False,"constitutional_evidence_verified":False,"anti_broadening_enforced":False,"any_permission_authorized":False,"semantic_selected":False,"scope_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
