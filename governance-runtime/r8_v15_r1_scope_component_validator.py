"""R8 v15-r1 Slice 21: local ScopeComponent validation only."""
from __future__ import annotations
import json
from typing import Any, Dict
import r8_v15_r1_frozen_schema_runtime as slice1

ANY_SENTINEL="ANY"; STABLE_SCOPE_REF="#/$defs/StableScopeValue"; STABLE_SCOPE_PATTERN="^(?!ANY$).+"
ECMA_LINE_TERMINATORS=("\n","\r","\u2028","\u2029")

class ScopeComponentError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _gcp(value:str)->None:
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ScopeComponentError("SCOPE_COMPONENT_GCP_INVALID",str(exc)) from exc

def _stable_branch_matches_frozen_pattern(value:str)->bool:
    return value != ANY_SENTINEL and value[0] not in ECMA_LINE_TERMINATORS

def validate_scope_component(value:Any)->Dict[str,Any]:
    if not isinstance(value,str) or not value:
        raise ScopeComponentError("SCOPE_COMPONENT_INVALID","must be non-empty string")
    if value != ANY_SENTINEL and not _stable_branch_matches_frozen_pattern(value):
        raise ScopeComponentError("SCOPE_COMPONENT_PATTERN_INVALID",f"stable branch does not match frozen pattern {STABLE_SCOPE_PATTERN}")
    _gcp(value)
    kind="ANY" if value==ANY_SENTINEL else "STABLE"
    return {"locally_valid":True,"value":value,"component_kind":kind,"validation_scope":"LOCAL_SCOPE_COMPONENT_SYNTAX_ONLY","authority_effect":"NONE","any_permission_verified":False,"scope_current":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
