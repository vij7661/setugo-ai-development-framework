"""R8 v15-r1 Slice 14: local ResolverConformanceVectorResult validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

RCS_VECTOR_RESULT_FIELDS: Tuple[str,...]=(
    "vector_id",
    "input_digest",
    "output_digest",
    "result",
    "result_digest",
)
RCS_VECTOR_RESULTS={"PASS","FAIL"}

class RCSVectorResultError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise RCSVectorResultError("RCS_VECTOR_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise RCSVectorResultError("RCS_VECTOR_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def validate_rcs_vector_result(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise RCSVectorResultError("RCS_VECTOR_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(RCS_VECTOR_RESULT_FIELDS)
    if len(record)!=len(RCS_VECTOR_RESULT_FIELDS) or actual!=expected:
        raise RCSVectorResultError(
            "RCS_VECTOR_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )

    for field in ("vector_id","input_digest","output_digest","result_digest"):
        _string(record[field],field)

    result=record["result"]
    if not isinstance(result,str) or result not in RCS_VECTOR_RESULTS:
        raise RCSVectorResultError("RCS_VECTOR_RESULT_INVALID","result must be PASS or FAIL")

    return {
        "locally_valid":True,
        "vector_id":record["vector_id"],
        "result":result,
        "validation_scope":"LOCAL_RESOLVER_CONFORMANCE_VECTOR_RESULT_STRUCTURE_ONLY",
        "authority_effect":"NONE",
        "input_digest_verified":False,
        "output_digest_verified":False,
        "result_digest_verified":False,
        "vector_executed":False,
        "conformance_qualified":False,
        "resolver_authorized":False,
        "runtime_qualified":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authority_granted":False,
        "terminal_authority":False,
    }
