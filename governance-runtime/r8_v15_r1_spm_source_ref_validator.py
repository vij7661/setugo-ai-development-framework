"""R8 v15-r1 Slice 34: local SPM SourceRef structural validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("design_id","path","commit","blob")

class SPMSourceRefError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise SPMSourceRefError("SPM_SOURCE_REF_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise SPMSourceRefError("SPM_SOURCE_REF_GCP_INVALID",f"{field}: {exc}") from exc

def validate_spm_source_ref(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping) or len(record)!=len(FIELDS) or set(record.keys())!=set(FIELDS):
        raise SPMSourceRefError("SPM_SOURCE_REF_FIELD_SET_INVALID","field set invalid")
    for field in FIELDS: _string(record[field],field)
    return {"locally_valid":True,"validation_scope":"LOCAL_SPM_SOURCE_REF_STRUCTURE_ONLY","authority_effect":"NONE","source_exists_verified":False,"commit_blob_verified":False,"source_authority_verified":False,"provenance_referential_integrity_verified":False,"evidence_promotion_authorized":False,"terminal_authority":False}
