"""R8 v15-r1 Slice 38: composite GCP-RVM-2 structural validation only."""
from __future__ import annotations
import json, re
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","canonical_vectors","rejection_vectors","canonicalization_rules")
CANON_FIELDS=("vector_id","input_representation","schema_context","expected_canonical_utf8","expected_sha256","source_rules")
REJECT_FIELDS=("vector_id","input_representation","schema_context","expected_outcome","expected_rejection_code","source_case_id","source_rules")
POS_ID_RE=re.compile(r"^GCP-RVM2-P[0-9]{2}$")
REJ_ID_RE=re.compile(r"^GCP-RVM2-R[0-9]{2}$")
DIGEST_RE=re.compile(r"^[0-9a-f]{64}$")
REJECT_CODE_RE=re.compile(r"^GCP_REJECT_[A-Z0-9_]+$")
CASE_RE=re.compile(r"^V[0-9]+-[0-9]{3}$")

class GCPRVM2Error(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact(value:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping) or len(value)!=len(fields) or set(value.keys())!=set(fields):
        raise GCPRVM2Error(code,f"{label} field set invalid")
    return value

def _nonempty(value:Any,label:str)->None:
    if not isinstance(value,str) or not value:
        raise GCPRVM2Error("GCP_RVM_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise GCPRVM2Error("GCP_RVM_GCP_INVALID",f"{label}: {exc}") from exc

def _digest(value:Any,label:str)->None:
    if not isinstance(value,str) or DIGEST_RE.fullmatch(value) is None:
        raise GCPRVM2Error("GCP_RVM_DIGEST_INVALID",f"{label} invalid SHA-256")

def _source_rules(value:Any,label:str)->None:
    if not isinstance(value,list) or not value:
        raise GCPRVM2Error("GCP_RVM_SOURCE_RULES_INVALID",f"{label} must be non-empty list")
    for i,item in enumerate(value): _nonempty(item,f"{label}[{i}]")
    if len(set(value))!=len(value):
        raise GCPRVM2Error("GCP_RVM_SOURCE_RULES_NOT_UNIQUE",f"{label} uniqueItems violated")

def _json_unique(value:list[Any],label:str)->None:
    keys=[json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False) for v in value]
    if len(set(keys))!=len(keys):
        raise GCPRVM2Error("GCP_RVM_UNIQUE_ITEMS_VIOLATION",f"{label} uniqueItems violated")

def _canonical(value:Any,index:int)->None:
    value=_exact(value,CANON_FIELDS,"GCP_RVM_CANON_FIELDS_INVALID",f"canonical_vectors[{index}]")
    if not isinstance(value["vector_id"],str) or POS_ID_RE.fullmatch(value["vector_id"]) is None:
        raise GCPRVM2Error("GCP_RVM_POS_ID_INVALID",f"canonical_vectors[{index}].vector_id invalid")
    if not isinstance(value["input_representation"],str) or not isinstance(value["expected_canonical_utf8"],str):
        raise GCPRVM2Error("GCP_RVM_PAYLOAD_STRING_INVALID",f"canonical_vectors[{index}] payload fields must be strings")
    _nonempty(value["schema_context"],f"canonical_vectors[{index}].schema_context")
    _digest(value["expected_sha256"],f"canonical_vectors[{index}].expected_sha256")
    _source_rules(value["source_rules"],f"canonical_vectors[{index}].source_rules")

def _rejection(value:Any,index:int)->None:
    value=_exact(value,REJECT_FIELDS,"GCP_RVM_REJECT_FIELDS_INVALID",f"rejection_vectors[{index}]")
    if not isinstance(value["vector_id"],str) or REJ_ID_RE.fullmatch(value["vector_id"]) is None:
        raise GCPRVM2Error("GCP_RVM_REJ_ID_INVALID",f"rejection_vectors[{index}].vector_id invalid")
    if not isinstance(value["input_representation"],str):
        raise GCPRVM2Error("GCP_RVM_INPUT_STRING_INVALID",f"rejection_vectors[{index}].input_representation must be string")
    _nonempty(value["schema_context"],f"rejection_vectors[{index}].schema_context")
    if value["expected_outcome"]!="REJECT" or not isinstance(value["expected_outcome"],str):
        raise GCPRVM2Error("GCP_RVM_OUTCOME_INVALID",f"rejection_vectors[{index}].expected_outcome invalid")
    if not isinstance(value["expected_rejection_code"],str) or REJECT_CODE_RE.fullmatch(value["expected_rejection_code"]) is None:
        raise GCPRVM2Error("GCP_RVM_REJECTION_CODE_INVALID",f"rejection_vectors[{index}].expected_rejection_code invalid")
    sci=value["source_case_id"]
    if sci is not None and (not isinstance(sci,str) or CASE_RE.fullmatch(sci) is None):
        raise GCPRVM2Error("GCP_RVM_SOURCE_CASE_INVALID",f"rejection_vectors[{index}].source_case_id invalid")
    _source_rules(value["source_rules"],f"rejection_vectors[{index}].source_rules")

def validate_gcp_rvm2_manifest(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,ROOT_FIELDS,"GCP_RVM_ROOT_FIELDS_INVALID","root")
    for field,expected in (("schema","gcp-rvm-2/v1"),("status","SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE"),("authority_effect","NONE")):
        if not isinstance(record[field],str) or record[field]!=expected:
            raise GCPRVM2Error("GCP_RVM_CONST_INVALID",f"{field} const invalid")
    canonical=record["canonical_vectors"]
    if not isinstance(canonical,list) or len(canonical)<5:
        raise GCPRVM2Error("GCP_RVM_CANONICALS_INVALID","canonical_vectors minItems 5")
    for i,item in enumerate(canonical): _canonical(item,i)
    _json_unique(canonical,"canonical_vectors")
    rejections=record["rejection_vectors"]
    if not isinstance(rejections,list) or len(rejections)<14:
        raise GCPRVM2Error("GCP_RVM_REJECTIONS_INVALID","rejection_vectors minItems 14")
    for i,item in enumerate(rejections): _rejection(item,i)
    _json_unique(rejections,"rejection_vectors")
    rules=record["canonicalization_rules"]
    if not isinstance(rules,list) or not rules:
        raise GCPRVM2Error("GCP_RVM_RULES_INVALID","canonicalization_rules must be non-empty list")
    for i,item in enumerate(rules): _nonempty(item,f"canonicalization_rules[{i}]")
    if len(set(rules))!=len(rules):
        raise GCPRVM2Error("GCP_RVM_RULES_NOT_UNIQUE","canonicalization_rules uniqueItems violated")
    return {"locally_valid":True,"validation_scope":"LOCAL_GCP_RVM2_FAMILY_STRUCTURE_ONLY","authority_effect":"NONE","canonicalization_executed":False,"digest_recomputed":False,"rejection_vectors_executed":False,"diagnostic_semantics_verified":False,"source_case_exists_verified":False,"terminal_authority":False}
