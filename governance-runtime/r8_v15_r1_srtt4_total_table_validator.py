"""R8 v15-r1 Slice 44: SRTT-4 TotalTable structural/domain closure only; no decision recomputation."""
from __future__ import annotations
import itertools,re
from collections import Counter
from collections.abc import Mapping
from typing import Any,Dict,Tuple

ROOT_FIELDS:Tuple[str,...]=("schema","status","authority_effect","generator_contract","rule_registry_path","domain_fixed","enum_order","row_count","distribution","verification","rows")
DOMAIN_FIELDS=("source_entry_state",)
ENUM_FIELDS=("old_scope_match","destination_scope_match","old_scope_effect","scope_relation","any_permission_valid","mapping_effective","lineage_mapping_valid","scope_expansion_authorized","decision_inside_authorized_expansion_domain")
DIST_FIELDS=("SEMANTIC_SCOPE_REVOKED","SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED","MAPPING_NOT_APPLICABLE","REPLACEMENT_ELIGIBLE","SEMANTIC_SCOPE_REPLACEMENT_INVALID")
VERIFY_FIELDS=("expected_row_count","generated_row_count","every_row_has_declared_rule","generation_conflicts")
ROW_FIELDS=("row_id","input","result","decisive_rule_id")
INPUT_FIELDS=("source_entry_state","old_scope_match","destination_scope_match","old_scope_effect","scope_relation","any_permission_valid","mapping_effective","lineage_mapping_valid","scope_expansion_authorized","decision_inside_authorized_expansion_domain")
OLD=("NO_MATCH","EXACT_MATCH")
DEST=("NO_MATCH","EXACT_MATCH","MAPPED_MATCH")
EFFECT=("BLOCK_OLD_SCOPE","REPLACE_OLD_SCOPE_FOR_EXACT_MATCH","REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH")
REL=("SAME","NARROWER","BROADER","DISJOINT")
BOOL=(False,True)
RESULTS=set(DIST_FIELDS)
EXPECTED_DIST={"SEMANTIC_SCOPE_REVOKED":1808,"SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED":288,"MAPPING_NOT_APPLICABLE":144,"REPLACEMENT_ELIGIBLE":22,"SEMANTIC_SCOPE_REPLACEMENT_INVALID":42}
RULE_RE=re.compile(r"^SRTT15-R(?:0[1-9]|1[01])$")
EXPECTED_DOMAIN=set(itertools.product(OLD,DEST,EFFECT,REL,BOOL,BOOL,BOOL,BOOL,BOOL))

