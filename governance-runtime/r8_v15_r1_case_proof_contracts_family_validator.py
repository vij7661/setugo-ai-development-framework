"""R8 v15-r1 Slice 39: composite CaseProofContracts-family structural validation only."""
from __future__ import annotations
import json, re
from collections.abc import Mapping
from typing import Any, Dict, Tuple
import r8_v15_r1_frozen_schema_runtime as slice1

ROOT_FIELDS: Tuple[str,...]=("schema","status","authority_effect","guard_range","fault_proof_legend","contracts")
CONTRACT_FIELDS=("guard_id","mechanism_id","positive_controls","negative_controls","canonical_source")
CASE_CONTROL_FIELDS=("case_id","case_text","source_version","source_commit","source_blob")
NEG_CONTROL_FIELDS=("case_id","case_text","source_version","source_commit","source_blob","fault_proof_class")
GUARD_RANGE="G001-G156"
GUARD_RE=re.compile(r"^G(?:0(?:0[1-9]|[1-9][0-9])|1(?:[0-4][0-9]|5[0-6]))$")
CASE_RE=re.compile(r"^V[0-9]+-[0-9]{3}$")
VERSION_RE=re.compile(r"^v[0-9]+$")
FP={"FP0","FP1","FP2","FP3","FP4","FP5","FP6"}
LEGEND={
"FP0":"NOT_APPLICABLE_DETERMINISTIC_INPUT: malformed/mismatched deterministic input is itself the proof.",
"FP1":"REQUIRED_SIGNED_STATE: independent signed/anchored registry, attestation, certificate, revocation, time, or witness state.",
"FP2":"REQUIRED_CONCURRENCY_TRACE: independent trace of concurrent attempts plus commit outcomes.",
"FP3":"REQUIRED_STORAGE_FAULT: independently captured rollback/corruption/outage/store mutation evidence.",
"FP4":"REQUIRED_RUNTIME_ATTESTATION: workload/runtime/sandbox identity or violation evidence independent of target guard result.",
"FP5":"REQUIRED_PROVENANCE_DIFF: exact source/artifact/schema/packet/provenance comparison evidence.",
"FP6":"REQUIRED_EXTERNAL_EFFECT: provider attempt/receipt/observation/reconciliation evidence independent of effect success guard."
}

class CaseProofContractsError(ValueError):
    def __init__(self,code:str,message:str):
        super().__init__(f"{code}: {message}"); self.code=code

def _exact(value:Any,fields:tuple[str,...],code:str,label:str)->Mapping[str,Any]:
    if not isinstance(value,Mapping) or len(value)!=len(fields) or set(value.keys())!=set(fields):
        raise CaseProofContractsError(code,f"{label} field set invalid")
    return value

def _string(value:Any,label:str)->None:
    if not isinstance(value,str) or not value:
        raise CaseProofContractsError("CPC_STRING_INVALID",f"{label} must be non-empty string")
    try:
        slice1.canonicalize_json_text(json.dumps({"value":value},ensure_ascii=True,separators=(",",":")),schema_context="object")
    except slice1.GCPError as exc:
        raise CaseProofContractsError("CPC_GCP_INVALID",f"{label}: {exc}") from exc

def _control(value:Any,label:str,negative:bool)->None:
    fields=NEG_CONTROL_FIELDS if negative else CASE_CONTROL_FIELDS
    value=_exact(value,fields,"CPC_CONTROL_FIELDS_INVALID",label)
    if not isinstance(value["case_id"],str) or CASE_RE.fullmatch(value["case_id"]) is None:
        raise CaseProofContractsError("CPC_CASE_ID_INVALID",f"{label}.case_id invalid")
    _string(value["case_text"],f"{label}.case_text")
    if not isinstance(value["source_version"],str) or VERSION_RE.fullmatch(value["source_version"]) is None:
        raise CaseProofContractsError("CPC_SOURCE_VERSION_INVALID",f"{label}.source_version invalid")
    _string(value["source_commit"],f"{label}.source_commit")
    blob=value["source_blob"]
    if blob is not None: _string(blob,f"{label}.source_blob")
    if negative and (not isinstance(value["fault_proof_class"],str) or value["fault_proof_class"] not in FP):
        raise CaseProofContractsError("CPC_FAULT_PROOF_CLASS_INVALID",f"{label}.fault_proof_class invalid")

def _contract(value:Any,index:int)->None:
    value=_exact(value,CONTRACT_FIELDS,"CPC_CONTRACT_FIELDS_INVALID",f"contracts[{index}]")
    if not isinstance(value["guard_id"],str) or GUARD_RE.fullmatch(value["guard_id"]) is None:
        raise CaseProofContractsError("CPC_GUARD_ID_INVALID",f"contracts[{index}].guard_id invalid")
    _string(value["mechanism_id"],f"contracts[{index}].mechanism_id")
    positives=value["positive_controls"]
    if not isinstance(positives,list) or not positives:
        raise CaseProofContractsError("CPC_POSITIVE_CONTROLS_INVALID",f"contracts[{index}].positive_controls minItems 1")
    for j,item in enumerate(positives): _control(item,f"contracts[{index}].positive_controls[{j}]",False)
    negatives=value["negative_controls"]
    if not isinstance(negatives,list) or not negatives:
        raise CaseProofContractsError("CPC_NEGATIVE_CONTROLS_INVALID",f"contracts[{index}].negative_controls minItems 1")
    for j,item in enumerate(negatives): _control(item,f"contracts[{index}].negative_controls[{j}]",True)
    source=value["canonical_source"]
    if not isinstance(source,Mapping) or len(source)<1:
        raise CaseProofContractsError("CPC_CANONICAL_SOURCE_INVALID",f"contracts[{index}].canonical_source minProperties 1")

def validate_case_proof_contracts(record:Mapping[str,Any])->Dict[str,Any]:
    record=_exact(record,ROOT_FIELDS,"CPC_ROOT_FIELDS_INVALID","root")
    for field,expected in (("schema","r8-v15-r1-case-proof-contracts/v1"),("status","SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE"),("authority_effect","NONE"),("guard_range",GUARD_RANGE)):
        if not isinstance(record[field],str) or record[field]!=expected:
            raise CaseProofContractsError("CPC_ROOT_CONST_INVALID",f"{field} const invalid")
    legend=_exact(record["fault_proof_legend"],tuple(LEGEND.keys()),"CPC_LEGEND_FIELDS_INVALID","fault_proof_legend")
    for key,expected in LEGEND.items():
        if not isinstance(legend[key],str) or legend[key]!=expected:
            raise CaseProofContractsError("CPC_LEGEND_CONST_INVALID",f"fault_proof_legend.{key} invalid")
    contracts=record["contracts"]
    if not isinstance(contracts,list) or len(contracts)!=156:
        raise CaseProofContractsError("CPC_CONTRACT_COUNT_INVALID","contracts must contain exactly 156 items")
    for i,item in enumerate(contracts): _contract(item,i)
    return {"locally_valid":True,"validation_scope":"LOCAL_CASE_PROOF_CONTRACTS_FAMILY_STRUCTURE_ONLY","authority_effect":"NONE","guard_identity_closure_verified":False,"registry_cross_match_verified":False,"fault_proof_evidence_verified":False,"negative_controls_executed":False,"canonical_source_verified":False,"freeze_readiness_verified":False,"terminal_authority":False}
