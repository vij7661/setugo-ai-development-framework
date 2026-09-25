"""R8 v15-r1 Slice 35: composite SPM-1 provenance-family structural validation only."""
from __future__ import annotations
import json, re
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","semantic_candidate_commit","generator","artifact_count","entry_count","source_ref_catalog","artifacts","entries","coverage")
GENERATOR_FIELDS: Tuple[str,...]=("generator_id","generator_artifact_path","generator_artifact_sha256","runtime_manifest_digest","workload_attestation_proof_digest","qualification_status")
ARTIFACT_FIELDS=("artifact_id","path","git_blob_sha1","sha256")
SOURCE_REF_FIELDS=("design_id","path","commit","blob")
ENTRY_FIELDS=("artifact_id","artifact_sha256","json_pointer","semantic_purpose","source_design_ids","source_ref_ids","generator_id","generator_runtime_manifest_digest","reviewer_status")
COVERAGE_FIELDS=("uncovered_semantic_elements","non_authoritative_only_sources","conflicting_entries")
STATUS={"SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE","FINAL_FREEZE_ELIGIBLE"}
QUALIFICATION={"QUALIFIED","UNATTESTED_RUNTIME","REVOKED","DRIFTED","UNREGISTERED"}
DIGEST_RE=re.compile(r"^[0-9a-f]{64}$")
BLOB_RE=re.compile(r"^[0-9a-f]{40}$")

