"""R8 v15-r1 Slice 33: local NCG Structured Closure structural validation only."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

FIELDS: Tuple[str,...]=("schema","status","authority_effect","dependency_nodes","dependency_edges","evaluation_order","ownership","verification","edge_semantics","reviewer_suggested_edge_disposition","v15_closure_assertions")
VERIFICATION_FIELDS=("node_count","edge_count","dependency_acyclic","topological_order","evaluation_stage_count","ownership_class_count","duplicate_ownership_classes","edge_semantics_declared")
EDGE_SEMANTICS_FIELDS=("kind","transitive_closure_edges_omitted","source_matrix","hand_added_untraceable_edges_forbidden")

class NCGStructuredClosureError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _string(value:Any,field:str)->None:
    if not isinstance(value,str) or not value:
        raise NCGStructuredClosureError("NCG_STRING_INVALID",f"{field} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise NCGStructuredClosureError("NCG_GCP_INVALID",f"{field}: {exc}") from exc

def _fixed_unique_strings(value:Any,count:int,field:str)->None:
    if not isinstance(value,list) or len(value)!=count:
        raise NCGStructuredClosureError("NCG_LIST_CARDINALITY_INVALID",f"{field} must contain exactly {count} items")
    for i,v in enumerate(value): _string(v,f"{field}[{i}]")
    if len(set(value))!=len(value):
        raise NCGStructuredClosureError("NCG_LIST_NOT_UNIQUE",f"{field} must be unique")

def _pair_list(value:Any,count:int,field:str,unique:bool)->None:
    if not isinstance(value,list) or len(value)!=count:
        raise NCGStructuredClosureError("NCG_PAIR_LIST_CARDINALITY_INVALID",f"{field} must contain exactly {count} pairs")
    keys=[]
    for i,pair in enumerate(value):
        if not isinstance(pair,list) or len(pair)!=2:
            raise NCGStructuredClosureError("NCG_PAIR_INVALID",f"{field}[{i}] must be two-item array")
        _string(pair[0],f"{field}[{i}][0]"); _string(pair[1],f"{field}[{i}][1]")
        keys.append(json.dumps(pair,ensure_ascii=False,separators=(",",":")))
    if unique and len(set(keys))!=len(keys):
        raise NCGStructuredClosureError("NCG_PAIR_LIST_NOT_UNIQUE",f"{field} must be unique")

def validate_ncg_structured_closure(record:Mapping[str,Any])->Dict[str,Any]:
    if not isinstance(record,Mapping) or len(record)!=len(FIELDS) or set(record.keys())!=set(FIELDS):
        raise NCGStructuredClosureError("NCG_FIELD_SET_INVALID","top-level field set invalid")
    _string(record["schema"],"schema"); _string(record["status"],"status")
    if record["authority_effect"]!="NONE" or not isinstance(record["authority_effect"],str):
        raise NCGStructuredClosureError("NCG_AUTHORITY_EFFECT_INVALID","authority_effect must be NONE")
    _fixed_unique_strings(record["dependency_nodes"],18,"dependency_nodes")
    _pair_list(record["dependency_edges"],29,"dependency_edges",True)
    _fixed_unique_strings(record["evaluation_order"],21,"evaluation_order")
    _pair_list(record["ownership"],18,"ownership",False)

    verification=record["verification"]
    if not isinstance(verification,Mapping) or len(verification)!=len(VERIFICATION_FIELDS) or set(verification.keys())!=set(VERIFICATION_FIELDS):
        raise NCGStructuredClosureError("NCG_VERIFICATION_INVALID","verification field set invalid")
    for field,expected in (("node_count",18),("edge_count",29),("evaluation_stage_count",21),("ownership_class_count",18)):
        if type(verification[field]) is not int or verification[field]!=expected:
            raise NCGStructuredClosureError("NCG_VERIFICATION_CONST_INVALID",f"{field} invalid")
    for field in ("dependency_acyclic","edge_semantics_declared"):
        if type(verification[field]) is not bool or verification[field] is not True:
            raise NCGStructuredClosureError("NCG_VERIFICATION_TRUE_INVALID",f"{field} must be exact true")
    _fixed_unique_strings(verification["topological_order"],18,"verification.topological_order")
    if not isinstance(verification["duplicate_ownership_classes"],list) or verification["duplicate_ownership_classes"]:
        raise NCGStructuredClosureError("NCG_DUPLICATE_OWNERSHIP_CLASSES_INVALID","must be empty array")

    edge=record["edge_semantics"]
    if not isinstance(edge,Mapping) or len(edge)!=len(EDGE_SEMANTICS_FIELDS) or set(edge.keys())!=set(EDGE_SEMANTICS_FIELDS):
        raise NCGStructuredClosureError("NCG_EDGE_SEMANTICS_INVALID","edge_semantics field set invalid")
    if edge["kind"]!="DIRECT_AUTHORITY_RELEVANT_CONSUMPTION_OR_PRECONDITION" or not isinstance(edge["kind"],str):
        raise NCGStructuredClosureError("NCG_EDGE_KIND_INVALID","kind const invalid")
    if edge["source_matrix"]!="governance-r8/R8-V15-NCG-1-MATRICES.md" or not isinstance(edge["source_matrix"],str):
        raise NCGStructuredClosureError("NCG_EDGE_SOURCE_MATRIX_INVALID","source_matrix const invalid")
    for field in ("transitive_closure_edges_omitted","hand_added_untraceable_edges_forbidden"):
        if type(edge[field]) is not bool or edge[field] is not True:
            raise NCGStructuredClosureError("NCG_EDGE_TRUE_CONST_INVALID",f"{field} must be exact true")

    suggestions=record["reviewer_suggested_edge_disposition"]
    if not isinstance(suggestions,list) or any(not isinstance(v,Mapping) for v in suggestions):
        raise NCGStructuredClosureError("NCG_REVIEWER_DISPOSITION_INVALID","must be array of objects")
    if not isinstance(record["v15_closure_assertions"],Mapping):
        raise NCGStructuredClosureError("NCG_CLOSURE_ASSERTIONS_INVALID","v15_closure_assertions must be object")
    return {"locally_valid":True,"validation_scope":"LOCAL_NCG_STRUCTURED_CLOSURE_SHAPE_ONLY","authority_effect":"NONE","acyclicity_recomputed":False,"topology_verified":False,"edge_semantics_verified":False,"ownership_semantics_verified":False,"authority_graph_enforced":False,"terminal_authority":False}
