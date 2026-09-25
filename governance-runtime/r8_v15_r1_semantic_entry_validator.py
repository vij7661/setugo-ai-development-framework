"""R8 v15-r1 Slice 17: local SemanticEntry structural validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX

SEMANTIC_ENTRY_FIELDS: Tuple[str,...]=(
    "semantic_entry_id","semantic_input_id","semantic_lineage_id","semantic_version",
    "scope_tuple","specificity_score","lifecycle_state","predecessor_entry_id",
    "successor_of_entry_id","scope_replacement_mapping_id","lineage_mapping_id",
    "any_scope_permission_id","semantic_class","artifact_or_rule_digest","schema_version",
    "source_authority_digest","effective_sequence","constitutional_binding_digest",
    "semantic_entry_key",
)
SCOPE_FIELDS: Tuple[str,...]=(
    "trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id",
    "project_id","experiment_or_release_id","object_class","action_class",
)
LIFECYCLE_STATES={
    "ACTIVE","SUSPENDED","REVOKED","SUPERSEDED","RETIRED",
    "SCOPE_PERMISSION_REEVALUATION_REQUIRED",
}
REQUIRED_STRINGS=(
    "semantic_entry_id","semantic_input_id","semantic_lineage_id","semantic_version",
    "semantic_class","artifact_or_rule_digest","schema_version","source_authority_digest",
    "semantic_entry_key",
)
NULLABLE_STRINGS=(
    "predecessor_entry_id","successor_of_entry_id","scope_replacement_mapping_id",
    "lineage_mapping_id","any_scope_permission_id","constitutional_binding_digest",
)

class SemanticEntryError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _gcp_string(value:str,field:str,*,code:str="SEMANTIC_ENTRY_GCP_STRING_INVALID")->None:
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise SemanticEntryError(code,f"{field}: {exc}") from exc

def _required_string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise SemanticEntryError("SEMANTIC_ENTRY_STRING_INVALID",f"{field} must be non-empty string")
    _gcp_string(value,field)

def _nullable_string(value:Any,field:str)->None:
    if value is None:
        return
    if not isinstance(value,str) or not value:
        raise SemanticEntryError("SEMANTIC_ENTRY_NULLABLE_STRING_INVALID",f"{field} must be null or non-empty string")
    _gcp_string(value,field)

def _scope_component(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise SemanticEntryError("SEMANTIC_ENTRY_SCOPE_COMPONENT_INVALID",f"{field} must be non-empty string")
    # Exact ANY is the frozen sentinel. All other non-empty strings are StableScopeValue.
    _gcp_string(value,field,code="SEMANTIC_ENTRY_SCOPE_COMPONENT_GCP_INVALID")

def _scope_tuple(value:Any)->Mapping[str,Any]:
    if not isinstance(value,Mapping):
        raise SemanticEntryError("SEMANTIC_ENTRY_SCOPE_FIELD_SET_INVALID","scope_tuple must be mapping")
    actual=set(value.keys()); expected=set(SCOPE_FIELDS)
    if len(value)!=len(SCOPE_FIELDS) or actual!=expected:
        raise SemanticEntryError(
            "SEMANTIC_ENTRY_SCOPE_FIELD_SET_INVALID",
            f"scope_tuple missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )
    for field in SCOPE_FIELDS:
        _scope_component(value[field],f"scope_tuple.{field}")
    return value

def validate_semantic_entry(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise SemanticEntryError("SEMANTIC_ENTRY_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(SEMANTIC_ENTRY_FIELDS)
    if len(record)!=len(SEMANTIC_ENTRY_FIELDS) or actual!=expected:
        raise SemanticEntryError(
            "SEMANTIC_ENTRY_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )

    for field in REQUIRED_STRINGS:
        _required_string(record[field],field)

    scope=_scope_tuple(record["scope_tuple"])

    specificity=record["specificity_score"]
    if isinstance(specificity,bool) or not isinstance(specificity,int) or not 0<=specificity<=9:
        raise SemanticEntryError("SEMANTIC_ENTRY_SPECIFICITY_INVALID","specificity_score must be integer 0..9")

    lifecycle=record["lifecycle_state"]
    if not isinstance(lifecycle,str) or lifecycle not in LIFECYCLE_STATES:
        raise SemanticEntryError("SEMANTIC_ENTRY_LIFECYCLE_INVALID","lifecycle_state outside frozen enum")

    for field in NULLABLE_STRINGS:
        _nullable_string(record[field],field)

    sequence=record["effective_sequence"]
    if isinstance(sequence,bool) or not isinstance(sequence,int) or sequence<0 or sequence>INT64_MAX:
        raise SemanticEntryError("SEMANTIC_ENTRY_SEQUENCE_INVALID","effective_sequence outside frozen Sequence closure")

    return {
        "locally_valid":True,
        "semantic_entry_id":record["semantic_entry_id"],
        "lifecycle_state":lifecycle,
        "effective_sequence":sequence,
        "validation_scope":"LOCAL_SEMANTIC_ENTRY_STRUCTURE_ONLY",
        "authority_effect":"NONE",
        "specificity_verified":False,
        "semantic_entry_key_verified":False,
        "any_scope_permission_verified":False,
        "entry_current":False,
        "semantic_selected":False,
        "lineage_transition_authorized":False,
        "scope_transition_authorized":False,
        "constitutional_authorized":False,
        "runtime_qualified":False,
        "evidence_promotion_authorized":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authority_granted":False,
        "terminal_authority":False,
    }
