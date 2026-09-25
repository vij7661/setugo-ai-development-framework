"""R8 v15-r1 Slice 15: local ResolverConformanceAggregateResult validation only."""

# CI retrigger only: no semantic change.

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX
RCS_AGGREGATE_RESULT_FIELDS: Tuple[str,...]=(
    "status",
    "vector_count",
    "passed_vector_count",
    "aggregate_digest",
)
RCS_AGGREGATE_STATUSES={"PASS","FAIL"}

class RCSAggregateResultError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise RCSAggregateResultError("RCS_AGGREGATE_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise RCSAggregateResultError("RCS_AGGREGATE_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def _count(value:Any,field:str,minimum:int,code:str)->None:
    if isinstance(value,bool) or not isinstance(value,int) or value<minimum or value>INT64_MAX:
        raise RCSAggregateResultError(code,f"{field} outside frozen integer closure")

def validate_rcs_aggregate_result(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise RCSAggregateResultError("RCS_AGGREGATE_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(RCS_AGGREGATE_RESULT_FIELDS)
    if len(record)!=len(RCS_AGGREGATE_RESULT_FIELDS) or actual!=expected:
        raise RCSAggregateResultError(
            "RCS_AGGREGATE_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )

    status=record["status"]
    if not isinstance(status,str) or status not in RCS_AGGREGATE_STATUSES:
        raise RCSAggregateResultError("RCS_AGGREGATE_STATUS_INVALID","status must be PASS or FAIL")

    _count(record["vector_count"],"vector_count",1,"RCS_AGGREGATE_VECTOR_COUNT_INVALID")
    _count(record["passed_vector_count"],"passed_vector_count",0,"RCS_AGGREGATE_PASSED_COUNT_INVALID")
    _string(record["aggregate_digest"],"aggregate_digest")

    return {
        "locally_valid":True,
        "status":status,
        "vector_count":record["vector_count"],
        "passed_vector_count":record["passed_vector_count"],
        "validation_scope":"LOCAL_RESOLVER_CONFORMANCE_AGGREGATE_RESULT_STRUCTURE_ONLY",
        "authority_effect":"NONE",
        "count_relation_verified":False,
        "aggregate_digest_verified":False,
        "aggregate_semantics_verified":False,
        "conformance_qualified":False,
        "resolver_authorized":False,
        "runtime_qualified":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authority_granted":False,
        "terminal_authority":False,
    }
