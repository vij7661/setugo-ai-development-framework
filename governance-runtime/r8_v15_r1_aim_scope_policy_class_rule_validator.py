"""R8 v15-r1 Slice 25: local AIMScopePolicyClassRule structural validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

AIM_SCOPE_POLICY_CLASS_RULE_FIELDS: Tuple[str,...]=("semantic_class","allowed_any_tuple_components")
SCOPE_COMPONENT_NAMES=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")

class AIMScopePolicyClassRuleError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _class_string(value:Any)->None:
    if not isinstance(value,str) or not value:
        raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_STRING_INVALID","semantic_class must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_GCP_INVALID",str(exc)) from exc

def validate_aim_scope_policy_class_rule(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(AIM_SCOPE_POLICY_CLASS_RULE_FIELDS)
    if len(record)!=len(AIM_SCOPE_POLICY_CLASS_RULE_FIELDS) or actual!=expected:
        raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    _class_string(record["semantic_class"])
    comps=record["allowed_any_tuple_components"]
    if not isinstance(comps,list):
        raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_COMPONENTS_INVALID","allowed_any_tuple_components must be list")
    for v in comps:
        if not isinstance(v,str) or v not in SCOPE_COMPONENT_NAMES:
            raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_COMPONENT_NAME_INVALID","component outside frozen enum")
    if len(set(comps))!=len(comps):
        raise AIMScopePolicyClassRuleError("AIM_SCOPE_CLASS_COMPONENTS_NOT_UNIQUE","components must be unique")
    return {"locally_valid":True,"semantic_class":record["semantic_class"],"component_count":len(comps),"validation_scope":"LOCAL_AIM_SCOPE_POLICY_CLASS_RULE_STRUCTURE_ONLY","authority_effect":"NONE","aim_policy_current":False,"any_permission_authorized":False,"semantic_selected":False,"scope_authorized":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
