"""R8 v15-r1 Slice 23: local ScopeComponentName enum validation only."""
from __future__ import annotations
from typing import Any, Dict, Tuple

SCOPE_COMPONENT_NAMES: Tuple[str,...]=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")

class ScopeComponentNameError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def validate_scope_component_name(value:Any)->Dict[str,Any]:
    if not isinstance(value,str) or value not in SCOPE_COMPONENT_NAMES:
        raise ScopeComponentNameError("SCOPE_COMPONENT_NAME_INVALID","value outside frozen enum")
    return {"locally_valid":True,"value":value,"validation_scope":"LOCAL_SCOPE_COMPONENT_NAME_ENUM_ONLY","authority_effect":"NONE","any_permission_verified":False,"scope_current":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
