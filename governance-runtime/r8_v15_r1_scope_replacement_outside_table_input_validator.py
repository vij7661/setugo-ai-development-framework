"""R8 v15-r1 Slice 28: local ScopeReplacementOutsideTableInput structural validation only."""
from __future__ import annotations
from collections.abc import Mapping
from typing import Any, Dict, Tuple

FIELDS: Tuple[str,...]=("source_entry_state","old_scope_match","destination_scope_match","old_scope_effect","scope_relation","any_permission_valid","mapping_effective","lineage_mapping_valid","scope_expansion_authorized","decision_inside_authorized_expansion_domain")
SOURCE_STATES={"ACTIVE","SUSPENDED","SUPERSEDED","RETIRED","SCOPE_PERMISSION_REEVALUATION_REQUIRED"}
OLD_SCOPE_MATCHES={"NO_MATCH","EXACT_MATCH"}
DESTINATION_SCOPE_MATCHES={"NO_MATCH","EXACT_MATCH","MAPPED_MATCH"}
OLD_SCOPE_EFFECTS={"BLOCK_OLD_SCOPE","REPLACE_OLD_SCOPE_FOR_EXACT_MATCH","REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH"}
SCOPE_RELATIONS={"SAME","NARROWER","BROADER","DISJOINT"}
BOOL_FIELDS=("any_permission_valid","mapping_effective","lineage_mapping_valid","scope_expansion_authorized","decision_inside_authorized_expansion_domain")

class ScopeReplacementOutsideTableInputError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _enum(value:Any,allowed:set[str],field:str)->None:
    if not isinstance(value,str) or value not in allowed:
        raise ScopeReplacementOutsideTableInputError("SCOPE_REPLACEMENT_OUTSIDE_ENUM_INVALID",f"{field} outside frozen enum")

def validate_scope_replacement_outside_table_input(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping):
        raise ScopeReplacementOutsideTableInputError("SCOPE_REPLACEMENT_OUTSIDE_FIELD_SET_INVALID","record must be mapping")
    actual=set(record.keys()); expected=set(FIELDS)
    if len(record)!=len(FIELDS) or actual!=expected:
        raise ScopeReplacementOutsideTableInputError("SCOPE_REPLACEMENT_OUTSIDE_FIELD_SET_INVALID",f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    _enum(record["source_entry_state"],SOURCE_STATES,"source_entry_state")
    _enum(record["old_scope_match"],OLD_SCOPE_MATCHES,"old_scope_match")
    _enum(record["destination_scope_match"],DESTINATION_SCOPE_MATCHES,"destination_scope_match")
    _enum(record["old_scope_effect"],OLD_SCOPE_EFFECTS,"old_scope_effect")
    _enum(record["scope_relation"],SCOPE_RELATIONS,"scope_relation")
    for field in BOOL_FIELDS:
        if type(record[field]) is not bool:
            raise ScopeReplacementOutsideTableInputError("SCOPE_REPLACEMENT_OUTSIDE_BOOLEAN_INVALID",f"{field} must be exact bool")
    return {"locally_valid":True,"validation_scope":"LOCAL_SCOPE_REPLACEMENT_OUTSIDE_TABLE_INPUT_STRUCTURE_ONLY","authority_effect":"NONE","mapping_effectiveness_verified":False,"any_permission_verified":False,"lineage_mapping_verified":False,"srtt_table_lookup_performed":False,"not_a_replacement_branch_verified":False,"replacement_eligible":False,"scope_expansion_verified":False,"semantic_selected":False,"constitutional_authorized":False,"runtime_qualified":False,"evidence_promotion_authorized":False,"policy_authority_granted":False,"terminal_authority":False}
