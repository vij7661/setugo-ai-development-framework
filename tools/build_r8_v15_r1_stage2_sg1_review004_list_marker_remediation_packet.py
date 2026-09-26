#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, subprocess

MANIFEST_PATH=pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json")
MANIFEST=json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
PROPOSAL=MANIFEST["proposal"]
CANDIDATE=MANIFEST["candidate"]
REVIEW4=MANIFEST["reviews"]["expected_fresh_review_004"]
OUT=pathlib.Path("stage2-sg1-review")
OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-STAGE2-SG1-REVIEW-004-LIST-MARKER-REMEDIATION-PACKET.txt"

CURRENT_FILES=[
("governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-PROPOSAL.json","SG-1 PROPOSAL CONTRACT"),
("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json","CURRENT REVIEW/ACTIVATION MANIFEST"),
("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json","CURRENT ACTIVATION-GATE BINDING"),
("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-001.txt","HISTORICAL REVIEW 001"),
("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt","HISTORICAL REVIEW 002"),
("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt","HISTORICAL REVIEW 003"),
("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-ATTEMPT-001-FAILED.json","FAILED-CLOSED ACTIVATION ATTEMPT 001"),
("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-ATTEMPT-002-FAILED.json","FAILED-CLOSED ACTIVATION ATTEMPT 002"),
(".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml","CURRENT REPAIRED ACTIVATION GATE"),
("tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py","CURRENT PARSER REGRESSION VALIDATOR"),
("governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-SURFACE.json","EXACT DEPENDENCY SEMANTIC SURFACE"),
("governance-runtime/test_r8_v15_r1_stage2_sg1_dependency_semantics.py","UNCHANGED 18-CASE SG-1 HARNESS"),
("tools/compare_r8_v15_r1_stage2_sg1_results.py","UNCHANGED RESULT COMPARATOR"),
(".github/workflows/r8-v15-r1-stage2-sg1-core.yml","UNCHANGED SG-1 REUSABLE CORE"),
("tools/verify_r8_v15_r1_ig1_successor3_exact_candidate.py","UNCHANGED STAGE1 REGRESSION VERIFIER"),
("governance-r8/R8-V15-R1-STAGE2-SG1-PROPOSAL-PREFLIGHT-GREEN-001.json","STATIC PREFLIGHT EVIDENCE"),
]

def sh(*args): return subprocess.check_output(args)
def show(rev,path): return sh("git","show",f"{rev}:{path}")
def blob(rev,path): return sh("git","rev-parse",f"{rev}:{path}").decode().strip()

