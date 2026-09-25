"""R8 v15-r1 Slice 21: local ScopeComponent validation only."""
from __future__ import annotations
import json
from typing import Any, Dict
import r8_v15_r1_frozen_schema_runtime as slice1

ANY_SENTINEL="ANY"; STABLE_SCOPE_REF="#/$defs/StableScopeValue"

class ScopeComponentError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _gcp(value:str)->None:
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ScopeComponentError("SCOPE_COMPONENT_GCP_INVALID",str(exc)) from exc

def validate_scope_component(value:Any)->Dict[str,Any]:
    if not isinstance(value,str) or not value:
        raise ScopeComponentError("SCOPE_COMPONENT_INVALID","must be non-empty string")
    _gcp(value)
    kind="ANY" if value==ANY_SENTINEL else "STABLE"
    return {"locally_valid":True,"value":value,"component_kind":kind,"validation_scope":"LOCAL_SCOPE_COMPONENT_SYNTAX_ONLY","authority_effect":"NONE","any_permission_verified":False,"scope_current":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
