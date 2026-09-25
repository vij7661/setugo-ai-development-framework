"""R8 v15-r1 Slice 13: local ResolverConformanceSuite1 validation only."""

from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

RCS_SUITE_FIELDS:Tuple[str,...]=(
 "suite_id","suite_version","vector_manifest_digest","vector_generator_implementation_digest",
 "generator_runtime_manifest_digest","input_corpus_digest","expected_result_manifest_digest",
 "execution_harness_digest","required_resolver_runtime_identity_digest",
 "required_resolver_workload_identity_digest","result_schema_digest","suite_digest"
)

class RCSSuiteError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(v:Any,field:str)->None:
    if not isinstance(v,str) or not v:
        raise RCSSuiteError("RCS_SUITE_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":v},ensure_ascii=True,separators=(",",":"))
    try:slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:raise RCSSuiteError("RCS_SUITE_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def validate_rcs_suite(value:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(value,Mapping):
        raise RCSSuiteError("RCS_SUITE_FIELD_SET_INVALID","ResolverConformanceSuite1 must be mapping")
    actual=set(value.keys()); expected=set(RCS_SUITE_FIELDS)
    if len(value)!=len(RCS_SUITE_FIELDS) or actual!=expected:
        raise RCSSuiteError("RCS_SUITE_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for f in RCS_SUITE_FIELDS:_string(value[f],f)
    return {
      "locally_valid":True,
      "validation_scope":"LOCAL_SUITE_IDENTITY_STRUCTURE_ONLY",
      "authority_effect":"NONE",
      "required_runtime_identity_verified":False,
      "required_workload_identity_verified":False,
      "suite_digest_verified":False,
      "vector_generator_identity_verified":False,
      "execution_harness_verified":False,
      "suite_current":False,
      "suite_executed":False,
      "resolver_qualified":False,
      "conformance_fresh":False,
      "runtime_qualified":False,
      "release_authorized":False,
      "deployment_authorized":False,
      "production_authorized":False,
      "policy_authority_granted":False,
      "terminal_authority":False
    }