head=sh("git","rev-parse","HEAD").decode().strip()
gate_blob=blob(head,".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
if gate_blob != MANIFEST["activation_gate"]["blob_sha1"]:
    raise SystemExit("current gate blob does not match manifest")
if REVIEW4["blob_sha1"] is not None:
    raise SystemExit("Review 004 must remain pending")
if pathlib.Path(REVIEW4["path"]).exists():
    raise SystemExit("Review 004 unexpectedly exists")
if pathlib.Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json").exists():
    raise SystemExit("activation artifact must be absent")

header=f"""R8 v15-r1 — STAGE2 SG-1 — FRESH REVIEW 004 — H-SECTION LIST-MARKER REMEDIATION

USE ONLY THIS FILE.
Do not use prior conversation history, model recollection, GitHub access, or external APIs.
This is a narrow remediation review after activation attempt 002 failed closed.
NO SG-1 semantic execution occurred in activation attempt 001 or activation attempt 002.
NO activation artifact exists on this remediation branch.

WHY REVIEW 004 EXISTS
Review 003 returned BOUNDED_PASS for activation-gate blob 9adc02a0f29a8dd7b3e88c51decc8dd066c3e577.
The user explicitly approved that exact gate and Review 003.
Activation attempt 002 ran at commit 0e90bbe5ad2213412d4a3cc287776b2c1efaaaf7.
GitHub Actions run/job: 36223537668 / 108353145716.
The reusable SG-1 core job 108353161400 was SKIPPED.
Exact verify failure:
  review activation declaration is not exactly one YES

The Review 003 H section used the packet-required list form:
  - Stage2 SG-1 may be explicitly activated by user: YES.
The prior parser accepted optional punctuation but did not accept the leading list marker.
This is classified as a false-negative H-section list-marker compatibility defect.
It is NOT an SG-1 semantic-test failure.

NARROW REPAIR
The parser now accepts optional leading whitespace and one optional "- " list marker for the two H declarations, plus the already-reviewed optional single trailing period.
It also expands the existing hidden Critical/High line guard to catch optional list markers and the phrase HIGH FINDING / CRITICAL FINDING.
It still requires exactly one ordered A-H document, clean C/D sections, exactly one activation YES declaration, exactly one broader Stage2 NO declaration, rejects contradictory activation NO or broader Stage2 YES anywhere, and rejects duplicate/reordered A-H sections.
The exact preserved Review 002 and Review 003 are both run through the regression validator.

EXACT CURRENT IDENTITIES
proposal ID: {PROPOSAL["id"]}
proposal commit: {PROPOSAL["commit"]}
proposal blob: {PROPOSAL["blob_sha1"]}
candidate: {CANDIDATE["commit"]}
candidate tree: {CANDIDATE["tree"]}
candidate parent: {CANDIDATE["parent"]}
current remediation bundle commit: {head}
attempt 001 run/job: 36190374209 / 108253787018
attempt 002 run/job: 36223537668 / 108353145716
attempt 002 skipped core job: 108353161400
prior gate reviewed by Review 003: 9adc02a0f29a8dd7b3e88c51decc8dd066c3e577
current repaired activation-gate blob: {gate_blob}
Review 003 blob: 378ffe70e131b6c63e95f4142596ae091ba37ebe
expected fresh Review 004 path: {REVIEW4["path"]}

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
A future successful SG-1 execution still requires fresh independent post-execution review before SG-1 closure or any later Stage2 gate.

REVIEW FOCUS
DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings before the final disposition.
Review:
1. both failed activation attempts are preserved and neither reached SG-1 semantic execution;
2. the current delta is limited to list-marker compatibility, hidden-finding guard hardening, fresh Review 004 path, and successor branch binding;
3. accepting one optional "- " prefix plus one optional trailing period cannot create an activation/broader-authority false-green;
4. duplicate/reordered A-H, contradictory H declarations, malformed punctuation, hidden CRITICAL/HIGH and HIGH FINDING/CRITICAL FINDING forms remain rejected;
5. exact Review 002 and exact Review 003 now parse without editing either review;
6. proposal/candidate/semantic machinery remain unchanged;
7. prior approvals cannot authorize the new gate blob;
8. fresh Review 004 + NEW explicit user approval are required before another activation attempt;
9. activation artifact is absent;
10. authority/cadence/post-execution-review boundaries remain unchanged.

REQUIRED OUTPUT — RETURN ONLY A-H

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_REMEDIATION_IDENTITY
Include proposal/candidate identities, both failed activation run/job identities, Review 003 blob, prior gate blob, current gate blob, current remediation bundle commit, and unchanged semantic machinery blobs.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_LOW_FINDINGS
Enumerate all remaining findings.

F. REMEDIATION_ASSESSMENT
F1 failed-attempt preservation and no semantic execution
F2 narrow list-marker parser delta
F3 exact Review 002 + Review 003 regression
F4 duplicate/reordered/contradictory/hidden-finding rejection
F5 unchanged proposal/candidate/semantic machinery
F6 stale prior approvals cannot authorize new gate
F7 Review 004 + new explicit approval requirement
F8 authority/cadence/post-execution-review boundary

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State that remediation grants no authority; SG-1 inactive; broader Stage2 unauthorized; fallback-to-3 ACTIVE; six-slice cadence not restored.

H. FINAL_GATE
State exactly:
- Stage2 SG-1 may be explicitly activated by user: YES or NO.
- If YES, activation is NOT automatic and a NEW explicit user approval must bind proposal commit {PROPOSAL["commit"]}, proposal blob {PROPOSAL["blob_sha1"]}, fresh Review-004 blob, and current activation-gate blob {gate_blob}.
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
        if not b.endswith(b"\n"): fp.write(b"\n")
        fp.write(f"===== END {label} =====\n".encode())

data=TARGET.read_bytes()
print(TARGET.name,len(data),hashlib.sha256(data).hexdigest())
