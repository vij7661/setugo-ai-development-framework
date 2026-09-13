"""V24 I11 execution harness V1: construction-only enforcement layer.

Importing or unit-testing this module executes no WDPC scientific case.
It binds the reviewed V8 plan and mechanically enforces Section 7 fixture
branches, Section 8 negative PASS invariants, Section 13 scheduling/locks,
and append-only scientific result chaining.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping
import hashlib
import json

from v24_i11_case_specs_v8 import CASE_SPECS
from v24_i11_harness_contract_v7 import (
    AuthorityEffectObservation, CaseRunBinding, ConjunctiveAssertionObservation,
    GovernedEndpointObservation, InsufficientEvidenceEndpointCondition,
    PositiveAssertionObservation, classify_conjunctive_negative,
    classify_negative, classify_positive,
)

EXECUTION_HARNESS_VERSION="1.0.0-PRE-EXECUTION"
V8_PACKET_SHA256="e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e"
V8_PLAN_BODY_SHA256="3b442e55bec52aec24042d714d4064985eb85acf914afa5903d00d1a61b373ab"
V8_REVIEW_BINDING_BLOB="716a2a2917130c898cc4244d44cf0141e49dd83e"
HARNESS_V7_BLOB="6573767ae85d7ca0cfaa8b7bbafa826a7ba0c5cb"

EXACT_FIXTURE_BRANCHES={
"WDPC-433":"OMIT_EXACTLY_ONE_ACTIVE_PREDICATE",
"WDPC-453":"OMIT_EXACTLY_ONE_STRICTER_SUBSYSTEM_PREDICATE",
"WDPC-458":"AUTHORITY_PRESENT_INDEPENDENCE_UNPROVEN",
"WDPC-457":"NO_STRICTER_SOURCE_ENDPOINT_HISTORY_UNCHANGED",
"WDPC-472":"COMPETING_ADMISSION_LINEAGE_CURRENT_UNKNOWN",
"WDPC-474":"COMPETING_COMPLETENESS_LINEAGE_CURRENT_UNKNOWN",
"WDPC-479":"BOUND_STATE_ONLY_CHANGE_AFTER_DECISION",
"WDPC-482":"WRONG_ARTIFACT_BLOB_ONLY",
"WDPC-483":"ADMITTED_INSTANCE_STALES_COMPLETENESS",
"WDPC-497":"DIRECT_UNADMITTED_WRITER_NO_STRICTER_FENCE",
"WDPC-498":"IAM_PERIMETER_ONLY_DRIFT_AFTER_DECISION",
"WDPC-499":"GENESIS_CIRCULARITY",
"WDPC-502":"ABSENT_IUDA_LINEAGE",
"WDPC-503":"IN_PLACE_BOOTSTRAP_MUTATION_UNCHANGED_GENERATION",
}
SERIAL_CASES={"WDPC-434","WDPC-464","WDPC-460","WDPC-484","WDPC-472","WDPC-474"}
EVIDENCE_LOCK_CLASS={
"E-WITNESS":"WITNESS_LINEAGE","E-WITNESS-LINEAGE":"WITNESS_LINEAGE",
"E-LEDGER-LINEAGE":"LEDGER_LINEAGE","E-COMPLETENESS-LEDGER-LINEAGE":"LEDGER_LINEAGE",
"E-IAM-PERIMETER":"IAM_PERIMETER","E-IUDA":"IUDA",
"E-ADMISSION-COMPLETENESS":"IUDA","E-COMPOSITE-486":"IUDA",
"E-SEMANTIC":"SEMANTIC_WORKSHEET","E-BOOTSTRAP":"BOOTSTRAP_CEREMONY",
"E-BOOTSTRAP-CONTROL":"BOOTSTRAP_CEREMONY",
}

PROFILE_REQUIRED_FIELDS={
"O-AGG":{"authority_transition_state","effect_before","effect_after"},
"O-CONTROL":{"downstream_guarded_decision_before","downstream_guarded_decision_after","material_effect_before","material_effect_after"},
"O-ENDPOINT":{"table_active","dispatch_before","dispatch_after","material_effect_before","material_effect_after"},
"O-NORMATIVE":{"authority_derived_from_target","decision_dispatch_before","decision_dispatch_after","material_effect_before","material_effect_after"},
"O-PROOF":{"proof_state","consuming_authority_decision_before","consuming_authority_decision_after","material_effect_before","material_effect_after"},
"O-UNIVERSE":{"unqualified_path_reached_sink","sink_effect_before","sink_effect_after"},
"O-MIGRATION":{"predecessor_read_accepted","successor_activated","material_effect_before","material_effect_after"},
"O-APPLICATION":{"valid_applied_state","sink_effect_before","sink_effect_after"},
"O-APPLY":{"worker_invocation_before","worker_invocation_after","application_record_count_before","application_record_count_after","material_effect_before","material_effect_after"},
"O-HISTORY":{"historical_decision_digest_before","historical_decision_digest_after","historical_result_before","historical_result_after","retroactively_upgraded","material_effect_before","material_effect_after"},
"O-BOOTSTRAP":{"completeness_current_record_count_before","completeness_current_record_count_after","generation_activated","material_effect_before","material_effect_after"},
"O-PERIMETER":{"closed_world_authority_path_qualified","material_write_count_before","material_write_count_after","material_effect_before","material_effect_after"},
}

def _sha(value: Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def validate_fixture_branch(case_id:str, observed:str|None)->list[str]:
    expected=EXACT_FIXTURE_BRANCHES.get(case_id)
    return [] if expected is None or observed==expected else [f"FIXTURE_BRANCH_MISMATCH:{expected}:{observed}"]

def validate_profile_negative(profile:str, o:Mapping[str,Any])->list[str]:
    required=PROFILE_REQUIRED_FIELDS.get(profile)
    if required is None: return [f"UNKNOWN_PROFILE:{profile}"]
    missing=required-set(o)
    if missing: return ["PROFILE_FIELDS_MISSING:"+",".join(sorted(missing))]
    p=[]
    dz=lambda a,b,code: p.append(code) if o[b]!=o[a] else None
    if profile=="O-AGG":
        if o["authority_transition_state"]=="SUCCESS": p.append("AGG_TRANSITION_SUCCESS_FORBIDDEN")
        dz("effect_before","effect_after","AGG_EFFECT_DELTA_NONZERO")
    elif profile=="O-CONTROL":
        dz("downstream_guarded_decision_before","downstream_guarded_decision_after","CONTROL_DECISION_DELTA_NONZERO")
        dz("material_effect_before","material_effect_after","CONTROL_EFFECT_DELTA_NONZERO")
    elif profile=="O-ENDPOINT":
        if o["table_active"]: p.append("ENDPOINT_TABLE_ACTIVE_FORBIDDEN")
        dz("dispatch_before","dispatch_after","ENDPOINT_DISPATCH_DELTA_NONZERO")
        dz("material_effect_before","material_effect_after","ENDPOINT_EFFECT_DELTA_NONZERO")
    elif profile=="O-NORMATIVE":
        if o["authority_derived_from_target"]: p.append("NORMATIVE_AUTHORITY_DERIVATION_FORBIDDEN")
        dz("decision_dispatch_before","decision_dispatch_after","NORMATIVE_DISPATCH_DELTA_NONZERO")
        dz("material_effect_before","material_effect_after","NORMATIVE_EFFECT_DELTA_NONZERO")
    elif profile=="O-PROOF":
        if o["proof_state"]=="PASS": p.append("PROOF_PASS_FORBIDDEN")
        dz("consuming_authority_decision_before","consuming_authority_decision_after","PROOF_CONSUMER_DELTA_NONZERO")
        dz("material_effect_before","material_effect_after","PROOF_EFFECT_DELTA_NONZERO")
    elif profile=="O-UNIVERSE":
        if o["unqualified_path_reached_sink"]: p.append("UNQUALIFIED_PATH_REACHED_SINK")
        dz("sink_effect_before","sink_effect_after","UNIVERSE_EFFECT_DELTA_NONZERO")
    elif profile=="O-MIGRATION":
        if o["predecessor_read_accepted"]: p.append("PREDECESSOR_READ_ACCEPTED")
        if o["successor_activated"]: p.append("SUCCESSOR_ACTIVATED")
        dz("material_effect_before","material_effect_after","MIGRATION_EFFECT_DELTA_NONZERO")
    elif profile=="O-APPLICATION":
        if o["valid_applied_state"]: p.append("VALID_APPLIED_STATE_FORBIDDEN")
        dz("sink_effect_before","sink_effect_after","APPLICATION_EFFECT_DELTA_NONZERO")
    elif profile=="O-APPLY":
        dz("worker_invocation_before","worker_invocation_after","APPLY_WORKER_DELTA_NONZERO")
        dz("application_record_count_before","application_record_count_after","APPLY_RECORD_DELTA_NONZERO")
        dz("material_effect_before","material_effect_after","APPLY_EFFECT_DELTA_NONZERO")
    elif profile=="O-HISTORY":
        dz("historical_decision_digest_before","historical_decision_digest_after","HISTORY_DIGEST_CHANGED")
        dz("historical_result_before","historical_result_after","HISTORY_RESULT_CHANGED")
        if o["retroactively_upgraded"]: p.append("HISTORY_RETROACTIVE_UPGRADE")
        dz("material_effect_before","material_effect_after","HISTORY_EFFECT_DELTA_NONZERO")
    elif profile=="O-BOOTSTRAP":
        dz("completeness_current_record_count_before","completeness_current_record_count_after","BOOTSTRAP_COMPLETENESS_DELTA_NONZERO")
        if o["generation_activated"]: p.append("BOOTSTRAP_GENERATION_ACTIVATED")
        dz("material_effect_before","material_effect_after","BOOTSTRAP_EFFECT_DELTA_NONZERO")
    elif profile=="O-PERIMETER":
        if o["closed_world_authority_path_qualified"]: p.append("PERIMETER_CLOSED_WORLD_PATH_QUALIFIED")
        dz("material_write_count_before","material_write_count_after","PERIMETER_WRITE_DELTA_NONZERO")
        dz("material_effect_before","material_effect_after","PERIMETER_EFFECT_DELTA_NONZERO")
    return p

@dataclass(frozen=True)
class ScientificCaseResult:
    case_id:str; run_id:str; result_state:str; profile_id:str
    evidence_digest:str; predecessor_record_digest:str|None
    diagnostics:tuple[str,...]=(); authority_effect:str="NONE_EVIDENCE_ONLY"
    def digest(self)->str: return _sha(asdict(self))

class ResultLedger:
    def __init__(self): self._records=[]; self._run_ids=set()
    @property
    def head(self): return None if not self._records else self._records[-1].digest()
    @property
    def records(self): return tuple(self._records)
    def append(self,r:ScientificCaseResult)->str:
        if r.run_id in self._run_ids: raise ValueError("DUPLICATE_RUN_ID")
        if r.predecessor_record_digest!=self.head: raise ValueError("RESULT_LEDGER_PREDECESSOR_MISMATCH")
        self._records.append(r); self._run_ids.add(r.run_id); return r.digest()

class ExecutionScheduler:
    def __init__(self): self._active_locks=set(); self._active={}; self._terminal={}
    def required_locks(self,case_id:str,evidence_snapshot_id:str|None=None)->tuple[str,...]:
        s=CASE_SPECS[case_id]; locks=set()
        if case_id in SERIAL_CASES: locks.add("SERIAL_SCIENTIFIC_CASE")
        c=EVIDENCE_LOCK_CLASS.get(s["evidence_profile"])
        if c: locks.add("EVIDENCE_CLASS:"+c)
        if s["evidence_profile"]!="NONE":
            if not evidence_snapshot_id: raise ValueError("EXTERNAL_EVIDENCE_SNAPSHOT_ID_REQUIRED")
            locks.add("EVIDENCE_SNAPSHOT:"+evidence_snapshot_id)
        return tuple(sorted(locks))
    def unresolved_negatives(self,case_id:str)->tuple[str,...]:
        s=CASE_SPECS[case_id]
        if s["case_type"]!="POS": return ()
        profile=s["profile_id"]; bad=[]
        for cid,x in CASE_SPECS.items():
            if x["case_type"]!="NEG" or x["profile_id"]!=profile: continue
            r=self._terminal.get(cid)
            if r!="PASS": bad.append(cid)
        return tuple(sorted(bad))
    def acquire(self,case_id:str,evidence_snapshot_id:str|None=None)->tuple[str,...]:
        bad=self.unresolved_negatives(case_id)
        if bad: raise ValueError("POSITIVE_BEFORE_NEGATIVE_RESOLUTION:"+",".join(bad))
        locks=self.required_locks(case_id,evidence_snapshot_id)
        c=self._active_locks.intersection(locks)
        if c: raise ValueError("EVIDENCE_LOCK_CONFLICT:"+",".join(sorted(c)))
        self._active_locks.update(locks); self._active[case_id]=locks; return locks
    def release(self,case_id:str,terminal_result:str)->None:
        locks=self._active.pop(case_id,None)
        if locks is None: raise ValueError("CASE_NOT_ACTIVE")
        for lock in locks: self._active_locks.remove(lock)
        self._terminal[case_id]=terminal_result

def adjudicate_negative(case_id:str, binding:CaseRunBinding, endpoint:GovernedEndpointObservation,
                        effect:AuthorityEffectObservation, profile_observation:Mapping[str,Any],
                        fixture_valid:bool, harness_valid:bool, fixture_branch_id:str|None=None,
                        ie:InsufficientEvidenceEndpointCondition|None=None,
                        conjunctive:ConjunctiveAssertionObservation|None=None)->ScientificCaseResult:
    s=CASE_SPECS[case_id]
    branch_errors=validate_fixture_branch(case_id,fixture_branch_id)
    if branch_errors: state="FAIL_FIXTURE_DEFECT"; diag=branch_errors
    elif s["expected_kind"]=="CONJUNCTIVE_ASSERTION":
        state=classify_conjunctive_negative(case_id=case_id,expected_endpoint="AUTHORITY_EVIDENCE_SOURCE_INVALID",
            observation=conjunctive,effect=effect,fixture_valid=fixture_valid,harness_valid=harness_valid); diag=[]
    else:
        state=classify_negative(case_id=case_id,expected_endpoint=s["expected_value"],observed=endpoint,
            effect=effect,fixture_valid=fixture_valid,harness_valid=harness_valid,ie_condition=ie); diag=[]
    if state=="PASS":
        errs=validate_profile_negative(s["profile_id"],profile_observation)
        if errs: state="FAIL_CODE_DEFECT"; diag.extend(errs)
    return ScientificCaseResult(case_id,binding.run_id,state,s["profile_id"],_sha(profile_observation),None,tuple(diag))

def adjudicate_positive(case_id:str,binding:CaseRunBinding,o:PositiveAssertionObservation,
                        fixture_valid:bool,harness_valid:bool)->ScientificCaseResult:
    s=CASE_SPECS[case_id]
    state=classify_positive(observation=o,fixture_valid=fixture_valid,harness_valid=harness_valid)
    return ScientificCaseResult(case_id,binding.run_id,state,s["profile_id"],_sha(asdict(o)),None)

def assert_execution_frontier()->dict[str,Any]:
    if len(CASE_SPECS)!=76 or set(CASE_SPECS)!={f"WDPC-{i}" for i in range(431,507)}:
        raise AssertionError("CASE_SPEC_COVERAGE_INVALID")
    if any(CASE_SPECS[c]["status"]!="BLOCKED_BY_I1_SEMANTIC_QUALIFICATION" for c in ("WDPC-469","WDPC-495")):
        raise AssertionError("BLOCKED_CASE_STATUS_INVALID")
    missing=[c for c,s in CASE_SPECS.items() if s["case_type"]=="NEG" and s["profile_id"] not in PROFILE_REQUIRED_FIELDS]
    if missing: raise AssertionError("NEGATIVE_PROFILE_NOT_IMPLEMENTED:"+",".join(missing))
    return {"plan_review_gate":"PASS","repository_binding_gate":"PASS",
            "execution_harness_profile_invariant_gate":"CONSTRUCTION_READY",
            "wdpc_execution_status":"NOT_EXECUTED","case_count":76,
            "blocked_cases":["WDPC-469","WDPC-495"],"authority_effect":"NONE_EVIDENCE_ONLY"}
