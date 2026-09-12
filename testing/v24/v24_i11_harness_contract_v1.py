"""WDPC V24 I11 falsification harness contract.

Schema/invariant definitions only. Importing this module executes no WDPC case.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import hashlib, json

HARNESS_ID="WDPC-V24-I11-HARNESS"
HARNESS_VERSION="1.0.0-PLAN-REVIEW"
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
EXECUTION_CLASSES={"REFERENCE_HARNESS","REFERENCE_MECHANISM_ONLY","HYBRID_EXTERNAL_REQUIRED","EXTERNAL_MANUAL_REQUIRED","MANUAL_SEMANTIC_REQUIRED","STATIC_OR_MANUAL_REQUIRED","BLOCKED_BY_I1_SEMANTIC_QUALIFICATION"}
CASE_IDS=tuple(f"WDPC-{i}" for i in range(431,507))

def digest(v:Any)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

@dataclass(frozen=True)
class GovernedEndpointObservation:
    endpoint:str|None
    emission_surface:str
    raw_result_digest:str
    internal_diagnostics:tuple[str,...]=()

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


def validate_environment(env:EnvironmentIdentity)->list[str]:
    p=[]
    if not env.python_version.startswith(PYTHON_RUNTIME):p.append("HARNESS_RUNTIME_VERSION_MISMATCH")
    if env.timezone!=TIMEZONE:p.append("HARNESS_TIMEZONE_MISMATCH")
    if env.pythonhashseed!=PYTHONHASHSEED:p.append("HARNESS_PYTHONHASHSEED_MISMATCH")
    if env.fixture_random_seed!=FIXTURE_RANDOM_SEED:p.append("HARNESS_RANDOM_SEED_MISMATCH")
    if env.clock_model not in {"FROZEN_LOGICAL_CLOCK","EXPLICIT_CASE_TIMESTAMPS"}:p.append("HARNESS_CLOCK_MODEL_INVALID")
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
