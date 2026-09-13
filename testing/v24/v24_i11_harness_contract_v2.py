"""WDPC V24 I11 falsification harness contract V2.

Schema/invariant definitions only. Importing this module executes no WDPC case.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import hashlib, json

HARNESS_ID="WDPC-V24-I11-HARNESS"
HARNESS_VERSION="1.1.0-PLAN-REVIEW"
FROZEN_V24_DESIGN_SHA="db9e4b349fd26e128f4486878a4af64929000a7c"
FROZEN_I10_IMPLEMENTATION_SHA="9836dc3ff233cca582f485434fc1c6494cf7eb05"
FROZEN_I10_TREE="d68cbccdceebad88715c8b37ddfcd524fc16ce8a"
GOVERNANCE_GENERATION="V24"
PYTHON_RUNTIME="3.12"
PYTHONHASHSEED="0"
TIMEZONE="UTC"
FIXTURE_RANDOM_SEED=24011
REVIEWER_API_CALLS="PROHIBITED"
REFERENCE_NETWORK_POLICY="DENY"

RESULT_STATES={"PASS","FAIL_CODE_DEFECT","FAIL_HARNESS_DEFECT","FAIL_FIXTURE_DEFECT","INSUFFICIENT_EVIDENCE","NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED","BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE"}
CASE_STATUSES={"NOT_EXECUTED","EXECUTABLE","BLOCKED_BY_I1_SEMANTIC_QUALIFICATION","RUNNING","EXECUTED"}
EXECUTION_CLASSES={"REFERENCE_HARNESS","REFERENCE_MECHANISM_ONLY","HYBRID_EXTERNAL_REQUIRED","EXTERNAL_MANUAL_REQUIRED","MANUAL_SEMANTIC_REQUIRED","STATIC_OR_MANUAL_REQUIRED","BLOCKED_BY_I1_SEMANTIC_QUALIFICATION"}
CASE_IDS=tuple(f"WDPC-{i}" for i in range(431,507))
BLOCKED_CASES={"WDPC-469","WDPC-495"}

def digest(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

@dataclass(frozen=True)
class ExecutionClassPolicy:
    execution_class:str
    synthetic_execution_permitted:bool
    external_or_manual_evidence_required:bool
    operational_pass_permitted_without_external_evidence:bool
    default_missing_evidence_result:str|None

EXECUTION_CLASS_POLICY={
    "REFERENCE_HARNESS":ExecutionClassPolicy("REFERENCE_HARNESS",True,False,True,None),
    "REFERENCE_MECHANISM_ONLY":ExecutionClassPolicy("REFERENCE_MECHANISM_ONLY",True,False,False,None),
    "HYBRID_EXTERNAL_REQUIRED":ExecutionClassPolicy("HYBRID_EXTERNAL_REQUIRED",True,True,False,"NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED"),
    "EXTERNAL_MANUAL_REQUIRED":ExecutionClassPolicy("EXTERNAL_MANUAL_REQUIRED",False,True,False,"NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED"),
    "MANUAL_SEMANTIC_REQUIRED":ExecutionClassPolicy("MANUAL_SEMANTIC_REQUIRED",False,True,False,"NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED"),
    "STATIC_OR_MANUAL_REQUIRED":ExecutionClassPolicy("STATIC_OR_MANUAL_REQUIRED",False,True,False,"NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED"),
    "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION":ExecutionClassPolicy("BLOCKED_BY_I1_SEMANTIC_QUALIFICATION",False,True,False,None),
}

@dataclass(frozen=True)
class GovernedEndpointObservation:
    endpoint:str|None
    emission_surface:str
    raw_result_digest:str
    internal_diagnostics:tuple[str,...]=()

@dataclass(frozen=True)
class ConjunctiveAssertionObservation:
    primary_endpoint:GovernedEndpointObservation
    required_invariants:tuple[str,...]
    satisfied_invariants:tuple[str,...]
    invariant_evidence_digests:tuple[str,...]

    @property
    def complete(self)->bool:
        return set(self.required_invariants)==set(self.satisfied_invariants) and bool(self.required_invariants)

@dataclass(frozen=True)
class AuthorityEffectObservation:
    profile_id:str
    before_digest:str
    after_digest:str
    unauthorized_effect_count_before:int
    unauthorized_effect_count_after:int
    sink_state_before:str|None=None
    sink_state_after:str|None=None
    @property
    def unauthorized_effect_delta(self)->int:
        return self.unauthorized_effect_count_after-self.unauthorized_effect_count_before

@dataclass(frozen=True)
class EnvironmentIdentity:
    python_version:str
    os_release_digest:str
    uname_digest:str
    dependency_lock_digest:str
    dependency_lock_method:str
    timezone:str
    pythonhashseed:str
    fixture_random_seed:int
    clock_model:str

@dataclass(frozen=True)
class CaseRunBinding:
    case_id:str
    run_id:str
    plan_body_sha256:str
    plan_packet_blob_sha:str
    harness_blob_sha:str
    harness_version:str
    design_sha:str
    implementation_sha:str
    implementation_tree:str
    governance_generation:str
    target_module_blobs:tuple[str,...]
    fixture_digest:str
    environment_digest:str
    case_status:str


def validate_environment(env:EnvironmentIdentity)->list[str]:
    p=[]
    if not env.python_version.startswith(PYTHON_RUNTIME):p.append("HARNESS_RUNTIME_VERSION_MISMATCH")
    if env.timezone!=TIMEZONE:p.append("HARNESS_TIMEZONE_MISMATCH")
    if env.pythonhashseed!=PYTHONHASHSEED:p.append("HARNESS_PYTHONHASHSEED_MISMATCH")
    if env.fixture_random_seed!=FIXTURE_RANDOM_SEED:p.append("HARNESS_RANDOM_SEED_MISMATCH")
    if env.clock_model not in {"FROZEN_LOGICAL_CLOCK","EXPLICIT_CASE_TIMESTAMPS"}:p.append("HARNESS_CLOCK_MODEL_INVALID")
    if env.dependency_lock_method not in {"PIP_FREEZE","STDLIB_ONLY_PIP_UNAVAILABLE"}:p.append("HARNESS_DEPENDENCY_LOCK_METHOD_INVALID")
    for f in ("os_release_digest","uname_digest","dependency_lock_digest"):
        if len(getattr(env,f))!=64:p.append(f"HARNESS_ENV_DIGEST_INVALID:{f}")
    return p


def validate_binding(b:CaseRunBinding,*,plan_body_sha256:str,plan_packet_blob_sha:str,harness_blob_sha:str)->list[str]:
    p=[]
    if b.case_id not in CASE_IDS:p.append("CASE_ID_OUTSIDE_V24_I11")
    if b.plan_body_sha256!=plan_body_sha256:p.append("PLAN_BODY_SHA_MISMATCH")
    if b.plan_packet_blob_sha!=plan_packet_blob_sha:p.append("PLAN_PACKET_BLOB_SHA_MISMATCH")
    if b.harness_blob_sha!=harness_blob_sha:p.append("HARNESS_BLOB_SHA_MISMATCH")
    if b.harness_version!=HARNESS_VERSION:p.append("HARNESS_VERSION_MISMATCH")
    if b.design_sha!=FROZEN_V24_DESIGN_SHA:p.append("DESIGN_SHA_MISMATCH")
    if b.implementation_sha!=FROZEN_I10_IMPLEMENTATION_SHA:p.append("IMPLEMENTATION_SHA_MISMATCH")
    if b.implementation_tree!=FROZEN_I10_TREE:p.append("IMPLEMENTATION_TREE_MISMATCH")
    if b.governance_generation!=GOVERNANCE_GENERATION:p.append("GOVERNANCE_GENERATION_MISMATCH")
    if b.case_status not in CASE_STATUSES:p.append("CASE_STATUS_INVALID")
    if b.case_id in BLOCKED_CASES and b.case_status!="BLOCKED_BY_I1_SEMANTIC_QUALIFICATION":p.append("BLOCKED_CASE_STATUS_REQUIRED")
    if not b.target_module_blobs:p.append("TARGET_MODULE_BLOB_SET_REQUIRED")
    if len(b.fixture_digest)!=64:p.append("FIXTURE_DIGEST_INVALID")
    if len(b.environment_digest)!=64:p.append("ENVIRONMENT_DIGEST_INVALID")
    return p


def classify_negative(*,expected_endpoint:str,observed:GovernedEndpointObservation|None,effect:AuthorityEffectObservation|None,fixture_valid:bool,harness_valid:bool)->str:
    """No diagnostic-to-endpoint normalization is permitted."""
    if not fixture_valid:return "FAIL_FIXTURE_DEFECT"
    if not harness_valid:return "FAIL_HARNESS_DEFECT"
    if observed is None or observed.endpoint is None:return "FAIL_CODE_DEFECT"
    if observed.endpoint!=expected_endpoint:return "FAIL_CODE_DEFECT"
    if effect is None:return "FAIL_HARNESS_DEFECT"
    if effect.unauthorized_effect_delta!=0:return "FAIL_CODE_DEFECT"
    return "PASS"


def classify_conjunctive_negative(*,expected_endpoint:str,observation:ConjunctiveAssertionObservation|None,effect:AuthorityEffectObservation|None,fixture_valid:bool,harness_valid:bool)->str:
    if not fixture_valid:return "FAIL_FIXTURE_DEFECT"
    if not harness_valid:return "FAIL_HARNESS_DEFECT"
    if observation is None:return "FAIL_HARNESS_DEFECT"
    if observation.primary_endpoint.endpoint!=expected_endpoint:return "FAIL_CODE_DEFECT"
    if not observation.complete:return "FAIL_CODE_DEFECT"
    if effect is None:return "FAIL_HARNESS_DEFECT"
    if effect.unauthorized_effect_delta!=0:return "FAIL_CODE_DEFECT"
    return "PASS"