class SPM1Error(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact_mapping(value:Any,fields:Tuple[str,...]|tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping):
        raise SPM1Error(code,f"{label} must be mapping")
    if len(value)!=len(fields) or set(value.keys())!=set(fields):
        raise SPM1Error(code,f"{label} field set invalid")
    return value

def _gcp_string(value:Any,label:str)->str:
    if not isinstance(value,str) or not value:
        raise SPM1Error("SPM_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise SPM1Error("SPM_GCP_INVALID",f"{label}: {exc}") from exc
    return value

def _digest(value:Any,label:str)->None:
    if not isinstance(value,str) or DIGEST_RE.fullmatch(value) is None:
        raise SPM1Error("SPM_DIGEST_INVALID",f"{label} must be lowercase hex SHA-256")

def _nullable_digest(value:Any,label:str)->None:
    if value is not None: _digest(value,label)

def _unique_json(items:list[Any],label:str)->None:
    try:
        keys=[json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False) for v in items]
    except (TypeError,ValueError) as exc:
        raise SPM1Error("SPM_JSON_VALUE_INVALID",f"{label}: {exc}") from exc
    if len(set(keys))!=len(keys):
        raise SPM1Error("SPM_UNIQUE_ITEMS_VIOLATION",f"{label} must be unique by JSON value")

def _generator(value:Any)->None:
    value=_exact_mapping(value,GENERATOR_FIELDS,"SPM_GENERATOR_FIELD_SET_INVALID","generator")
    _gcp_string(value["generator_id"],"generator.generator_id")
    _gcp_string(value["generator_artifact_path"],"generator.generator_artifact_path")
    _digest(value["generator_artifact_sha256"],"generator.generator_artifact_sha256")
    _nullable_digest(value["runtime_manifest_digest"],"generator.runtime_manifest_digest")
    _nullable_digest(value["workload_attestation_proof_digest"],"generator.workload_attestation_proof_digest")
    if not isinstance(value["qualification_status"],str) or value["qualification_status"] not in QUALIFICATION:
        raise SPM1Error("SPM_GENERATOR_QUALIFICATION_INVALID","generator.qualification_status outside frozen enum")

def _artifact(value:Any,index:int)->None:
    value=_exact_mapping(value,ARTIFACT_FIELDS,"SPM_ARTIFACT_FIELD_SET_INVALID",f"artifacts[{index}]")
    _gcp_string(value["artifact_id"],f"artifacts[{index}].artifact_id")
    _gcp_string(value["path"],f"artifacts[{index}].path")
    if not isinstance(value["git_blob_sha1"],str) or BLOB_RE.fullmatch(value["git_blob_sha1"]) is None:
        raise SPM1Error("SPM_GIT_BLOB_INVALID",f"artifacts[{index}].git_blob_sha1 invalid")
    _digest(value["sha256"],f"artifacts[{index}].sha256")

def _source_ref(value:Any,label:str)->None:
    value=_exact_mapping(value,SOURCE_REF_FIELDS,"SPM_SOURCE_REF_FIELD_SET_INVALID",label)
    for field in SOURCE_REF_FIELDS: _gcp_string(value[field],f"{label}.{field}")

def _unique_nonempty_strings(value:Any,label:str)->None:
    if not isinstance(value,list) or not value:
        raise SPM1Error("SPM_STRING_LIST_INVALID",f"{label} must be non-empty list")
    for i,v in enumerate(value): _gcp_string(v,f"{label}[{i}]")
    if len(set(value))!=len(value):
        raise SPM1Error("SPM_STRING_LIST_NOT_UNIQUE",f"{label} must be unique")

def _entry(value:Any,index:int)->None:
    value=_exact_mapping(value,ENTRY_FIELDS,"SPM_ENTRY_FIELD_SET_INVALID",f"entries[{index}]")
    _gcp_string(value["artifact_id"],f"entries[{index}].artifact_id")
    _digest(value["artifact_sha256"],f"entries[{index}].artifact_sha256")
    if not isinstance(value["json_pointer"],str) or not value["json_pointer"].startswith("/"):
        raise SPM1Error("SPM_JSON_POINTER_INVALID",f"entries[{index}].json_pointer must match ^/")
    _gcp_string(value["semantic_purpose"],f"entries[{index}].semantic_purpose")
    _unique_nonempty_strings(value["source_design_ids"],f"entries[{index}].source_design_ids")
    _unique_nonempty_strings(value["source_ref_ids"],f"entries[{index}].source_ref_ids")
    _gcp_string(value["generator_id"],f"entries[{index}].generator_id")
    _nullable_digest(value["generator_runtime_manifest_digest"],f"entries[{index}].generator_runtime_manifest_digest")
    if not isinstance(value["reviewer_status"],str) or value["reviewer_status"] not in {"NOT_YET_REVIEWED","REVIEW_REQUIRED","REVIEWED"}:
        raise SPM1Error("SPM_REVIEWER_STATUS_INVALID",f"entries[{index}].reviewer_status invalid")

def validate_spm1_manifest(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact_mapping(record,ROOT_FIELDS,"SPM_ROOT_FIELD_SET_INVALID","root")
    if record["schema"]!="r8-v15-r1-spm-1/v1" or not isinstance(record["schema"],str):
        raise SPM1Error("SPM_SCHEMA_CONST_INVALID","schema const invalid")
    if not isinstance(record["status"],str) or record["status"] not in STATUS:
        raise SPM1Error("SPM_STATUS_INVALID","status outside frozen enum")
    if record["authority_effect"]!="NONE" or not isinstance(record["authority_effect"],str):
        raise SPM1Error("SPM_AUTHORITY_EFFECT_INVALID","authority_effect must be NONE")
    if record["semantic_candidate_commit"]!="c721b38cf8b00294797300b526596ce723a47ff8" or not isinstance(record["semantic_candidate_commit"],str):
        raise SPM1Error("SPM_SEMANTIC_COMMIT_INVALID","semantic_candidate_commit const invalid")
    _generator(record["generator"])
    for field in ("artifact_count","entry_count"):
        value=record[field]
        if isinstance(value,bool) or not isinstance(value,int) or value<1:
            raise SPM1Error("SPM_COUNT_INVALID",f"{field} must be integer >=1")
    artifacts=record["artifacts"]
    if not isinstance(artifacts,list) or not artifacts:
        raise SPM1Error("SPM_ARTIFACTS_INVALID","artifacts must be non-empty list")
    for i,v in enumerate(artifacts): _artifact(v,i)
    _unique_json(artifacts,"artifacts")
    entries=record["entries"]
    if not isinstance(entries,list) or not entries:
        raise SPM1Error("SPM_ENTRIES_INVALID","entries must be non-empty list")
    for i,v in enumerate(entries): _entry(v,i)
    coverage=_exact_mapping(record["coverage"],COVERAGE_FIELDS,"SPM_COVERAGE_FIELD_SET_INVALID","coverage")
    for field in COVERAGE_FIELDS:
        if not isinstance(coverage[field],list) or coverage[field]:
            raise SPM1Error("SPM_COVERAGE_INVALID",f"coverage.{field} must be empty array")
    catalog=record["source_ref_catalog"]
    if not isinstance(catalog,Mapping) or len(catalog)<1:
        raise SPM1Error("SPM_SOURCE_CATALOG_INVALID","source_ref_catalog must be non-empty object")
    for key,value in catalog.items():
        if not isinstance(key,str):
            raise SPM1Error("SPM_SOURCE_CATALOG_KEY_INVALID","source_ref_catalog keys must be strings")
        _source_ref(value,f"source_ref_catalog[{key!r}]")
    return {"locally_valid":True,"validation_scope":"LOCAL_SPM1_FAMILY_STRUCTURE_ONLY","authority_effect":"NONE","source_ref_binding_verified":False,"count_correspondence_verified":False,"generator_qualification_verified":False,"final_freeze_eligibility_verified":False,"artifact_digests_verified":False,"source_authority_verified":False,"provenance_semantics_verified":False,"evidence_promotion_authorized":False,"runtime_qualified":False,"terminal_authority":False}
