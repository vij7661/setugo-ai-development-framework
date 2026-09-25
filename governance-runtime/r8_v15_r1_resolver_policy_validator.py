"""R8 v15-r1 Slice 11: local ResolverPolicyContract validation only."""

from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

RESOLVER_POLICY_FIELDS: Tuple[str,...]=(
 "policy_version","resolver_algorithm_version","resolver_policy_id",
 "lineage_start_rule_digest","candidate_construction_rule_digest","specificity_rule_digest",
 "lifecycle_error_precedence_digest","mapping_traversal_rule_digest","successor_traversal_rule_digest",
 "replacement_evaluation_rule_digest","any_validation_rule_digest","fallback_prohibition_rule_digest",
 "forensic_replay_rule_digest","conformance_suite_id","resolver_policy_digest","conformance_vector_set_digest"
)

class ResolverPolicyError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(v:Any,field:str)->None:
    if not isinstance(v,str) or not v:
        raise ResolverPolicyError("RESOLVER_POLICY_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":v},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise ResolverPolicyError("RESOLVER_POLICY_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def validate_resolver_policy_contract(value:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(value,Mapping):
        raise ResolverPolicyError("RESOLVER_POLICY_FIELD_SET_INVALID","ResolverPolicyContract must be mapping")
    actual=set(value.keys()); expected=set(RESOLVER_POLICY_FIELDS)
    if len(value)!=len(RESOLVER_POLICY_FIELDS) or actual!=expected:
        raise ResolverPolicyError("RESOLVER_POLICY_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for field in RESOLVER_POLICY_FIELDS:
        _string(value[field],field)
    return {
      "locally_valid":True,
      "validation_scope":"LOCAL_STRUCTURE_ONLY",
      "authority_effect":"NONE",
      "resolver_policy_digest_verified":False,
      "conformance_vector_set_digest_verified":False,
      "policy_current":False,
      "policy_active":False,
      "policy_authorized":False,
      "resolver_authorized":False,
      "runtime_qualified":False,
      "release_authorized":False,
      "deployment_authorized":False,
      "production_authorized":False,
      "policy_authority_granted":False,
      "terminal_authority":False
    }
