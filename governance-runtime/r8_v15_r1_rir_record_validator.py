"""R8 v15-r1 Slice 12: local ResolverImplementationRegistryRecord validation only."""

from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

INT64_MAX=slice1.INT64_MAX
RIR_RECORD_FIELDS:Tuple[str,...]=(
 "resolver_implementation_record_id","rir_record_id","resolver_policy_digest","implementation_id",
 "resolver_implementation_digest","resolver_runtime_manifest_digest","workload_attestation_policy_digest",
 "runtime_identity_digest","workload_identity_digest","conformance_suite_digest","predecessor_record_id",
 "constitutional_source_evidence_digest","activation_sequence","retirement_or_revocation_sequence",
 "lifecycle_state","freshness_profile_id","record_digest"
)
STRING_FIELDS=tuple(f for f in RIR_RECORD_FIELDS if f not in {"predecessor_record_id","activation_sequence","retirement_or_revocation_sequence","lifecycle_state"})
LIFECYCLE={"ACTIVE","SUSPENDED","RETIRED","REVOKED"}

class RIRRecordError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(v:Any,field:str)->None:
    if not isinstance(v,str) or not v:
        raise RIRRecordError("RIR_STRING_INVALID",f"{field} must be non-empty string")
    encoded=json.dumps({"value":v},ensure_ascii=True,separators=(",",":"))
    try:slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:raise RIRRecordError("RIR_GCP_STRING_INVALID",f"{field}: {exc}") from exc

def _seq(v:Any,field:str)->None:
    if isinstance(v,bool) or not isinstance(v,int) or v<0 or v>INT64_MAX:
        raise RIRRecordError("RIR_SEQUENCE_INVALID",f"{field} outside frozen Sequence closure")

def validate_rir_record(value:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(value,Mapping):
        raise RIRRecordError("RIR_FIELD_SET_INVALID","RIR record must be mapping")
    actual=set(value.keys()); expected=set(RIR_RECORD_FIELDS)
    if len(value)!=len(RIR_RECORD_FIELDS) or actual!=expected:
        raise RIRRecordError("RIR_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    for f in STRING_FIELDS:_string(value[f],f)
    pred=value["predecessor_record_id"]
    if pred is not None:
        if not isinstance(pred,str) or not pred:
            raise RIRRecordError("RIR_PREDECESSOR_INVALID","predecessor_record_id must be null or non-empty string")
        try:_string(pred,"predecessor_record_id")
        except RIRRecordError as exc:
            if exc.code=="RIR_GCP_STRING_INVALID":raise
            raise RIRRecordError("RIR_PREDECESSOR_INVALID",str(exc)) from exc
    _seq(value["activation_sequence"],"activation_sequence")
    retire=value["retirement_or_revocation_sequence"]
    if retire is not None:_seq(retire,"retirement_or_revocation_sequence")
    if value["lifecycle_state"] not in LIFECYCLE:
        raise RIRRecordError("RIR_LIFECYCLE_INVALID","unsupported lifecycle_state")
    return {
      "locally_valid":True,
      "validation_scope":"LOCAL_RECORD_STRUCTURE_ONLY",
      "authority_effect":"NONE",
      "temporal_ordering_verified":False,
      "temporal_eligibility_proven":False,
      "record_digest_verified":False,
      "record_current":False,
      "registry_head_current":False,
      "resolver_authorized":False,
      "conformance_qualified":False,
      "runtime_qualified":False,
      "release_authorized":False,
      "deployment_authorized":False,
      "production_authorized":False,
      "policy_authority_granted":False,
      "terminal_authority":False
    }
