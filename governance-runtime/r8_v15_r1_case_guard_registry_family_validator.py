"""R8 v15-r1 Slice 36: composite CaseRegistry + GuardRegistry structural validation only."""
from __future__ import annotations
import json, re
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

CASE_ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","source_versions","case_count","guard_referenced_case_count","missing_guard_referenced_cases","duplicate_conflicts","cases")
GUARD_ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","registry_range","records")
CASE_SOURCE_FIELDS=("version","commit","blob")
CASE_FIELDS=("case_id","text","source_version","source_commit","source_blob")
GUARD_RECORD_FIELDS=("guard_id","mechanism_id","positive_case_ids","negative_cases","canonical_source","activation_sequence","lifecycle_state")
NEGATIVE_FIELDS=("case_id","fault_proof_class")
V_RE=re.compile(r"^v[0-9]+$")
CASE_RE=re.compile(r"^V[0-9]+-[0-9]{3}$")
GUARD_RE=re.compile(r"^G(?:0(?:0[1-9]|[1-9][0-9])|1(?:[0-4][0-9]|5[0-6]))$")
FP_RE=re.compile(r"^FP[0-6]$")

class RegistryFamilyError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _gcp_string(value:Any,label:str)->None:
    if not isinstance(value,str) or not value:
        raise RegistryFamilyError("REGISTRY_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise RegistryFamilyError("REGISTRY_GCP_INVALID",f"{label}: {exc}") from exc

def _exact(value:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping) or len(value)!=len(fields) or set(value.keys())!=set(fields):
        raise RegistryFamilyError(code,f"{label} field set invalid")
    return value

def _empty_array(value:Any,label:str)->None:
    if not isinstance(value,list) or value:
        raise RegistryFamilyError("REGISTRY_EMPTY_ARRAY_INVALID",f"{label} must be empty array")

def _case_record(value:Any,index:int)->None:
    value=_exact(value,CASE_FIELDS,"CASE_RECORD_FIELD_SET_INVALID",f"cases[{index}]")
    cid=value["case_id"]
    if not isinstance(cid,str) or CASE_RE.fullmatch(cid) is None:
        raise RegistryFamilyError("CASE_ID_INVALID",f"cases[{index}].case_id invalid")
    _gcp_string(value["text"],f"cases[{index}].text")
    sv=value["source_version"]
    if not isinstance(sv,str) or V_RE.fullmatch(sv) is None:
        raise RegistryFamilyError("CASE_SOURCE_VERSION_INVALID",f"cases[{index}].source_version invalid")
    _gcp_string(value["source_commit"],f"cases[{index}].source_commit")
    _gcp_string(value["source_blob"],f"cases[{index}].source_blob")

def validate_case_registry(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,CASE_ROOT_FIELDS,"CASE_REGISTRY_FIELD_SET_INVALID","CaseRegistry")
    _gcp_string(record["schema"],"schema"); _gcp_string(record["status"],"status")
    if record["authority_effect"]!="NONE" or not isinstance(record["authority_effect"],str):
        raise RegistryFamilyError("CASE_AUTHORITY_EFFECT_INVALID","authority_effect must be NONE")
    sources=record["source_versions"]
    if not isinstance(sources,list):
        raise RegistryFamilyError("CASE_SOURCE_VERSIONS_INVALID","source_versions must be array")
    for i,item in enumerate(sources):
        item=_exact(item,CASE_SOURCE_FIELDS,"CASE_SOURCE_FIELD_SET_INVALID",f"source_versions[{i}]")
        if not isinstance(item["version"],str) or V_RE.fullmatch(item["version"]) is None:
            raise RegistryFamilyError("CASE_SOURCE_VERSION_INVALID",f"source_versions[{i}].version invalid")
        _gcp_string(item["commit"],f"source_versions[{i}].commit")
        _gcp_string(item["blob"],f"source_versions[{i}].blob")
    if type(record["case_count"]) is not int or record["case_count"]!=467:
        raise RegistryFamilyError("CASE_COUNT_INVALID","case_count must be exact integer 467")
    grc=record["guard_referenced_case_count"]
    if isinstance(grc,bool) or not isinstance(grc,int) or grc<0:
        raise RegistryFamilyError("CASE_GUARD_REFERENCED_COUNT_INVALID","guard_referenced_case_count must be integer >=0")
    _empty_array(record["missing_guard_referenced_cases"],"missing_guard_referenced_cases")
    _empty_array(record["duplicate_conflicts"],"duplicate_conflicts")
    cases=record["cases"]
    if not isinstance(cases,list) or len(cases)!=467:
        raise RegistryFamilyError("CASE_RECORD_COUNT_INVALID","cases must contain exactly 467 items")
    for i,item in enumerate(cases): _case_record(item,i)
    return {"locally_valid":True,"validation_scope":"LOCAL_CASE_REGISTRY_STRUCTURE_ONLY","authority_effect":"NONE","case_identity_uniqueness_verified":False,"cross_registry_references_verified":False,"registry_authority_granted":False,"currentness_verified":False,"terminal_authority":False}

def _negative(value:Any,label:str)->None:
    value=_exact(value,NEGATIVE_FIELDS,"GUARD_NEGATIVE_FIELD_SET_INVALID",label)
    if not isinstance(value["case_id"],str) or CASE_RE.fullmatch(value["case_id"]) is None:
        raise RegistryFamilyError("GUARD_NEGATIVE_CASE_ID_INVALID",f"{label}.case_id invalid")
    if not isinstance(value["fault_proof_class"],str) or FP_RE.fullmatch(value["fault_proof_class"]) is None:
        raise RegistryFamilyError("GUARD_FAULT_PROOF_CLASS_INVALID",f"{label}.fault_proof_class invalid")

def _guard_record(value:Any,index:int)->None:
    value=_exact(value,GUARD_RECORD_FIELDS,"GUARD_RECORD_FIELD_SET_INVALID",f"records[{index}]")
    gid=value["guard_id"]
    if not isinstance(gid,str) or GUARD_RE.fullmatch(gid) is None:
        raise RegistryFamilyError("GUARD_ID_INVALID",f"records[{index}].guard_id invalid")
    _gcp_string(value["mechanism_id"],f"records[{index}].mechanism_id")
    positives=value["positive_case_ids"]
    if not isinstance(positives,list) or not positives:
        raise RegistryFamilyError("GUARD_POSITIVE_CASES_INVALID",f"records[{index}].positive_case_ids must be non-empty array")
    for j,cid in enumerate(positives):
        if not isinstance(cid,str) or CASE_RE.fullmatch(cid) is None:
            raise RegistryFamilyError("GUARD_POSITIVE_CASE_ID_INVALID",f"records[{index}].positive_case_ids[{j}] invalid")
    if len(set(positives))!=len(positives):
        raise RegistryFamilyError("GUARD_POSITIVE_CASES_NOT_UNIQUE",f"records[{index}].positive_case_ids uniqueItems violated")
    negatives=value["negative_cases"]
    if not isinstance(negatives,list) or not negatives:
        raise RegistryFamilyError("GUARD_NEGATIVE_CASES_INVALID",f"records[{index}].negative_cases must be non-empty array")
    for j,item in enumerate(negatives): _negative(item,f"records[{index}].negative_cases[{j}]")
    source=value["canonical_source"]
    if not isinstance(source,Mapping) or len(source)<1:
        raise RegistryFamilyError("GUARD_CANONICAL_SOURCE_INVALID",f"records[{index}].canonical_source must be non-empty object")
    _gcp_string(value["activation_sequence"],f"records[{index}].activation_sequence")
    if value["lifecycle_state"]!="ACTIVE" or not isinstance(value["lifecycle_state"],str):
        raise RegistryFamilyError("GUARD_LIFECYCLE_INVALID",f"records[{index}].lifecycle_state must be ACTIVE")

def validate_guard_registry(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise RegistryFamilyError("GUARD_REGISTRY_FIELD_SET_INVALID","GuardRegistry must be mapping")
    allowed=set(GUARD_ROOT_FIELDS)|{"seed_catalog","v13_design","v14_design","v15_design"}
    if not set(record.keys()).issubset(allowed) or not set(GUARD_ROOT_FIELDS).issubset(record.keys()):
        raise RegistryFamilyError("GUARD_REGISTRY_FIELD_SET_INVALID","GuardRegistry required/additional properties invalid")
    _gcp_string(record["schema"],"schema"); _gcp_string(record["status"],"status")
    if record["authority_effect"]!="NONE" or not isinstance(record["authority_effect"],str):
        raise RegistryFamilyError("GUARD_AUTHORITY_EFFECT_INVALID","authority_effect must be NONE")
    if record["registry_range"]!="G001-G156" or not isinstance(record["registry_range"],str):
        raise RegistryFamilyError("GUARD_RANGE_INVALID","registry_range const invalid")
    if "seed_catalog" in record and not (record["seed_catalog"] is None or isinstance(record["seed_catalog"],(Mapping,str))):
        raise RegistryFamilyError("GUARD_SEED_CATALOG_INVALID","seed_catalog type invalid")
    for field in ("v13_design","v14_design","v15_design"):
        if field in record and not (record[field] is None or isinstance(record[field],Mapping)):
            raise RegistryFamilyError("GUARD_DESIGN_INVALID",f"{field} type invalid")
    records=record["records"]
    if not isinstance(records,list) or len(records)!=156:
        raise RegistryFamilyError("GUARD_RECORD_COUNT_INVALID","records must contain exactly 156 items")
    for i,item in enumerate(records): _guard_record(item,i)
    return {"locally_valid":True,"validation_scope":"LOCAL_GUARD_REGISTRY_STRUCTURE_ONLY","authority_effect":"NONE","guard_identity_uniqueness_verified":False,"cross_registry_references_verified":False,"registry_authority_granted":False,"currentness_verified":False,"terminal_authority":False}
