"""R8 v15-r1 Slice 24: local ANYScopePermission structural validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX
ANY_SCOPE_PERMISSION_FIELDS: Tuple[str,...]=("permission_id","semantic_class","allowed_any_tuple_components","effective_sequence","lifecycle_state","constitutional_authority_evidence_digest","permission_digest")
SCOPE_COMPONENT_NAMES=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
LIFECYCLE_STATES={"ACTIVE","SUSPENDED","RETIRED","REVOKED"}

class ANYScopePermissionError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise ANYScopePermissionError("ANY_PERMISSION_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ANYScopePermissionError("ANY_PERMISSION_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def validate_any_scope_permission(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise ANYScopePermissionError("ANY_PERMISSION_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(ANY_SCOPE_PERMISSION_FIELDS)
    if len(record)!=len(ANY_SCOPE_PERMISSION_FIELDS) or actual!=expected:
        raise ANYScopePermissionError("ANY_PERMISSION_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for f in ("permission_id","semantic_class","constitutional_authority_evidence_digest","permission_digest"):_string(record[f],f)
    comps=record["allowed_any_tuple_components"]
    if not isinstance(comps,list):
        raise ANYScopePermissionError("ANY_PERMISSION_COMPONENTS_INVALID","allowed_any_tuple_components must be list")
    for v in comps:
        if not isinstance(v,str) or v not in SCOPE_COMPONENT_NAMES:
            raise ANYScopePermissionError("ANY_PERMISSION_COMPONENT_NAME_INVALID","component outside frozen enum")
    if len(set(comps))!=len(comps):
        raise ANYScopePermissionError("ANY_PERMISSION_COMPONENTS_NOT_UNIQUE","components must be unique")
    seq=record["effective_sequence"]
    if isinstance(seq,bool) or not isinstance(seq,int) or seq<0 or seq>INT64_MAX:
        raise ANYScopePermissionError("ANY_PERMISSION_SEQUENCE_INVALID","effective_sequence outside frozen Sequence")
    state=record["lifecycle_state"]
    if not isinstance(state,str) or state not in LIFECYCLE_STATES:
        raise ANYScopePermissionError("ANY_PERMISSION_LIFECYCLE_INVALID","lifecycle_state outside frozen enum")
    return {"locally_valid":True,"permission_id":record["permission_id"],"declared_lifecycle_state":state,"validation_scope":"LOCAL_ANY_SCOPE_PERMISSION_STRUCTURE_ONLY","authority_effect":"NONE","permission_current":False,"permission_effective":False,"semantic_entry_any_coverage_verified":False,"constitutional_evidence_verified":False,"broadening_authorized":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
