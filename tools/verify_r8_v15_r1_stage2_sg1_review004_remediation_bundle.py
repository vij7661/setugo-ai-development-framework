#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, sys

TOOLS=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(TOOLS))
from validate_r8_v15_r1_stage2_sg1_activation_gate_parser import parse_review_contract

MANIFEST=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json")
BINDING=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json")
GATE=pathlib.Path(".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
PACKET=pathlib.Path("stage2-sg1-review/R8-V15-R1-STAGE2-SG1-REVIEW-004-LIST-MARKER-REMEDIATION-PACKET.txt")
REVIEW2=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
REVIEW3=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt")
FAIL1=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-ATTEMPT-001-FAILED.json")
FAIL2=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-ATTEMPT-002-FAILED.json")
ACT=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json")
REVIEW4=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-004.txt")

EXPECTED_GATE="5d75c4b5c85fec075812c819c979e7048df8cd7f"
EXPECTED_BINDING="88d76f7f5592a777177c9006a474824a1064c348"
EXPECTED_MANIFEST="0d25a2d3851673f1b2943a8b4bfdf9b11dfabd99"
EXPECTED_REVIEW2="fa4e783d698db8701990a0eb92cbf34e1f3054bb"
EXPECTED_REVIEW3="378ffe70e131b6c63e95f4142596ae091ba37ebe"
EXPECTED_FAIL1="241809c0965541f65e3a81c12d3f475719beb011"
EXPECTED_FAIL2="777763a679f0dfd4fd1c3d7e472a5e6ea373dbbf"
EXPECTED_REVIEW4="governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-004.txt"

def blob(path:str)->str:
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def fail(msg:str)->None:
    raise SystemExit(msg)

def main()->None:
    if blob(str(GATE))!=EXPECTED_GATE: fail("gate blob mismatch")
    if blob(str(BINDING))!=EXPECTED_BINDING: fail("binding blob mismatch")
    if blob(str(MANIFEST))!=EXPECTED_MANIFEST: fail("manifest blob mismatch")
    if blob(str(REVIEW2))!=EXPECTED_REVIEW2: fail("Review 002 changed")
    if blob(str(REVIEW3))!=EXPECTED_REVIEW3: fail("Review 003 changed")
    if blob(str(FAIL1))!=EXPECTED_FAIL1: fail("attempt 001 evidence changed")
    if blob(str(FAIL2))!=EXPECTED_FAIL2: fail("attempt 002 evidence changed")
    if ACT.exists(): fail("activation artifact must be absent")
    if REVIEW4.exists(): fail("Review 004 must remain absent before independent review")

    parse_review_contract(REVIEW2.read_text(encoding="utf-8"))
    parse_review_contract(REVIEW3.read_text(encoding="utf-8"))

    f1=json.loads(FAIL1.read_text(encoding="utf-8"))
    f2=json.loads(FAIL2.read_text(encoding="utf-8"))
    if f1["status"]!="FAILED_CLOSED_BEFORE_SEMANTIC_EXECUTION" or f1["semantic_execution_performed"] is not False:
        fail("attempt 001 execution boundary mismatch")
    if f2["status"]!="FAILED_CLOSED_BEFORE_SEMANTIC_EXECUTION" or f2["semantic_execution_performed"] is not False or f2["reusable_core_reached"] is not False:
        fail("attempt 002 execution boundary mismatch")
    if f2["exact_failure"]!="review activation declaration is not exactly one YES":
        fail("attempt 002 exact failure mismatch")

    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    b=json.loads(BINDING.read_text(encoding="utf-8"))
    if m["status"]!="H_SECTION_LIST_MARKER_REMEDIATION_REQUIRES_FRESH_REVIEW_004_NOT_ACTIVE":
        fail("manifest status mismatch")
    if m["authority_effect"]!="NONE": fail("manifest authority effect mismatch")
    if m["activation_gate"]["blob_sha1"]!=EXPECTED_GATE: fail("manifest gate mismatch")
    if m["activation_binding"]["blob_sha1"]!=EXPECTED_BINDING: fail("manifest binding mismatch")
    if m["reviews"]["historical_review_003"]["blob_sha1"]!=EXPECTED_REVIEW3: fail("manifest Review 003 history mismatch")
    if m["reviews"]["expected_fresh_review_004"]["path"]!=EXPECTED_REVIEW4 or m["reviews"]["expected_fresh_review_004"]["blob_sha1"] is not None:
        fail("manifest Review 004 pending state mismatch")
    if len(m["activation_attempt_history"])!=2 or any(x["semantic_execution_performed"] is not False for x in m["activation_attempt_history"]):
        fail("activation attempt history mismatch")
    g=m["governance"]
    if g["fallback_to_3"]!="ACTIVE" or g["six_slice_cadence_restored"] is not False:
        fail("cadence mismatch")
    if g["activation_artifact_exists"] is not False or g["semantic_execution_performed"] is not False or g["broader_stage2_authorized"] is not False:
        fail("authority/execution mismatch")

    if b["activation_gate"]["blob_sha1"]!=EXPECTED_GATE: fail("binding gate mismatch")
    if b["expected_review"]["path"]!=EXPECTED_REVIEW4 or b["expected_review"]["blob_sha1"] is not None:
        fail("binding Review 004 pending state mismatch")
    if b["expected_review"]["required_disposition"]!="BOUNDED_PASS" or b["expected_review"]["required_critical_findings"]!=0 or b["expected_review"]["required_high_findings"]!=0 or b["expected_review"]["required_final_gate"]!="YES":
        fail("binding Review 004 requirements mismatch")
    if b["activation_artifact_exists"] is not False or b["semantic_execution_performed"] is not False or b["stage2_sg1_authorized"] is not False:
        fail("binding authority state mismatch")

    gate=GATE.read_text(encoding="utf-8")
    if f'EXPECTED_REVIEW_PATH="{EXPECTED_REVIEW4}"' not in gate: fail("gate Review 004 path mismatch")
    for required in (
        r'^\s*(?:-\s*)?Stage2 SG-1 may be explicitly activated by user:\s*YES\.?\s*$',
        r'^\s*(?:-\s*)?Stage2 SG-1 may be explicitly activated by user:\s*NO\.?\s*$',
        r'^\s*(?:-\s*)?Broader Stage2 semantic authority granted:\s*NO\.?\s*$',
        r'^\s*(?:-\s*)?Broader Stage2 semantic authority granted:\s*YES\.?\s*$',
        r'^\s*(?:-\s*)?(?:CRITICAL|HIGH)(?:\s+FINDING)?\s*:'
    ):
        if required not in gate: fail("gate parser token missing: "+required)

    if not PACKET.exists(): fail("Review 004 packet missing")
    p=PACKET.read_text(encoding="utf-8")
    header=p.split("===== BEGIN",1)[0]
    for required in (
        EXPECTED_GATE, EXPECTED_REVIEW3, EXPECTED_REVIEW4,
        "36223537668 / 108353145716",
        "108353161400",
        "DO NOT STOP AFTER THE FIRST FINDING.",
        "a NEW explicit user approval must bind",
        "NO SG-1 semantic execution occurred in activation attempt 001 or activation attempt 002."
    ):
        if required not in header: fail("packet header missing: "+required)

    print(json.dumps({
        "status":"PASS",
        "current_gate_blob":EXPECTED_GATE,
        "review_002_blob":EXPECTED_REVIEW2,
        "review_003_blob":EXPECTED_REVIEW3,
        "review_004_path":EXPECTED_REVIEW4,
        "attempt_001_run":36190374209,
        "attempt_002_run":36223537668,
        "activation_artifact_exists":False,
        "semantic_execution_performed":False,
        "broader_stage2_authorized":False
    },sort_keys=True))

if __name__=="__main__":
    main()
