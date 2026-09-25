"""R8 v15-r1 Slice 10: local ReviewAttestation validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

REVIEW_ATTESTATION_FIELDS: Tuple[str,...]=(
    "reviewer_canonical_subject_id",
    "reviewer_admin_domain_id",
    "candidate_digest",
    "governance_snapshot_digest",
    "packet_digest",
    "attestation_digest",
    "review_dimension_results",
)

REVIEW_DIMENSION_FIELDS: Tuple[str,...]=(
    "dimension_id",
    "result",
    "result_digest",
)

REVIEW_RESULTS={"PASS","FAIL","UNAVAILABLE"}

class ReviewAttestationError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _meta()->Dict[str,Any]:
    return {
        "authority_effect":"NONE",
        "dimension_uniqueness_proven":False,
        "reviewer_independence_proven":False,
        "signature_verified":False,
        "attestation_digest_verified":False,
        "review_gate_closed":False,
        "promotion_authorized":False,
        "runtime_qualified":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authorized":False,
        "terminal_authority":False,
    }

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise ReviewAttestationError("REVIEW_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise ReviewAttestationError("REVIEW_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def validate_review_attestation(attestation:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(attestation,Mapping):
        raise ReviewAttestationError("REVIEW_ATTESTATION_FIELD_SET_INVALID","ReviewAttestation must be mapping")
    actual=set(attestation.keys()); expected=set(REVIEW_ATTESTATION_FIELDS)
    if len(attestation)!=len(REVIEW_ATTESTATION_FIELDS) or actual!=expected:
        raise ReviewAttestationError(
            "REVIEW_ATTESTATION_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )

    for field in REVIEW_ATTESTATION_FIELDS[:-1]:
        _string(attestation[field],field)

    dimensions=attestation["review_dimension_results"]
    if not isinstance(dimensions,list) or len(dimensions)<1:
        raise ReviewAttestationError("REVIEW_DIMENSIONS_INVALID","review_dimension_results must be non-empty JSON-array-equivalent list")

    for index,item in enumerate(dimensions):
        if not isinstance(item,Mapping):
            raise ReviewAttestationError("REVIEW_DIMENSION_FIELD_SET_INVALID",f"dimension[{index}] must be mapping")
        a=set(item.keys()); e=set(REVIEW_DIMENSION_FIELDS)
        if len(item)!=len(REVIEW_DIMENSION_FIELDS) or a!=e:
            raise ReviewAttestationError(
                "REVIEW_DIMENSION_FIELD_SET_INVALID",
                f"dimension[{index}] missing={sorted(e-a)} extra={sorted(a-e)}"
            )
        _string(item["dimension_id"],f"review_dimension_results[{index}].dimension_id")
        _string(item["result_digest"],f"review_dimension_results[{index}].result_digest")
        result=item["result"]
        if not isinstance(result,str) or result not in REVIEW_RESULTS:
            raise ReviewAttestationError(
                "REVIEW_DIMENSION_RESULT_INVALID",
                f"review_dimension_results[{index}].result must be PASS, FAIL, or UNAVAILABLE"
            )

    result={
        "locally_valid":True,
        "review_dimension_count":len(dimensions),
        "candidate_digest":attestation["candidate_digest"],
        "validation_scope":"LOCAL_REVIEW_ATTESTATION_STRUCTURE_ONLY",
    }
    result.update(_meta())
    return result
