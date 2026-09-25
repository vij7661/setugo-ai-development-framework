"""R8 v15-r1 Slice 31: local ReviewPresentationSchema root validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("schema","status","authority_effect","unknown_display_field_default","packet_types")
PACKET_FIELDS=("packet_type_id","fields","ordering_semantic","evidence_association_semantic")
FIELD_RULE_FIELDS=("field_id","classification","conditions","source_rules")
CLASSIFICATIONS={"REVIEW_SEMANTIC","DISPLAY_NON_SEMANTIC"}
SCHEMA_CONST="r8-v15-r1-rps-1/v1"
STATUS_CONST="SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE"
AUTHORITY_CONST="NONE"
UNKNOWN_DEFAULT_CONST="REVIEW_SEMANTIC"

class ReviewPresentationSchemaError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise ReviewPresentationSchemaError("RPS_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ReviewPresentationSchemaError("RPS_GCP_INVALID",f"{field}: {exc}") from exc

def _field_rule(rule:Any,label:str)->None:
    if not isinstance(rule,Mapping):
        raise ReviewPresentationSchemaError("RPS_FIELD_RULE_INVALID",f"{label} must be mapping")
    if len(rule)!=len(FIELD_RULE_FIELDS) or set(rule.keys())!=set(FIELD_RULE_FIELDS):
        raise ReviewPresentationSchemaError("RPS_FIELD_RULE_INVALID",f"{label} field set invalid")
    _string(rule["field_id"],label+".field_id")
    if not isinstance(rule["classification"],str) or rule["classification"] not in CLASSIFICATIONS:
        raise ReviewPresentationSchemaError("RPS_CLASSIFICATION_INVALID",f"{label}.classification invalid")
    conditions=rule["conditions"]
    if not isinstance(conditions,list):
        raise ReviewPresentationSchemaError("RPS_CONDITIONS_INVALID",f"{label}.conditions must be list")
    for i,v in enumerate(conditions): _string(v,f"{label}.conditions[{i}]")
    sources=rule["source_rules"]
    if not isinstance(sources,list) or not sources:
        raise ReviewPresentationSchemaError("RPS_SOURCE_RULES_INVALID",f"{label}.source_rules must be non-empty list")
    for i,v in enumerate(sources): _string(v,f"{label}.source_rules[{i}]")
    if len(set(sources))!=len(sources):
        raise ReviewPresentationSchemaError("RPS_SOURCE_RULES_NOT_UNIQUE",f"{label}.source_rules must be unique")

def _packet(packet:Any,index:int)->None:
    if not isinstance(packet,Mapping):
        raise ReviewPresentationSchemaError("RPS_PACKET_INVALID",f"packet_types[{index}] must be mapping")
    if len(packet)!=len(PACKET_FIELDS) or set(packet.keys())!=set(PACKET_FIELDS):
        raise ReviewPresentationSchemaError("RPS_PACKET_INVALID",f"packet_types[{index}] field set invalid")
    _string(packet["packet_type_id"],f"packet_types[{index}].packet_type_id")
    fields=packet["fields"]
    if not isinstance(fields,list) or not fields:
        raise ReviewPresentationSchemaError("RPS_PACKET_FIELDS_INVALID",f"packet_types[{index}].fields must be non-empty list")
    for j,rule in enumerate(fields): _field_rule(rule,f"packet_types[{index}].fields[{j}]")
    keys=[json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")) for v in fields]
    if len(set(keys))!=len(keys):
        raise ReviewPresentationSchemaError("RPS_PACKET_FIELDS_NOT_UNIQUE",f"packet_types[{index}].fields uniqueItems violated")
    for name in ("ordering_semantic","evidence_association_semantic"):
        if type(packet[name]) is not bool or packet[name] is not True:
            raise ReviewPresentationSchemaError("RPS_PACKET_TRUE_CONST_INVALID",f"packet_types[{index}].{name} must be exact true")

def validate_review_presentation_schema(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise ReviewPresentationSchemaError("RPS_FIELD_SET_INVALID","record must be mapping")
    if len(record)!=len(FIELDS) or set(record.keys())!=set(FIELDS):
        raise ReviewPresentationSchemaError("RPS_FIELD_SET_INVALID","top-level field set invalid")
    consts=(("schema",SCHEMA_CONST),("status",STATUS_CONST),("authority_effect",AUTHORITY_CONST),("unknown_display_field_default",UNKNOWN_DEFAULT_CONST))
    for field,expected in consts:
        if not isinstance(record[field],str) or record[field]!=expected:
            raise ReviewPresentationSchemaError("RPS_CONST_INVALID",f"{field} must equal frozen const")
    packets=record["packet_types"]
    if not isinstance(packets,list) or not packets:
        raise ReviewPresentationSchemaError("RPS_PACKET_TYPES_INVALID","packet_types must be non-empty list")
    for i,packet in enumerate(packets): _packet(packet,i)
    return {"locally_valid":True,"packet_type_count":len(packets),"validation_scope":"LOCAL_REVIEW_PRESENTATION_SCHEMA_STRUCTURE_ONLY","authority_effect":"NONE","unknown_field_materiality_enforced":False,"presentation_enforced":False,"reviewer_independence_verified":False,"review_authority_granted":False,"runtime_qualified":False,"terminal_authority":False}
