"""R8 v15-r1 Slice 40: composite SPG-1 binding + RuntimeManifest structural validation only."""
from __future__ import annotations
import json, re
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","generator_id","generator_artifact_path","generator_artifact_sha256","runtime_manifest","workload_attestation_policy_digest","workload_attestation_proof_digest","allowed_input_design_artifacts","allowed_output_schema_classes","signing_credential_id","revocation_state","qualification_status")
RUNTIME_FIELDS: Tuple[str,...]=("application_artifact_digest","interpreter_compiler_runtime_version_digest","crypto_library_digest","schema_parser_bundle_digest","os_container_image_digest","las_anchor_client_library_digest","runtime_manifest_digest")
STATUS={"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","QUALIFIED_GENERATOR_BINDING"}
REVOCATION={"ACTIVE","SUSPENDED","REVOKED","RETIRED","UNKNOWN"}
QUALIFICATION={"QUALIFIED","UNATTESTED_RUNTIME","REVOKED","DRIFTED","UNREGISTERED"}
DIGEST_RE=re.compile(r"^[0-9a-f]{64}$")

class SPG1BindingError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact(value:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping) or len(value)!=len(fields) or set(value.keys())!=set(fields):
        raise SPG1BindingError(code,f"{label} field set invalid")
    return value

def _string(value:Any,label:str)->None:
    if not isinstance(value,str) or not value:
        raise SPG1BindingError("SPG_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise SPG1BindingError("SPG_GCP_INVALID",f"{label}: {exc}") from exc

def _digest(value:Any,label:str)->None:
    if not isinstance(value,str) or DIGEST_RE.fullmatch(value) is None:
        raise SPG1BindingError("SPG_DIGEST_INVALID",f"{label} invalid SHA-256")

def _nullable_digest(value:Any,label:str)->None:
    if value is not None: _digest(value,label)

def _string_array(value:Any,label:str)->None:
    if not isinstance(value,list) or not value:
        raise SPG1BindingError("SPG_STRING_ARRAY_INVALID",f"{label} must be non-empty array")
    for i,item in enumerate(value): _string(item,f"{label}[{i}]")
    if len(set(value))!=len(value):
        raise SPG1BindingError("SPG_STRING_ARRAY_NOT_UNIQUE",f"{label} uniqueItems violated")

def _runtime(value:Any)->None:
    value=_exact(value,RUNTIME_FIELDS,"SPG_RUNTIME_FIELDS_INVALID","runtime_manifest")
    _digest(value["application_artifact_digest"],"runtime_manifest.application_artifact_digest")
    for field in RUNTIME_FIELDS[1:]: _nullable_digest(value[field],f"runtime_manifest.{field}")

def validate_spg1_binding(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,ROOT_FIELDS,"SPG_ROOT_FIELDS_INVALID","root")
    if record["schema"]!="r8-v15-r1-spg-1-binding/v1" or not isinstance(record["schema"],str):
        raise SPG1BindingError("SPG_SCHEMA_INVALID","schema const invalid")
    if not isinstance(record["status"],str) or record["status"] not in STATUS:
        raise SPG1BindingError("SPG_STATUS_INVALID","status outside frozen enum")
    if record["authority_effect"]!="NONE" or not isinstance(record["authority_effect"],str):
        raise SPG1BindingError("SPG_AUTHORITY_EFFECT_INVALID","authority_effect must be NONE")
    _string(record["generator_id"],"generator_id"); _string(record["generator_artifact_path"],"generator_artifact_path")
    _digest(record["generator_artifact_sha256"],"generator_artifact_sha256")
    _runtime(record["runtime_manifest"])
    _nullable_digest(record["workload_attestation_policy_digest"],"workload_attestation_policy_digest")
    _nullable_digest(record["workload_attestation_proof_digest"],"workload_attestation_proof_digest")
    _string_array(record["allowed_input_design_artifacts"],"allowed_input_design_artifacts")
    _string_array(record["allowed_output_schema_classes"],"allowed_output_schema_classes")
    if record["signing_credential_id"] is not None: _string(record["signing_credential_id"],"signing_credential_id")
    if not isinstance(record["revocation_state"],str) or record["revocation_state"] not in REVOCATION:
        raise SPG1BindingError("SPG_REVOCATION_INVALID","revocation_state outside frozen enum")
    if not isinstance(record["qualification_status"],str) or record["qualification_status"] not in QUALIFICATION:
        raise SPG1BindingError("SPG_QUALIFICATION_INVALID","qualification_status outside frozen enum")
    return {"locally_valid":True,"validation_scope":"LOCAL_SPG1_BINDING_FAMILY_STRUCTURE_ONLY","authority_effect":"NONE","generator_qualification_verified":False,"workload_attestation_verified":False,"artifact_authenticity_verified":False,"runtime_manifest_verified":False,"revocation_current":False,"final_freeze_eligibility_verified":False,"signing_authority_verified":False,"runtime_qualified":False,"terminal_authority":False}
