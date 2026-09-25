"""R8 v15-r1 Slice 37: composite Guard-Omission evidence + manifest structural validation only."""
from __future__ import annotations
import json, re
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

EVIDENCE_ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","semantic_candidate_commit","purpose","digest_contract","record_count","all_guard_sets_equal","all_case_sets_equal","records")
MANIFEST_ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","current_guard_registry","current_case_registry","omitted_table_count","invalid_omission_count","validation_contract","omitted_tables","reverification","legacy_note")
DIGEST_CONTRACT_FIELDS=("algorithm","text_encoding","line_separator","trailing_line_separator_added","digest_field","verification_instruction")
EVIDENCE_RECORD_FIELDS=("source_version","source_path","source_commit","source_blob","line_start","line_end","digest_basis","raw_section_sha256","raw_section_bytes","parsed_guard_ids","parsed_case_ids","manifest_guard_ids","manifest_case_ids","verification","excerpt")
VERIFICATION_FIELDS=("guard_set_equal","case_set_equal","missing_guard_ids","extra_guard_ids","missing_case_ids","extra_case_ids")
MANIFEST_RECORD_FIELDS=("source_version","source_path","source_commit","source_blob","line_start","line_end","raw_section_sha256","raw_section_bytes","guard_ids","referenced_case_ids","parsed_source_guard_set_equals_manifest_set","parsed_source_case_set_equals_manifest_set","all_guard_ids_in_current_registry","all_referenced_case_ids_in_current_case_registry","missing_guard_ids","extra_guard_ids","missing_case_ids","extra_case_ids","evidence_record_index")
VERSION_RE=re.compile(r"^v[0-9]+$")
GUARD_RE=re.compile(r"^G[0-9]{3}$")
CASE_RE=re.compile(r"^V[0-9]+-[0-9]{3}$")
DIGEST_RE=re.compile(r"^[0-9a-f]{64}$")

class GuardOmissionFamilyError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact(value:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping) or len(value)!=len(fields) or set(value.keys())!=set(fields):
        raise GuardOmissionFamilyError(code,f"{label} field set invalid")
    return value

