"""R8 v15-r1 Slice 16: local ResolverConformanceEvidence structural validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX

RCS_EVIDENCE_FIELDS: Tuple[str,...]=(
    "rir_record_digest","rir_record_id","resolver_policy_digest","implementation_id",
    "resolver_implementation_digest","resolver_runtime_manifest_digest","runtime_identity_digest",
    "workload_identity_digest","conformance_suite_digest","rcs_suite","rcs_suite_digest",
    "rcs_vector_digests","raw_per_vector_results","deterministic_aggregate_result",
    "registry_head_digest","freshness_profile_id","status","evidence_digest",
)
RCS_SUITE_FIELDS: Tuple[str,...]=(
    "suite_id","suite_version","vector_manifest_digest","vector_generator_implementation_digest",
    "generator_runtime_manifest_digest","input_corpus_digest","expected_result_manifest_digest",
    "execution_harness_digest","required_resolver_runtime_identity_digest",
    "required_resolver_workload_identity_digest","result_schema_digest","suite_digest",
)
RCS_VECTOR_RESULT_FIELDS: Tuple[str,...]=(
    "vector_id","input_digest","output_digest","result","result_digest",
)
RCS_AGGREGATE_RESULT_FIELDS: Tuple[str,...]=(
    "status","vector_count","passed_vector_count","aggregate_digest",
)
RCS_EVIDENCE_STATUSES={"PASS","FAIL","EXPIRED","UNAVAILABLE"}
RCS_VECTOR_RESULTS={"PASS","FAIL"}
RCS_AGGREGATE_STATUSES={"PASS","FAIL"}

_SCALAR_FIELDS=(
    "rir_record_digest","rir_record_id","resolver_policy_digest","implementation_id",
    "resolver_implementation_digest","resolver_runtime_manifest_digest","runtime_identity_digest",
    "workload_identity_digest","conformance_suite_digest","rcs_suite_digest",
    "registry_head_digest","freshness_profile_id","evidence_digest",
)

class RCSEvidenceError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise RCSEvidenceError("RCS_EVIDENCE_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise RCSEvidenceError("RCS_EVIDENCE_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def _exact(obj:Any,fields:Tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(obj,Mapping):
        raise RCSEvidenceError(code,f"{label} must be mapping")
    actual=set(obj.keys()); expected=set(fields)
    if len(obj)!=len(fields) or actual!=expected:
        raise RCSEvidenceError(code,f"{label} missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    return obj

def _count(value:Any,minimum:int,code:str,field:str)->None:
    if isinstance(value,bool) or not isinstance(value,int) or value<minimum or value>INT64_MAX:
        raise RCSEvidenceError(code,f"{field} outside frozen integer closure")

def _validate_suite(value:Any)->None:
    suite=_exact(value,RCS_SUITE_FIELDS,"RCS_EVIDENCE_SUITE_FIELD_SET_INVALID","rcs_suite")
    for field in RCS_SUITE_FIELDS:
        _string(suite[field],f"rcs_suite.{field}")

def _validate_vector(value:Any,index:int)->None:
    item=_exact(value,RCS_VECTOR_RESULT_FIELDS,"RCS_EVIDENCE_VECTOR_FIELD_SET_INVALID",f"raw_per_vector_results[{index}]")
    for field in ("vector_id","input_digest","output_digest","result_digest"):
        _string(item[field],f"raw_per_vector_results[{index}].{field}")
    result=item["result"]
    if not isinstance(result,str) or result not in RCS_VECTOR_RESULTS:
        raise RCSEvidenceError("RCS_EVIDENCE_VECTOR_RESULT_INVALID",f"raw_per_vector_results[{index}].result must be PASS or FAIL")

def _validate_aggregate(value:Any)->None:
    item=_exact(value,RCS_AGGREGATE_RESULT_FIELDS,"RCS_EVIDENCE_AGGREGATE_FIELD_SET_INVALID","deterministic_aggregate_result")
    status=item["status"]
    if not isinstance(status,str) or status not in RCS_AGGREGATE_STATUSES:
        raise RCSEvidenceError("RCS_EVIDENCE_AGGREGATE_STATUS_INVALID","aggregate status must be PASS or FAIL")
    _count(item["vector_count"],1,"RCS_EVIDENCE_AGGREGATE_VECTOR_COUNT_INVALID","vector_count")
    _count(item["passed_vector_count"],0,"RCS_EVIDENCE_AGGREGATE_PASSED_COUNT_INVALID","passed_vector_count")
    _string(item["aggregate_digest"],"deterministic_aggregate_result.aggregate_digest")

def validate_rcs_evidence(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,RCS_EVIDENCE_FIELDS,"RCS_EVIDENCE_FIELD_SET_INVALID","ResolverConformanceEvidence")

    for field in _SCALAR_FIELDS:
        _string(record[field],field)

    status=record["status"]
    if not isinstance(status,str) or status not in RCS_EVIDENCE_STATUSES:
        raise RCSEvidenceError("RCS_EVIDENCE_STATUS_INVALID","status must be PASS, FAIL, EXPIRED, or UNAVAILABLE")

    _validate_suite(record["rcs_suite"])

    digests=record["rcs_vector_digests"]
    if not isinstance(digests,list) or len(digests)<1:
        raise RCSEvidenceError("RCS_EVIDENCE_VECTOR_DIGESTS_INVALID","rcs_vector_digests must be non-empty list")
    for index,value in enumerate(digests):
        _string(value,f"rcs_vector_digests[{index}]")

    results=record["raw_per_vector_results"]
    if not isinstance(results,list) or len(results)<1:
        raise RCSEvidenceError("RCS_EVIDENCE_VECTOR_RESULTS_INVALID","raw_per_vector_results must be non-empty list")
    for index,value in enumerate(results):
        _validate_vector(value,index)

    _validate_aggregate(record["deterministic_aggregate_result"])

    return {
        "locally_valid":True,
        "status":status,
        "rir_record_id":record["rir_record_id"],
        "implementation_id":record["implementation_id"],
        "validation_scope":"LOCAL_RESOLVER_CONFORMANCE_EVIDENCE_STRUCTURE_ONLY",
        "authority_effect":"NONE",
        "suite_digest_binding_verified":False,
        "resolver_identity_binding_verified":False,
        "workload_identity_binding_verified":False,
        "vector_manifest_binding_verified":False,
        "array_count_relation_verified":False,
        "current_pass_exact_tuple_verified":False,
        "freshness_verified":False,
        "cached_pass_substitution_prevented":False,
        "evidence_digest_verified":False,
        "resolver_qualified":False,
        "resolver_authorized":False,
        "runtime_qualified":False,
        "evidence_promotion_authorized":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authority_granted":False,
        "terminal_authority":False,
    }
