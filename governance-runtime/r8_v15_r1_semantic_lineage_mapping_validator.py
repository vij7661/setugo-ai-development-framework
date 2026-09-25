"""R8 v15-r1 Slice 18: local SemanticLineageMapping structural validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX

SEMANTIC_LINEAGE_MAPPING_FIELDS: Tuple[str,...]=(
    "mapping_id","semantic_input_id","source_lineage_id","destination_lineage_id",
    "source_entry_id","destination_entry_id","source_scope_tuple","destination_scope_tuple",
    "transition_semantics_digest","constitutional_evidence_digest","effective_sequence",
    "lifecycle_state","mapping_digest",
)
SCOPE_FIELDS: Tuple[str,...]=(
    "trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id",
    "project_id","experiment_or_release_id","object_class","action_class",
)
LIFECYCLE_STATES={"ACTIVE","SUSPENDED","RETIRED","REVOKED"}
REQUIRED_STRINGS=(
    "mapping_id","semantic_input_id","source_lineage_id","destination_lineage_id",
    "source_entry_id","destination_entry_id","transition_semantics_digest",
    "constitutional_evidence_digest","mapping_digest",
)

class SemanticLineageMappingError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _gcp_string(value:str,field:str,code:str)->None:
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise SemanticLineageMappingError(code,f"{field}: {exc}") from exc

def _required_string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise SemanticLineageMappingError("SEMANTIC_LINEAGE_STRING_INVALID",f"{field} must be non-empty string")
    _gcp_string(value,field,"SEMANTIC_LINEAGE_GCP_STRING_INVALID")

def _scope_component(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise SemanticLineageMappingError("SEMANTIC_LINEAGE_SCOPE_COMPONENT_INVALID",f"{field} must be non-empty string")
    _gcp_string(value,field,"SEMANTIC_LINEAGE_SCOPE_COMPONENT_GCP_INVALID")

def _scope_tuple(value:Any,label:str,code:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping):
        raise SemanticLineageMappingError(code,f"{label} must be mapping")
    actual=set(value.keys()); expected=set(SCOPE_FIELDS)
    if len(value)!=len(SCOPE_FIELDS) or actual!=expected:
        raise SemanticLineageMappingError(code,f"{label} missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for field in SCOPE_FIELDS:
        _scope_component(value[field],f"{label}.{field}")
    return value

def validate_semantic_lineage_mapping(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise SemanticLineageMappingError("SEMANTIC_LINEAGE_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(SEMANTIC_LINEAGE_MAPPING_FIELDS)
    if len(record)!=len(SEMANTIC_LINEAGE_MAPPING_FIELDS) or actual!=expected:
        raise SemanticLineageMappingError(
            "SEMANTIC_LINEAGE_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )

    for field in REQUIRED_STRINGS:
        _required_string(record[field],field)

    _scope_tuple(record["source_scope_tuple"],"source_scope_tuple","SEMANTIC_LINEAGE_SOURCE_SCOPE_FIELD_SET_INVALID")
    _scope_tuple(record["destination_scope_tuple"],"destination_scope_tuple","SEMANTIC_LINEAGE_DEST_SCOPE_FIELD_SET_INVALID")

    sequence=record["effective_sequence"]
    if isinstance(sequence,bool) or not isinstance(sequence,int) or sequence<0 or sequence>INT64_MAX:
        raise SemanticLineageMappingError("SEMANTIC_LINEAGE_SEQUENCE_INVALID","effective_sequence outside frozen Sequence closure")

    lifecycle=record["lifecycle_state"]
    if not isinstance(lifecycle,str) or lifecycle not in LIFECYCLE_STATES:
        raise SemanticLineageMappingError("SEMANTIC_LINEAGE_LIFECYCLE_INVALID","lifecycle_state outside frozen enum")

    return {
        "locally_valid":True,
        "mapping_id":record["mapping_id"],
        "lifecycle_state":lifecycle,
        "effective_sequence":sequence,
        "validation_scope":"LOCAL_SEMANTIC_LINEAGE_MAPPING_STRUCTURE_ONLY",
        "authority_effect":"NONE",
        "source_destination_relation_verified":False,
        "transition_semantics_digest_verified":False,
        "constitutional_evidence_digest_verified":False,
        "mapping_digest_verified":False,
        "mapping_current":False,
        "mapping_effective":False,
        "source_entry_exists":False,
        "destination_entry_exists":False,
        "source_lineage_exists":False,
        "destination_lineage_exists":False,
        "lineage_transition_authorized":False,
        "scope_transition_authorized":False,
        "semantic_selected":False,
        "constitutional_authorized":False,
        "runtime_qualified":False,
        "evidence_promotion_authorized":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authority_granted":False,
        "terminal_authority":False,
    }