def _string(value:Any,label:str)->None:
    if not isinstance(value,str) or not value:
        raise GuardOmissionFamilyError("GO_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise GuardOmissionFamilyError("GO_GCP_INVALID",f"{label}: {exc}") from exc

def _positive_int(value:Any,label:str)->None:
    if isinstance(value,bool) or not isinstance(value,int) or value<1:
        raise GuardOmissionFamilyError("GO_POSITIVE_INTEGER_INVALID",f"{label} must be integer >=1")

def _digest(value:Any,label:str)->None:
    if not isinstance(value,str) or DIGEST_RE.fullmatch(value) is None:
        raise GuardOmissionFamilyError("GO_DIGEST_INVALID",f"{label} invalid SHA-256")

def _id_list(value:Any,label:str,pattern:re.Pattern[str])->None:
    if not isinstance(value,list) or not value:
        raise GuardOmissionFamilyError("GO_ID_LIST_INVALID",f"{label} must be non-empty list")
    for i,item in enumerate(value):
        if not isinstance(item,str) or pattern.fullmatch(item) is None:
            raise GuardOmissionFamilyError("GO_ID_INVALID",f"{label}[{i}] invalid")
    if len(set(value))!=len(value):
        raise GuardOmissionFamilyError("GO_ID_LIST_NOT_UNIQUE",f"{label} uniqueItems violated")

def _empty(value:Any,label:str)->None:
    if not isinstance(value,list) or value:
        raise GuardOmissionFamilyError("GO_EMPTY_ARRAY_INVALID",f"{label} must be empty array")

def _evidence_record(value:Any,index:int)->None:
    value=_exact(value,EVIDENCE_RECORD_FIELDS,"GO_EVIDENCE_RECORD_FIELDS_INVALID",f"records[{index}]")
    if not isinstance(value["source_version"],str) or VERSION_RE.fullmatch(value["source_version"]) is None:
        raise GuardOmissionFamilyError("GO_SOURCE_VERSION_INVALID",f"records[{index}].source_version invalid")
    for field in ("source_path","source_commit","source_blob","digest_basis","excerpt"): _string(value[field],f"records[{index}].{field}")
    _positive_int(value["line_start"],f"records[{index}].line_start"); _positive_int(value["line_end"],f"records[{index}].line_end")
    _digest(value["raw_section_sha256"],f"records[{index}].raw_section_sha256")
    _positive_int(value["raw_section_bytes"],f"records[{index}].raw_section_bytes")
    _id_list(value["parsed_guard_ids"],f"records[{index}].parsed_guard_ids",GUARD_RE)
    _id_list(value["parsed_case_ids"],f"records[{index}].parsed_case_ids",CASE_RE)
    _id_list(value["manifest_guard_ids"],f"records[{index}].manifest_guard_ids",GUARD_RE)
    _id_list(value["manifest_case_ids"],f"records[{index}].manifest_case_ids",CASE_RE)
    ver=_exact(value["verification"],VERIFICATION_FIELDS,"GO_VERIFICATION_FIELDS_INVALID",f"records[{index}].verification")
    for field in ("guard_set_equal","case_set_equal"):
        if type(ver[field]) is not bool or ver[field] is not True:
            raise GuardOmissionFamilyError("GO_VERIFICATION_TRUE_INVALID",f"records[{index}].verification.{field} must be true")
    for field in ("missing_guard_ids","extra_guard_ids","missing_case_ids","extra_case_ids"): _empty(ver[field],f"records[{index}].verification.{field}")

def validate_guard_omission_source_evidence(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,EVIDENCE_ROOT_FIELDS,"GO_EVIDENCE_ROOT_FIELDS_INVALID","evidence root")
    consts={"schema":"r8-v15-r1-guard-omission-source-evidence/v1","status":"REVIEW_EVIDENCE_NON_AUTHORITATIVE","authority_effect":"NONE","semantic_candidate_commit":"c721b38cf8b00294797300b526596ce723a47ff8"}
    for field,expected in consts.items():
        if not isinstance(record[field],str) or record[field]!=expected:
            raise GuardOmissionFamilyError("GO_EVIDENCE_CONST_INVALID",f"{field} const invalid")
    _string(record["purpose"],"purpose")
    dc=_exact(record["digest_contract"],DIGEST_CONTRACT_FIELDS,"GO_DIGEST_CONTRACT_FIELDS_INVALID","digest_contract")
    for field,expected in (("algorithm","SHA-256"),("text_encoding","UTF-8"),("line_separator","LF"),("digest_field","raw_section_sha256")):
        if not isinstance(dc[field],str) or dc[field]!=expected:
            raise GuardOmissionFamilyError("GO_DIGEST_CONTRACT_CONST_INVALID",f"digest_contract.{field} invalid")
    if type(dc["trailing_line_separator_added"]) is not bool or dc["trailing_line_separator_added"] is not False:
        raise GuardOmissionFamilyError("GO_DIGEST_CONTRACT_FALSE_INVALID","trailing_line_separator_added must be false")
    _string(dc["verification_instruction"],"digest_contract.verification_instruction")
    if type(record["record_count"]) is not int or record["record_count"]!=11:
        raise GuardOmissionFamilyError("GO_RECORD_COUNT_INVALID","record_count must be 11")
    for field in ("all_guard_sets_equal","all_case_sets_equal"):
        if type(record[field]) is not bool or record[field] is not True:
            raise GuardOmissionFamilyError("GO_ROOT_TRUE_INVALID",f"{field} must be true")
    records=record["records"]
    if not isinstance(records,list) or len(records)!=11:
        raise GuardOmissionFamilyError("GO_EVIDENCE_RECORDS_INVALID","records must contain exactly 11")
    for i,item in enumerate(records): _evidence_record(item,i)
    return {"locally_valid":True,"validation_scope":"LOCAL_GUARD_OMISSION_SOURCE_EVIDENCE_STRUCTURE_ONLY","authority_effect":"NONE","digest_recomputed":False,"guard_case_sets_recomputed":False,"source_exists_verified":False,"registry_membership_verified":False,"reverification_executed":False,"evidence_promotion_authorized":False,"terminal_authority":False}

def _manifest_record(value:Any,index:int)->None:
    value=_exact(value,MANIFEST_RECORD_FIELDS,"GO_MANIFEST_RECORD_FIELDS_INVALID",f"omitted_tables[{index}]")
    if not isinstance(value["source_version"],str) or VERSION_RE.fullmatch(value["source_version"]) is None:
        raise GuardOmissionFamilyError("GO_SOURCE_VERSION_INVALID",f"omitted_tables[{index}].source_version invalid")
    for field in ("source_path","source_commit","source_blob"): _string(value[field],f"omitted_tables[{index}].{field}")
    _positive_int(value["line_start"],f"omitted_tables[{index}].line_start"); _positive_int(value["line_end"],f"omitted_tables[{index}].line_end")
    _digest(value["raw_section_sha256"],f"omitted_tables[{index}].raw_section_sha256")
    _positive_int(value["raw_section_bytes"],f"omitted_tables[{index}].raw_section_bytes")
    _id_list(value["guard_ids"],f"omitted_tables[{index}].guard_ids",GUARD_RE)
    _id_list(value["referenced_case_ids"],f"omitted_tables[{index}].referenced_case_ids",CASE_RE)
    for field in ("parsed_source_guard_set_equals_manifest_set","parsed_source_case_set_equals_manifest_set","all_guard_ids_in_current_registry","all_referenced_case_ids_in_current_case_registry"):
        if type(value[field]) is not bool or value[field] is not True:
            raise GuardOmissionFamilyError("GO_MANIFEST_TRUE_INVALID",f"omitted_tables[{index}].{field} must be true")
    for field in ("missing_guard_ids","extra_guard_ids","missing_case_ids","extra_case_ids"): _empty(value[field],f"omitted_tables[{index}].{field}")
    eri=value["evidence_record_index"]
    if isinstance(eri,bool) or not isinstance(eri,int) or eri<0 or eri>10:
        raise GuardOmissionFamilyError("GO_EVIDENCE_INDEX_INVALID",f"omitted_tables[{index}].evidence_record_index invalid")

def validate_guard_omission_manifest(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,MANIFEST_ROOT_FIELDS,"GO_MANIFEST_ROOT_FIELDS_INVALID","manifest root")
    for field,expected in (("schema","guard-omission-manifest-1/v3"),("status","REVIEW_EVIDENCE_NON_AUTHORITATIVE"),("authority_effect","NONE")):
        if not isinstance(record[field],str) or record[field]!=expected:
            raise GuardOmissionFamilyError("GO_MANIFEST_CONST_INVALID",f"{field} const invalid")
    for field in ("current_guard_registry","current_case_registry","validation_contract","reverification"):
        if not isinstance(record[field],Mapping):
            raise GuardOmissionFamilyError("GO_MANIFEST_OPEN_OBJECT_INVALID",f"{field} must be object")
    if type(record["omitted_table_count"]) is not int or record["omitted_table_count"]!=11:
        raise GuardOmissionFamilyError("GO_OMITTED_COUNT_INVALID","omitted_table_count must be 11")
    if type(record["invalid_omission_count"]) is not int or record["invalid_omission_count"]!=0:
        raise GuardOmissionFamilyError("GO_INVALID_COUNT_INVALID","invalid_omission_count must be 0")
    tables=record["omitted_tables"]
    if not isinstance(tables,list) or len(tables)!=11:
        raise GuardOmissionFamilyError("GO_OMITTED_TABLES_INVALID","omitted_tables must contain exactly 11")
    for i,item in enumerate(tables): _manifest_record(item,i)
    _string(record["legacy_note"],"legacy_note")
    return {"locally_valid":True,"validation_scope":"LOCAL_GUARD_OMISSION_MANIFEST_STRUCTURE_ONLY","authority_effect":"NONE","digest_recomputed":False,"guard_case_sets_recomputed":False,"source_exists_verified":False,"registry_membership_verified":False,"reverification_executed":False,"evidence_promotion_authorized":False,"terminal_authority":False}
