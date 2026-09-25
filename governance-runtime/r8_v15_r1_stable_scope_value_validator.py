"""R8 v15-r1 Slice 20: local StableScopeValue validation only."""
from __future__ import annotations
import json
from typing import Any, Dict
import r8_v15_r1_frozen_schema_runtime as slice1

SCHEMA_TYPE="string"; MIN_LENGTH=1; PATTERN="^(?!ANY$).+"
ECMA_LINE_TERMINATORS=("\n","\r","\u2028","\u2029")

class StableScopeValueError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _gcp(value:str)->None:
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise StableScopeValueError("STABLE_SCOPE_GCP_INVALID",str(exc)) from exc

def _matches_frozen_pattern(value:str)->bool:
    # Exact semantics of frozen pattern ^(?!ANY$).+ for the already type/minLength-checked string:
    # exact ANY is excluded; the first scalar must not be an ECMA LineTerminator.
    # The tail is not end-anchored, so later/trailing line terminators do not invalidate a match.
    return value != "ANY" and value[0] not in ECMA_LINE_TERMINATORS

def validate_stable_scope_value(value:Any)->Dict[str,Any]:
    if not isinstance(value,str) or not value:
        raise StableScopeValueError("STABLE_SCOPE_VALUE_INVALID","must be non-empty string")
    if value=="ANY":
        raise StableScopeValueError("STABLE_SCOPE_ANY_FORBIDDEN","exact ANY is reserved sentinel")
    if not _matches_frozen_pattern(value):
        raise StableScopeValueError("STABLE_SCOPE_PATTERN_INVALID",f"value does not match frozen pattern {PATTERN}")
    _gcp(value)
    return {"locally_valid":True,"value":value,"validation_scope":"LOCAL_STABLE_SCOPE_VALUE_SYNTAX_ONLY","authority_effect":"NONE","scope_permission_verified":False,"scope_current":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
