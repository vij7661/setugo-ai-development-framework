"""R8 v15-r1 Slice 9: local EvidenceRecord validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX

EVIDENCE_RECORD_FIELDS: Tuple[str,...]=(
    "evidence_id","evidence_class","producer_identity_digest","runtime_identity_digest",
    "input_digest","input_object_ids","input_object_digests","execution_proof_digest",
    "output_derivation_digest","event_id","output_digest","effective_sequence","evidence_digest",
)

_SCALAR_STRING_FIELDS=(
    "evidence_id","evidence_class","producer_identity_digest","runtime_identity_digest",
    "input_digest","execution_proof_digest","output_derivation_digest","event_id",
    "output_digest","evidence_digest",
)

class EvidenceRecordError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _meta()->Dict[str,Any]:
    return {
        "authority_effect":"NONE",
        "input_arrays_correspondence_proven":False,
        "input_uniqueness_proven":False,
        "evidence_digest_verified":False,
        "execution_proof_verified":False,
        "output_derivation_verified":False,
        "evidence_class_upgrade_valid":False,
        "producer_revocation_temporally_valid":False,
        "mandatory_evidence_satisfied":False,
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
        raise EvidenceRecordError("EVIDENCE_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise EvidenceRecordError("EVIDENCE_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def _sequence(value:Any)->None:
    if isinstance(value,bool) or not isinstance(value,int) or value<0 or value>INT64_MAX:
        raise EvidenceRecordError("EVIDENCE_SEQUENCE_INVALID","effective_sequence outside frozen Sequence closure")

def validate_evidence_record(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise EvidenceRecordError("EVIDENCE_FIELD_SET_INVALID","EvidenceRecord must be mapping")
    actual=set(record.keys()); expected=set(EVIDENCE_RECORD_FIELDS)
    if len(record)!=len(EVIDENCE_RECORD_FIELDS) or actual!=expected:
        raise EvidenceRecordError("EVIDENCE_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")

    for field in _SCALAR_STRING_FIELDS:
        _string(record[field],field)

    ids=record["input_object_ids"]
    if not isinstance(ids,list) or len(ids)<1:
        raise EvidenceRecordError("EVIDENCE_INPUT_IDS_INVALID","input_object_ids must be non-empty JSON-array-equivalent list")
    for i,value in enumerate(ids):
        _string(value,f"input_object_ids[{i}]")

    digests=record["input_object_digests"]
    if not isinstance(digests,list) or len(digests)<1:
        raise EvidenceRecordError("EVIDENCE_INPUT_DIGESTS_INVALID","input_object_digests must be non-empty JSON-array-equivalent list")
    for i,value in enumerate(digests):
        _string(value,f"input_object_digests[{i}]")

    _sequence(record["effective_sequence"])

    result={
        "locally_valid":True,
        "evidence_id":record["evidence_id"],
        "evidence_class":record["evidence_class"],
        "effective_sequence":record["effective_sequence"],
        "input_object_id_count":len(ids),
        "input_object_digest_count":len(digests),
        "validation_scope":"LOCAL_EVIDENCE_RECORD_STRUCTURE_ONLY",
    }
    result.update(_meta())
    return result