class SRTT4TotalTableError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact(v:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(v,Mapping) or len(v)!=len(fields) or set(v.keys())!=set(fields):
        raise SRTT4TotalTableError(code,f"{label} field set invalid")
    return v

def _strict_list_const(v:Any,expected:tuple[Any,...],label:str)->None:
    if not isinstance(v,list) or len(v)!=len(expected):
        raise SRTT4TotalTableError("SRTT_TABLE_ENUM_ORDER_INVALID",f"{label} invalid")
    for got,exp in zip(v,expected):
        if type(got) is not type(exp) or got!=exp:
            raise SRTT4TotalTableError("SRTT_TABLE_ENUM_ORDER_INVALID",f"{label} invalid")

def _input(v:Any,label:str)->tuple[Any,...]:
    v=_exact(v,INPUT_FIELDS,"SRTT_TABLE_INPUT_FIELDS_INVALID",label)
    if v["source_entry_state"]!="REVOKED" or not isinstance(v["source_entry_state"],str):
        raise SRTT4TotalTableError("SRTT_TABLE_SOURCE_STATE_INVALID",f"{label}.source_entry_state invalid")
    if v["old_scope_match"] not in OLD or not isinstance(v["old_scope_match"],str): raise SRTT4TotalTableError("SRTT_TABLE_OLD_MATCH_INVALID",label)
    if v["destination_scope_match"] not in DEST or not isinstance(v["destination_scope_match"],str): raise SRTT4TotalTableError("SRTT_TABLE_DEST_MATCH_INVALID",label)
    if v["old_scope_effect"] not in EFFECT or not isinstance(v["old_scope_effect"],str): raise SRTT4TotalTableError("SRTT_TABLE_EFFECT_INVALID",label)
    if v["scope_relation"] not in REL or not isinstance(v["scope_relation"],str): raise SRTT4TotalTableError("SRTT_TABLE_RELATION_INVALID",label)
    bool_fields=INPUT_FIELDS[5:]
    for f in bool_fields:
        if type(v[f]) is not bool: raise SRTT4TotalTableError("SRTT_TABLE_BOOL_INVALID",f"{label}.{f} must be boolean")
    return (v["old_scope_match"],v["destination_scope_match"],v["old_scope_effect"],v["scope_relation"],*(v[f] for f in bool_fields))

def validate_srtt4_total_table(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,ROOT_FIELDS,"SRTT_TABLE_ROOT_FIELDS_INVALID","root")
    for f,e in (("schema","r8-v15-srtt-4-total-table/v1"),("authority_effect","NONE"),("generator_contract","R8V15-I001..I007"),("rule_registry_path","governance-r8/R8-V15-SRTT-4-RULE-REGISTRY.json")):
        if not isinstance(record[f],str) or record[f]!=e: raise SRTT4TotalTableError("SRTT_TABLE_CONST_INVALID",f"{f} const invalid")
    if not isinstance(record["status"],str) or not record["status"]: raise SRTT4TotalTableError("SRTT_TABLE_STATUS_INVALID","status invalid")
    domain=_exact(record["domain_fixed"],DOMAIN_FIELDS,"SRTT_TABLE_DOMAIN_FIELDS_INVALID","domain_fixed")
    if domain["source_entry_state"]!="REVOKED" or not isinstance(domain["source_entry_state"],str): raise SRTT4TotalTableError("SRTT_TABLE_DOMAIN_INVALID","domain source state invalid")
    enum=_exact(record["enum_order"],ENUM_FIELDS,"SRTT_TABLE_ENUM_FIELDS_INVALID","enum_order")
    for f,e in (("old_scope_match",OLD),("destination_scope_match",DEST),("old_scope_effect",EFFECT),("scope_relation",REL),("any_permission_valid",BOOL),("mapping_effective",BOOL),("lineage_mapping_valid",BOOL),("scope_expansion_authorized",BOOL),("decision_inside_authorized_expansion_domain",BOOL)):
        _strict_list_const(enum[f],e,f"enum_order.{f}")
    if type(record["row_count"]) is not int or record["row_count"]!=2304: raise SRTT4TotalTableError("SRTT_TABLE_ROW_COUNT_INVALID","row_count must be 2304")
    dist=_exact(record["distribution"],DIST_FIELDS,"SRTT_TABLE_DIST_FIELDS_INVALID","distribution")
    for f,e in EXPECTED_DIST.items():
        if type(dist[f]) is not int or dist[f]!=e: raise SRTT4TotalTableError("SRTT_TABLE_DIST_CONST_INVALID",f"distribution.{f} invalid")
    ver=_exact(record["verification"],VERIFY_FIELDS,"SRTT_TABLE_VERIFY_FIELDS_INVALID","verification")
    for f,e in (("expected_row_count",2304),("generated_row_count",2304),("generation_conflicts",0)):
        if type(ver[f]) is not int or ver[f]!=e: raise SRTT4TotalTableError("SRTT_TABLE_VERIFY_CONST_INVALID",f"verification.{f} invalid")
    if type(ver["every_row_has_declared_rule"]) is not bool or ver["every_row_has_declared_rule"] is not True:
        raise SRTT4TotalTableError("SRTT_TABLE_VERIFY_TRUE_INVALID","every_row_has_declared_rule must be exact true")
    rows=record["rows"]
    if not isinstance(rows,list) or len(rows)!=2304: raise SRTT4TotalTableError("SRTT_TABLE_ROWS_INVALID","rows must contain exactly 2304")
    row_ids=[]; inputs=[]; actual=Counter()
    for i,row in enumerate(rows):
        row=_exact(row,ROW_FIELDS,"SRTT_TABLE_ROW_FIELDS_INVALID",f"rows[{i}]")
        rid=row["row_id"]
        if isinstance(rid,bool) or not isinstance(rid,int) or rid<1 or rid>2304: raise SRTT4TotalTableError("SRTT_TABLE_ROW_ID_INVALID",f"rows[{i}].row_id invalid")
        row_ids.append(rid)
        inputs.append(_input(row["input"],f"rows[{i}].input"))
        result=row["result"]
        if not isinstance(result,str) or result not in RESULTS: raise SRTT4TotalTableError("SRTT_TABLE_RESULT_INVALID",f"rows[{i}].result invalid")
        actual[result]+=1
        rr=row["decisive_rule_id"]
        if not isinstance(rr,str) or RULE_RE.fullmatch(rr) is None: raise SRTT4TotalTableError("SRTT_TABLE_RULE_ID_INVALID",f"rows[{i}].decisive_rule_id invalid")
    if set(row_ids)!=set(range(1,2305)) or len(set(row_ids))!=2304: raise SRTT4TotalTableError("SRTT_TABLE_ROW_ID_CLOSURE_INVALID","row ids must be exactly 1..2304")
    if set(inputs)!=EXPECTED_DOMAIN or len(set(inputs))!=2304: raise SRTT4TotalTableError("SRTT_TABLE_CARTESIAN_DOMAIN_INVALID","input tuples must exactly cover declared Cartesian domain once")
    if dict(actual)!=EXPECTED_DIST: raise SRTT4TotalTableError("SRTT_TABLE_ACTUAL_DISTRIBUTION_INVALID","row results do not match frozen distribution counts")
    return {
      "locally_valid":True,
      "validation_scope":"LOCAL_SRTT4_TABLE_STRUCTURE_DOMAIN_AND_DISTRIBUTION_ONLY",
      "authority_effect":"NONE",
      "row_id_closure_verified":True,
      "cartesian_domain_closure_verified":True,
      "declared_distribution_verified":True,
      "decisive_rule_registry_membership_verified":False,
      "decision_semantics_recomputed":False,
      "replacement_authority_granted":False,
      "terminal_authority":False
    }
