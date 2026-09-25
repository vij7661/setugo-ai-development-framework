"""R8 v15-r1 Slice 30: local ReviewPresentation PacketType validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("packet_type_id","fields","ordering_semantic","evidence_association_semantic")
FIELD_RULE_FIELDS: Tuple[str,...]=("field_id","classification","conditions","source_rules")
CLASSIFICATIONS={"REVIEW_SEMANTIC","DISPLAY_NON_SEMANTIC"}

class ReviewPacketTypeError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise ReviewPacketTypeError("REVIEW_PACKET_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ReviewPacketTypeError("REVIEW_PACKET_GCP_INVALID",f"{field}: {exc}") from exc

def _field_rule(rule:Any,index:int)->None:
    if not isinstance(rule,Mapping):
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_RULE_INVALID",f"fields[{index}] must be mapping")
    actual=set(rule.keys()); expected=set(FIELD_RULE_FIELDS)
    if len(rule)!=len(FIELD_RULE_FIELDS) or actual!=expected:
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_RULE_INVALID",f"fields[{index}] field set invalid")
    _string(rule["field_id"],f"fields[{index}].field_id")
    c=rule["classification"]
    if not isinstance(c,str) or c not in CLASSIFICATIONS:
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_CLASSIFICATION_INVALID",f"fields[{index}] classification invalid")
    conditions=rule["conditions"]
    if not isinstance(conditions,list):
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_CONDITIONS_INVALID",f"fields[{index}].conditions must be list")
    for j,v in enumerate(conditions): _string(v,f"fields[{index}].conditions[{j}]")
    sources=rule["source_rules"]
    if not isinstance(sources,list) or not sources:
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_SOURCE_RULES_INVALID",f"fields[{index}].source_rules must be non-empty list")
    for j,v in enumerate(sources): _string(v,f"fields[{index}].source_rules[{j}]")
    if len(set(sources))!=len(sources):
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_SOURCE_RULES_NOT_UNIQUE",f"fields[{index}].source_rules must be unique")

def _json_key(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def validate_review_packet_type(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(FIELDS)
    if len(record)!=len(FIELDS) or actual!=expected:
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    _string(record["packet_type_id"],"packet_type_id")
    fields=record["fields"]
    if not isinstance(fields,list) or not fields:
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELDS_INVALID","fields must be non-empty list")
    for i,rule in enumerate(fields): _field_rule(rule,i)
    keys=[_json_key(v) for v in fields]
    if len(set(keys))!=len(keys):
        raise ReviewPacketTypeError("REVIEW_PACKET_FIELDS_NOT_UNIQUE","fields uniqueItems violated")
    for name in ("ordering_semantic","evidence_association_semantic"):
        if type(record[name]) is not bool or record[name] is not True:
            raise ReviewPacketTypeError("REVIEW_PACKET_TRUE_CONST_INVALID",f"{name} must be exact true")
    return {"locally_valid":True,"field_count":len(fields),"validation_scope":"LOCAL_REVIEW_PACKET_TYPE_STRUCTURE_ONLY","authority_effect":"NONE","ordering_semantics_executed":False,"evidence_association_verified":False,"review_materiality_verified":False,"review_authority_granted":False,"runtime_qualified":False,"terminal_authority":False}
