"""R8 v15-r1 Slice 27: local ScopeReplacementMapping structural validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("mapping_id","semantic_input_id","semantic_lineage_id","revoked_entry_id","destination_entry_id","old_scope_tuple","new_scope_tuple","old_specificity","new_specificity","old_scope_effect","decision_scope_match_rule_id","effective_sequence","constitutional_amendment_evidence_digest","lifecycle_state","mapping_digest")
SCOPE_FIELDS: Tuple[str,...]=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
OLD_SCOPE_EFFECTS={"BLOCK_OLD_SCOPE","REPLACE_OLD_SCOPE_FOR_EXACT_MATCH","REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH"}
LIFECYCLE_STATES={"ACTIVE","SUSPENDED","RETIRED","REVOKED"}
ECMA_LINE_TERMINATORS=("\n","\r","\u2028","\u2029")
INT64_MAX=slice1.INT64_MAX

class ScopeReplacementMappingError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _gcp_string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_GCP_INVALID",f"{field}: {exc}") from exc

def _scope_tuple(value:Any,field:str)->None:
    if not isinstance(value,Mapping):
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SCOPE_FIELD_SET_INVALID",f"{field} must be mapping")
    actual=set(value.keys()); expected=set(SCOPE_FIELDS)
    if len(value)!=len(SCOPE_FIELDS) or actual!=expected:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SCOPE_FIELD_SET_INVALID",f"{field} field set invalid")
    for component in SCOPE_FIELDS:
        v=value[component]
        if not isinstance(v,str) or not v:
            raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SCOPE_COMPONENT_INVALID",f"{field}.{component} must be non-empty string")
        if v!="ANY" and v[0] in ECMA_LINE_TERMINATORS:
            raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SCOPE_COMPONENT_PATTERN_INVALID",f"{field}.{component} violates frozen StableScopeValue pattern")
        try:
            slice1.canonicalize_json_text(json.dumps({"value":v},ensure_ascii=True,separators=(",",":")),schema_context="object")
        except slice1.GCPError as exc:
            raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SCOPE_COMPONENT_GCP_INVALID",f"{field}.{component}: {exc}") from exc

def validate_scope_replacement_mapping(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(FIELDS)
    if len(record)!=len(FIELDS) or actual!=expected:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for field in ("mapping_id","semantic_input_id","semantic_lineage_id","revoked_entry_id","destination_entry_id","decision_scope_match_rule_id","constitutional_amendment_evidence_digest","mapping_digest"):
        _gcp_string(record[field],field)
    _scope_tuple(record["old_scope_tuple"],"old_scope_tuple")
    _scope_tuple(record["new_scope_tuple"],"new_scope_tuple")
    for field in ("old_specificity","new_specificity"):
        v=record[field]
        if isinstance(v,bool) or not isinstance(v,int) or v<0 or v>9:
            raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SPECIFICITY_INVALID",f"{field} outside 0..9")
    effect=record["old_scope_effect"]
    if not isinstance(effect,str) or effect not in OLD_SCOPE_EFFECTS:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_EFFECT_INVALID","old_scope_effect outside frozen enum")
    seq=record["effective_sequence"]
    if isinstance(seq,bool) or not isinstance(seq,int) or seq<0 or seq>INT64_MAX:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_SEQUENCE_INVALID","effective_sequence outside frozen Sequence")
    state=record["lifecycle_state"]
    if not isinstance(state,str) or state not in LIFECYCLE_STATES:
        raise ScopeReplacementMappingError("SCOPE_REPLACEMENT_LIFECYCLE_INVALID","lifecycle_state outside frozen enum")
    return {"locally_valid":True,"validation_scope":"LOCAL_SCOPE_REPLACEMENT_MAPPING_STRUCTURE_ONLY","authority_effect":"NONE","objects_exist_verified":False,"specificity_matches_scope":False,"scope_relation_verified":False,"mapping_current":False,"mapping_effective":False,"constitutional_amendment_verified":False,"replacement_authorized":False,"semantic_selected":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
