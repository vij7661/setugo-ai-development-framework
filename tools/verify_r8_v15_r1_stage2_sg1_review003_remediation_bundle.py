#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

TOOLS=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(TOOLS))
from validate_r8_v15_r1_stage2_sg1_activation_gate_parser import parse_review_contract

MANIFEST=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json")
BINDING=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json")
REVIEW1=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-001.txt")
REVIEW2=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
FAILURE=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-ATTEMPT-001-FAILED.json")
GATE=pathlib.Path(".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
PACKET=pathlib.Path("stage2-sg1-review/R8-V15-R1-STAGE2-SG1-REVIEW-003-PARSER-REMEDIATION-PACKET.txt")
ACTIVATION=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json")

EXPECTED_PROPOSAL={
    "id":"R8V15R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-001",
    "commit":"67c84138140e86ba4a85a954f368f4c0f7e9ef3c",
    "blob_sha1":"d1ebd1427d5dfb07348fda2f817aa7f3d20feb3b",
    "path":"governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-PROPOSAL.json",
}
EXPECTED_CANDIDATE={
    "commit":"4984f06a4420b76ad1ad475751aebda04a2d2c5c",
    "tree":"5a34e0d7db3e750dd5b0f722ccecc8014be189ef",
    "parent":"751162ee42c603cb6c84ee12021d16bab6fa626b",
}
EXPECTED_MACHINERY={
    "governance-runtime/test_r8_v15_r1_stage2_sg1_dependency_semantics.py":"15cb741fedd6f65d4f1cf5a5a3873e70649ed4ad",
    "tools/compare_r8_v15_r1_stage2_sg1_results.py":"097464a6b99bc79117501f7700d012ebeddd8675",
    ".github/workflows/r8-v15-r1-stage2-sg1-core.yml":"93ea0cccfdb1392ef38ee41dd053512372de0c87",
    "tools/verify_r8_v15_r1_ig1_successor3_exact_candidate.py":"dc8b76d6710dee27af4a3502b157853959d34ba7",
}
EXPECTED_REVIEW1_BLOB="9edfc2055588a218b3358530b94b0365768176d1"
EXPECTED_REVIEW2_BLOB="fa4e783d698db8701990a0eb92cbf34e1f3054bb"
EXPECTED_FAILED_GATE="c09f5d75b70bf5f9f928a79d1dd094f11ff24279"
EXPECTED_CURRENT_GATE="9adc02a0f29a8dd7b3e88c51decc8dd066c3e577"
EXPECTED_FAILURE_BLOB="241809c0965541f65e3a81c12d3f475719beb011"
EXPECTED_REVIEW3="governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt"

def git_blob(path: str) -> str:
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def fail(message: str) -> None:
    raise SystemExit(message)

def main() -> None:
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    binding=json.loads(BINDING.read_text(encoding="utf-8"))
    failure=json.loads(FAILURE.read_text(encoding="utf-8"))

    if manifest.get("status")!="PARSER_REMEDIATION_REQUIRES_FRESH_REVIEW_003_NOT_ACTIVE":
        fail("manifest remediation status mismatch")
    if manifest.get("authority_effect")!="NONE":
        fail("manifest authority effect mismatch")
    if manifest.get("proposal")!=EXPECTED_PROPOSAL:
        fail("proposal identity mismatch")
    if manifest.get("candidate")!=EXPECTED_CANDIDATE:
        fail("candidate identity mismatch")
    if manifest.get("machinery")!=EXPECTED_MACHINERY:
        fail("semantic machinery map changed")
    for path,blob in EXPECTED_MACHINERY.items():
        if git_blob(path)!=blob:
            fail(f"semantic machinery blob changed: {path}")

    if git_blob(str(REVIEW1))!=EXPECTED_REVIEW1_BLOB:
        fail("Review 001 changed")
    if git_blob(str(REVIEW2))!=EXPECTED_REVIEW2_BLOB:
        fail("Review 002 changed")
    parse_review_contract(REVIEW2.read_text(encoding="utf-8"))

    if git_blob(str(FAILURE))!=EXPECTED_FAILURE_BLOB:
        fail("failed-attempt evidence changed")
    if failure.get("github_actions_run_id")!=36190374209 or failure.get("verify_job_id")!=108253787018:
        fail("failed-attempt run/job mismatch")
    if failure.get("status")!="FAILED_CLOSED_BEFORE_SEMANTIC_EXECUTION":
        fail("failed-attempt status mismatch")
    if failure.get("semantic_execution_performed") is not False or failure.get("reusable_core_reached") is not False:
        fail("failed-attempt execution boundary mismatch")
    if failure.get("activation_gate_blob_sha1")!=EXPECTED_FAILED_GATE:
        fail("failed-attempt prior gate mismatch")
    if failure.get("exact_failure")!="review broader authority declaration is not exactly one NO":
        fail("failed-attempt exact failure mismatch")

    if ACTIVATION.exists():
        fail("activation artifact must be absent during Review 003 remediation")
    if pathlib.Path(EXPECTED_REVIEW3).exists():
        fail("Review 003 must remain external and absent before review")

    gate_blob=git_blob(str(GATE))
    if gate_blob!=EXPECTED_CURRENT_GATE:
        fail("current repaired gate blob mismatch")
    if manifest["activation_gate"]["blob_sha1"]!=gate_blob:
        fail("manifest current gate mismatch")
    gate=GATE.read_text(encoding="utf-8")
    if f'EXPECTED_REVIEW_PATH="{EXPECTED_REVIEW3}"' not in gate:
        fail("gate does not require Review 003")
    for token in (
        r'Stage2 SG-1 may be explicitly activated by user:\s*YES\.?\s*$',
        r'Stage2 SG-1 may be explicitly activated by user:\s*NO\.?\s*$',
        r'Broader Stage2 semantic authority granted:\s*NO\.?\s*$',
        r'Broader Stage2 semantic authority granted:\s*YES\.?\s*$',
    ):
        if token not in gate:
            fail(f"missing repaired punctuation parser token: {token}")

    if binding["activation_gate"]["blob_sha1"]!=gate_blob:
        fail("binding gate blob mismatch")
    if binding["expected_review"]["path"]!=EXPECTED_REVIEW3:
        fail("binding does not require Review 003")
    if binding["expected_review"].get("blob_sha1") is not None:
        fail("Review 003 blob must be pending")
    if binding["expected_review"]["required_disposition"]!="BOUNDED_PASS":
        fail("Review 003 disposition requirement mismatch")
    if binding["expected_review"]["required_critical_findings"]!=0 or binding["expected_review"]["required_high_findings"]!=0:
        fail("Review 003 finding requirements mismatch")
    if binding["expected_review"]["required_final_gate"]!="YES":
        fail("Review 003 final gate requirement mismatch")
    if binding.get("activation_artifact_exists") is not False or binding.get("semantic_execution_performed") is not False:
        fail("binding activation/execution state mismatch")

    reviews=manifest["reviews"]
    if reviews["historical_review_002"]["blob_sha1"]!=EXPECTED_REVIEW2_BLOB:
        fail("manifest Review 002 history mismatch")
    if reviews["historical_review_002"]["reviewed_activation_gate_blob_sha1"]!=EXPECTED_FAILED_GATE:
        fail("manifest Review 002 gate history mismatch")
    if reviews["expected_fresh_review_003"]["path"]!=EXPECTED_REVIEW3 or reviews["expected_fresh_review_003"].get("blob_sha1") is not None:
        fail("manifest Review 003 pending state mismatch")

    hist=manifest.get("activation_attempt_history",[])
    if len(hist)!=1 or hist[0].get("evidence_blob_sha1")!=EXPECTED_FAILURE_BLOB or hist[0].get("semantic_execution_performed") is not False:
        fail("activation-attempt history mismatch")

    gov=manifest["governance"]
    if gov["authority_boundary"]!="LOCAL DEPENDENCY SEMANTIC FALSIFICATION ONLY":
        fail("authority boundary mismatch")
    if gov["fallback_to_3"]!="ACTIVE" or gov["six_slice_cadence_restored"] is not False:
        fail("cadence boundary mismatch")
    if gov["activation_artifact_exists"] is not False or gov["semantic_execution_performed"] is not False:
        fail("activation/execution governance state mismatch")
    if gov["broader_stage2_authorized"] is not False:
        fail("broader Stage2 authority mismatch")
    if gov["runtime_release_deployment_production_policy_constitutional_root_terminal_authority"] is not False:
        fail("downstream authority mismatch")

    if not PACKET.exists():
        fail("Review 003 remediation packet missing")
    packet=PACKET.read_text(encoding="utf-8")
    header=packet.split("===== BEGIN",1)[0]
    for required in (
        EXPECTED_REVIEW3,
        EXPECTED_CURRENT_GATE,
        EXPECTED_FAILED_GATE,
        EXPECTED_REVIEW2_BLOB,
        "36190374209 / 108253787018",
        "NO SG-1 semantic execution occurred in the failed attempt.",
        "DO NOT STOP AFTER THE FIRST FINDING.",
        "a NEW explicit user approval must bind",
    ):
        if required not in header:
            fail(f"packet header missing: {required}")
    if "Stage2 SG-1 may be explicitly activated by user: YES or NO." not in header:
        fail("packet final-gate instruction missing")
    if "Broader Stage2 semantic authority granted: NO." not in header:
        fail("packet broader authority boundary missing")

    print(json.dumps({
        "status":"PASS",
        "current_gate_blob":gate_blob,
        "review_002_blob":EXPECTED_REVIEW2_BLOB,
        "review_003_path":EXPECTED_REVIEW3,
        "activation_artifact_exists":False,
        "semantic_execution_performed":False,
        "failed_attempt_run":36190374209,
        "failed_attempt_job":108253787018,
        "broader_stage2_authorized":False,
    },sort_keys=True))

if __name__=="__main__":
    main()
