"""R8 v15-r1 Slice 22: local CanonicalScopeTuple validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

SCOPE_FIELDS: Tuple[str,...]=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
STABLE_SCOPE_PATTERN="^(?!ANY$).+"
ECMA_LINE_TERMINATORS=("\n","\r","\u2028","\u2029")

class CanonicalScopeTupleError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _component(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise CanonicalScopeTupleError("CANONICAL_SCOPE_COMPONENT_INVALID",f"{field} must be non-empty string")
    if value != "ANY" and value[0] in ECMA_LINE_TERMINATORS:
        raise CanonicalScopeTupleError("CANONICAL_SCOPE_COMPONENT_PATTERN_INVALID",f"{field} stable branch does not match frozen pattern {STABLE_SCOPE_PATTERN}")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise CanonicalScopeTupleError("CANONICAL_SCOPE_COMPONENT_GCP_INVALID",f"{field}: {exc}") from exc

def validate_canonical_scope_tuple(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise CanonicalScopeTupleError("CANONICAL_SCOPE_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(SCOPE_FIELDS)
    if len(record)!=len(SCOPE_FIELDS) or actual!=expected:
        raise CanonicalScopeTupleError("CANONICAL_SCOPE_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for f in SCOPE_FIELDS:_component(record[f],f)
    return {"locally_valid":True,"canonical_order":list(SCOPE_FIELDS),"validation_scope":"LOCAL_CANONICAL_SCOPE_TUPLE_STRUCTURE_ONLY","authority_effect":"NONE","any_permission_verified":False,"scope_current":False,"scope_match_verified":False,"scope_relation_verified":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
