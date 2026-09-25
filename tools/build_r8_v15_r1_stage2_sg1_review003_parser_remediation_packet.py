#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

MANIFEST_PATH=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json")
MANIFEST=json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
PROPOSAL=MANIFEST["proposal"]
CANDIDATE=MANIFEST["candidate"]
REVIEW3=MANIFEST["reviews"]["expected_fresh_review_003"]
FAILED_COMMIT="6acc2d3c934d44d20a334b4c0474f763f535586b"
FAILED_GATE="c09f5d75b70bf5f9f928a79d1dd094f11ff24279"
FAILED_RUN="36190374209"
FAILED_JOB="108253787018"

OUT=pathlib.Path("stage2-sg1-review")
OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-STAGE2-SG1-REVIEW-003-PARSER-REMEDIATION-PACKET.txt"

CURRENT_FILES=[
    ("governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-PROPOSAL.json","SG-1 PROPOSAL CONTRACT"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json","CURRENT REVIEW/ACTIVATION MANIFEST"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json","CURRENT ACTIVATION-GATE BINDING"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-001.txt","HISTORICAL REVIEW 001 — CHANGES_REQUIRED"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt","HISTORICAL REVIEW 002 — BOUNDED_PASS FOR PRIOR GATE"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-ATTEMPT-001-FAILED.json","FAILED-CLOSED ACTIVATION ATTEMPT 001"),
    (".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml","REPAIRED ACTIVATION GATE REQUIRING REVIEW 003"),
    ("tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py","PARSER REGRESSION VALIDATOR"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-SURFACE.json","EXACT DEPENDENCY SEMANTIC SURFACE"),
    ("governance-runtime/test_r8_v15_r1_stage2_sg1_dependency_semantics.py","UNCHANGED 18-CASE SG-1 HARNESS"),
    ("tools/compare_r8_v15_r1_stage2_sg1_results.py","UNCHANGED FORWARD/REVERSE COMPARATOR"),
    (".github/workflows/r8-v15-r1-stage2-sg1-core.yml","UNCHANGED SG-1 REUSABLE CORE"),
    ("tools/verify_r8_v15_r1_ig1_successor3_exact_candidate.py","UNCHANGED STAGE1 REGRESSION VERIFIER"),
    ("governance-r8/R8-V15-R1-STAGE2-SG1-PROPOSAL-PREFLIGHT-GREEN-001.json","STATIC PREFLIGHT EVIDENCE"),
]

def sh(*args):
    return subprocess.check_output(args)

def show(rev,path):
    return sh("git","show",f"{rev}:{path}")

def blob(rev,path):
    return sh("git","rev-parse",f"{rev}:{path}").decode().strip()

head=sh("git","rev-parse","HEAD").decode().strip()
gate_blob=blob(head,".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
if gate_blob != MANIFEST["activation_gate"]["blob_sha1"]:
    raise SystemExit("current gate blob does not match manifest")
if REVIEW3["blob_sha1"] is not None:
    raise SystemExit("Review 003 must remain pending before independent review")
if pathlib.Path(REVIEW3["path"]).exists():
    raise SystemExit("Review 003 unexpectedly exists")
if pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json").exists():
    raise SystemExit("activation artifact must be absent during remediation review")

header=f"""R8 v15-r1 — STAGE2 SG-1 — FRESH REVIEW 003 — ACTIVATION PARSER REMEDIATION

USE ONLY THIS FILE.
Do not use prior conversation history, model recollection, GitHub access, or external APIs.
This is a NARROW REMEDIATION REVIEW after a failed-closed activation attempt.
NO SG-1 semantic execution occurred in the failed attempt.
NO SG-1 semantic execution has occurred since.
NO activation artifact exists on this remediation successor branch.

WHY REVIEW 003 EXISTS
Review 002 was BOUNDED_PASS for activation-gate blob {FAILED_GATE}.
The user explicitly approved that exact gate and Review 002.
Activation attempt 001 ran at commit {FAILED_COMMIT}, GitHub Actions run/job {FAILED_RUN} / {FAILED_JOB}.
The activation verify job failed closed BEFORE the reusable SG-1 core because Review 002 states:
  Broader Stage2 semantic authority granted: NO.
with a trailing period, while the old activation parser required NO without a trailing period.
Exact failure:
  review broader authority declaration is not exactly one NO

This is classified as a false-negative punctuation-compatibility defect.
It is NOT an SG-1 semantic-test failure.
The failed activation attempt is preserved in the packet.

NARROW REPAIR
The activation parser now accepts the exact bounded declaration tokens with an optional single trailing period:
- activation YES or YES.
- contradictory activation NO or NO.
- broader Stage2 NO or NO.
- prohibited broader Stage2 YES or YES.
It still requires exactly one ordered A-H document, clean C/D sections, exactly one activation YES declaration, exactly one broader Stage2 NO declaration, rejects contradictions, rejects duplicate/reordered A-H sections, and rejects Critical/High findings outside C/D.
The exact preserved Review 002 is run through the parser regression validator.

EXACT CURRENT IDENTITIES
proposal ID: {PROPOSAL["id"]}
proposal commit: {PROPOSAL["commit"]}
proposal blob: {PROPOSAL["blob_sha1"]}
candidate: {CANDIDATE["commit"]}
candidate tree: {CANDIDATE["tree"]}
candidate parent: {CANDIDATE["parent"]}
current remediation bundle commit: {head}
prior reviewed/failed gate blob: {FAILED_GATE}
current repaired activation-gate blob: {gate_blob}
Review 002 blob: fa4e783d698db8701990a0eb92cbf34e1f3054bb
expected fresh Review 003 path: {REVIEW3["path"]}

UNCHANGED SEMANTIC MACHINERY
harness: 15cb741fedd6f65d4f1cf5a5a3873e70649ed4ad
comparator: 097464a6b99bc79117501f7700d012ebeddd8675
reusable core: 93ea0cccfdb1392ef38ee41dd053512372de0c87
Stage1 verifier: dc8b76d6710dee27af4a3502b157853959d34ba7
semantic surface: 94e3275edbb32baca640966830352f5e6c9f4ada
preflight: 963b3e29ce2cdb2621d83e4e9f3f657a45222ad6

AUTHORITY
This repair grants NO authority.
SG-1 is NOT active.
Broader Stage2 remains unauthorized.
Fallback-to-3 remains ACTIVE.
Six-slice cadence remains NOT restored.
Runtime/release/deployment/production/policy/constitutional/root/terminal authority remains NO.
A future successful SG-1 execution would still require fresh independent post-execution review before SG-1 closure or any later Stage2 gate.

REVIEW FOCUS
DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings before the final disposition.
Review specifically:
1. whether the preserved failed attempt proves fail-closed-before-semantic-execution;
2. whether the repair is narrowly limited to punctuation compatibility plus the required fresh-review path/branch successor;
3. whether accepting one optional trailing period introduces any false-green or contradictory-declaration path;
4. whether duplicate/reordered A-H, hidden Critical/High, and contradictory H declarations remain rejected;
5. whether exact Review 002 now parses successfully without editing Review 002;
6. whether proposal/candidate/semantic machinery identities remain unchanged;
7. whether the old explicit approval cannot authorize the new gate blob;
8. whether Review 003 and a NEW explicit user approval are required before another activation attempt;
9. whether activation artifact is absent on the remediation branch;
10. whether authority and cadence boundaries remain unchanged.

REQUIRED OUTPUT — RETURN ONLY A-H

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_REMEDIATION_IDENTITY
Include proposal ID/commit/blob, candidate/tree/parent, failed activation commit/run/job, prior gate blob, current gate blob, Review 002 blob, current remediation bundle commit, and unchanged semantic machinery blobs.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_LOW_FINDINGS
Enumerate all remaining findings.

F. REMEDIATION_ASSESSMENT
F1 failed-attempt preservation and no semantic execution
F2 narrow parser delta
F3 exact Review 002 punctuation regression
F4 duplicate/reordered/contradictory/hidden-finding rejection
F5 unchanged proposal/candidate/semantic machinery
F6 stale prior approval cannot authorize new gate
F7 Review 003 + new explicit approval requirement
F8 authority/cadence/post-execution-review boundary

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State that this remediation grants no authority; SG-1 remains inactive; broader Stage2 remains unauthorized; fallback-to-3 remains ACTIVE; six-slice cadence remains not restored.

H. FINAL_GATE
State exactly:
- Stage2 SG-1 may be explicitly activated by user: YES or NO.
- If YES, activation is NOT automatic and a NEW explicit user approval must bind proposal commit {PROPOSAL["commit"]}, proposal blob {PROPOSAL["blob_sha1"]}, fresh Review-003 blob, and current activation-gate blob {gate_blob}.
- SG-1 execution authority if later activated: LOCAL DEPENDENCY SEMANTIC FALSIFICATION ONLY.
- Broader Stage2 semantic authority granted: NO.
- Automatic six-slice cadence restoration: NO.
- Runtime/release/deployment/production/policy/constitutional/root/terminal authority granted: NO.

"""

with TARGET.open("wb") as fp:
    fp.write(header.encode())
    for path,label in CURRENT_FILES:
        b=show(head,path)
        fp.write(f"\n===== BEGIN {label} =====\npath={path}\nref={head}\ngit_blob_sha1={blob(head,path)}\nbyte_count={len(b)}\nsha256={hashlib.sha256(b).hexdigest()}\n".encode())
        fp.write(b)
        if not b.endswith(b"\n"):
            fp.write(b"\n")
        fp.write(f"===== END {label} =====\n".encode())

    old_gate=show(FAILED_COMMIT,".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
    fp.write(f"\n===== BEGIN PRIOR FAILED ACTIVATION GATE =====\npath=.github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml\nref={FAILED_COMMIT}\ngit_blob_sha1={blob(FAILED_COMMIT,'.github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml')}\nbyte_count={len(old_gate)}\nsha256={hashlib.sha256(old_gate).hexdigest()}\n".encode())
    fp.write(old_gate)
    if not old_gate.endswith(b"\n"):
        fp.write(b"\n")
    fp.write(b"===== END PRIOR FAILED ACTIVATION GATE =====\n")

    old_activation=show(FAILED_COMMIT,"governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json")
    fp.write(f"\n===== BEGIN PRIOR FAILED ACTIVATION ARTIFACT =====\npath=governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json\nref={FAILED_COMMIT}\ngit_blob_sha1={blob(FAILED_COMMIT,'governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json')}\nbyte_count={len(old_activation)}\nsha256={hashlib.sha256(old_activation).hexdigest()}\n".encode())
    fp.write(old_activation)
    if not old_activation.endswith(b"\n"):
        fp.write(b"\n")
    fp.write(b"===== END PRIOR FAILED ACTIVATION ARTIFACT =====\n")

data=TARGET.read_bytes()
print(TARGET.name, len(data), hashlib.sha256(data).hexdigest())
