"""R8 v15-r1 Slice 29: local ReviewPresentation FieldRule validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("field_id","classification","conditions","source_rules")
CLASSIFICATIONS: Tuple[str,...]=("REVIEW_SEMANTIC","DISPLAY_NON_SEMANTIC")

class ReviewFieldRuleError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise ReviewFieldRuleError("REVIEW_FIELD_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise ReviewFieldRuleError("REVIEW_FIELD_GCP_INVALID",f"{field}: {exc}") from exc

def validate_review_field_rule(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise ReviewFieldRuleError("REVIEW_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(FIELDS)
    if len(record)!=len(FIELDS) or actual!=expected:
        raise ReviewFieldRuleError("REVIEW_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    _string(record["field_id"],"field_id")
    classification=record["classification"]
    if not isinstance(classification,str) or classification not in CLASSIFICATIONS:
        raise ReviewFieldRuleError("REVIEW_FIELD_CLASSIFICATION_INVALID","classification outside frozen enum")
    conditions=record["conditions"]
    if not isinstance(conditions,list):
        raise ReviewFieldRuleError("REVIEW_FIELD_CONDITIONS_INVALID","conditions must be list")
    for i,value in enumerate(conditions): _string(value,f"conditions[{i}]")
    sources=record["source_rules"]
    if not isinstance(sources,list) or not sources:
        raise ReviewFieldRuleError("REVIEW_FIELD_SOURCE_RULES_INVALID","source_rules must be non-empty list")
    for i,value in enumerate(sources): _string(value,f"source_rules[{i}]")
    if len(set(sources))!=len(sources):
        raise ReviewFieldRuleError("REVIEW_FIELD_SOURCE_RULES_NOT_UNIQUE","source_rules must be unique")
    return {"locally_valid":True,"validation_scope":"LOCAL_REVIEW_FIELD_RULE_STRUCTURE_ONLY","authority_effect":"NONE","review_materiality_verified":False,"reviewer_influence_verified":False,"packet_semantics_verified":False,"review_authority_granted":False,"runtime_qualified":False,"terminal_authority":False}
