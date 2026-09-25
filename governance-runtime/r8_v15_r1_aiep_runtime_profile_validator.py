"""R8 v15-r1 Slice 19: local AIEPRuntimeProfile structural validation only."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple

import r8_v15_r1_frozen_schema_runtime as slice1

AIEP_RUNTIME_PROFILE_FIELDS: Tuple[str,...]=(
    "runtime_manifest_digest","attestation_state","read_only_root_filesystem",
    "arbitrary_mutable_environment_allowed","direct_db_cloud_provider_credentials_allowed",
    "general_external_network_dns_allowed","approved_channel_ids",
    "dynamic_code_loading_outside_runtime_manifest_allowed","profile_digest",
)
ATTESTATION_STATES={"ATTESTED","UNATTESTED_RUNTIME"}

class AIEPRuntimeProfileError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}")
        self.code=code

def _gcp_string(value:str,field:str,code:str)->None:
    encoded=json.dumps({"value":value},ensure_ascii=True,separators=(",",":"))
    try:
        slice1.canonicalize_json_text(encoded,schema_context="object")
    except slice1.GCPError as exc:
        raise AIEPRuntimeProfileError(code,f"{field}: {exc}") from exc

def _digest(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise AIEPRuntimeProfileError("AIEP_PROFILE_STRING_INVALID",f"{field} must be non-empty string")
    _gcp_string(value,field,"AIEP_PROFILE_GCP_STRING_INVALID")

def _const_bool(value:Any,expected:bool,code:str,field:str)->None:
    if type(value) is not bool or value is not expected:
        raise AIEPRuntimeProfileError(code,f"{field} must be exact boolean {str(expected).lower()}")

def validate_aiep_runtime_profile(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise AIEPRuntimeProfileError("AIEP_PROFILE_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(AIEP_RUNTIME_PROFILE_FIELDS)
    if len(record)!=len(AIEP_RUNTIME_PROFILE_FIELDS) or actual!=expected:
        raise AIEPRuntimeProfileError(
            "AIEP_PROFILE_FIELD_SET_INVALID",
            f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}",
        )

    _digest(record["runtime_manifest_digest"],"runtime_manifest_digest")
    _digest(record["profile_digest"],"profile_digest")

    state=record["attestation_state"]
    if not isinstance(state,str) or state not in ATTESTATION_STATES:
        raise AIEPRuntimeProfileError("AIEP_PROFILE_ATTESTATION_STATE_INVALID","attestation_state outside frozen enum")

    _const_bool(record["read_only_root_filesystem"],True,"AIEP_PROFILE_READ_ONLY_ROOT_INVALID","read_only_root_filesystem")
    _const_bool(record["arbitrary_mutable_environment_allowed"],False,"AIEP_PROFILE_MUTABLE_ENV_INVALID","arbitrary_mutable_environment_allowed")
    _const_bool(record["direct_db_cloud_provider_credentials_allowed"],False,"AIEP_PROFILE_DIRECT_CREDENTIALS_INVALID","direct_db_cloud_provider_credentials_allowed")
    _const_bool(record["general_external_network_dns_allowed"],False,"AIEP_PROFILE_EXTERNAL_NETWORK_INVALID","general_external_network_dns_allowed")
    _const_bool(record["dynamic_code_loading_outside_runtime_manifest_allowed"],False,"AIEP_PROFILE_DYNAMIC_CODE_INVALID","dynamic_code_loading_outside_runtime_manifest_allowed")

    channels=record["approved_channel_ids"]
    if not isinstance(channels,list) or len(channels)<1:
        raise AIEPRuntimeProfileError("AIEP_PROFILE_CHANNELS_INVALID","approved_channel_ids must be non-empty list")
    checked=[]
    for index,value in enumerate(channels):
        if not isinstance(value,str) or not value:
            raise AIEPRuntimeProfileError("AIEP_PROFILE_CHANNEL_STRING_INVALID",f"approved_channel_ids[{index}] must be non-empty string")
        _gcp_string(value,f"approved_channel_ids[{index}]","AIEP_PROFILE_CHANNEL_GCP_INVALID")
        checked.append(value)
    if len(set(checked))!=len(checked):
        raise AIEPRuntimeProfileError("AIEP_PROFILE_CHANNELS_NOT_UNIQUE","approved_channel_ids must be unique")

    return {
        "locally_valid":True,
        "declared_attestation_state":state,
        "validation_scope":"LOCAL_AIEP_RUNTIME_PROFILE_STRUCTURE_ONLY",
        "authority_effect":"NONE",
        "runtime_manifest_verified":False,
        "profile_digest_verified":False,
        "attestation_verified":False,
        "approved_channels_authorized":False,
        "runtime_profile_current":False,
        "strong_evidence_producer_qualified":False,
        "root_authority_evaluator":False,
        "terminal_authority_evaluator":False,
        "runtime_qualified":False,
        "evidence_promotion_authorized":False,
        "release_authorized":False,
        "deployment_authorized":False,
        "production_authorized":False,
        "policy_authority_granted":False,
        "terminal_authority":False,
    }
