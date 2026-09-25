#!/usr/bin/env python3
import hashlib, pathlib, subprocess

PROPOSAL_COMMIT="b0b7ddd9fb8c4dfe9775990ac27968c85ade75c1"
OUT=pathlib.Path("ig1-successor1-review")
OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-IG1-SUCCESSOR1-EARLY-REVIEW-PACKET.txt"

FILES=[
("governance-r8/R8-V15-R1-INTEGRATION-GATE1-SUCCESSOR1-PROPOSAL.json","SUCCESSOR1 PROPOSAL"),
("governance-r8/R8-V15-R1-INTEGRATION-GATE1-INDEPENDENT-REVIEW-001.txt","PREDECESSOR REVIEW 001"),
("governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-FALLBACK-002.json","ACTIVE FALLBACK-TO-3"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json","EXACT 120-ENTRY PATH/MODE/TYPE/BLOB ALLOWLIST"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-FULL-CHANGE-INVENTORY.json","FULL 904-PATH CANDIDATE CHANGE INVENTORY"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json","PREFLIGHT SUMMARY"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-PROPOSAL-PREFLIGHT-FAILURE-001.json","PRESERVED PREFLIGHT FAILURE 001"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-PROPOSAL-PREFLIGHT-FAILURE-002.json","PRESERVED PREFLIGHT FAILURE 002"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-PROPOSAL-PREFLIGHT-GREEN-001.json","PREFLIGHT GREEN"),
("tools/r8_v15_r1_ig1_successor1_materialize.py","EXACT PROPOSED MATERIALIZER"),
("governance-runtime/test_r8_v15_r1_ig1_integration_oracle.py","EXACT STRICT INTEGRATION ORACLE"),
(".github/workflows/r8-v15-r1-ig1-successor1-materialize.yml","EXACT PROPOSED MATERIALIZATION WORKFLOW"),
]

def sh(*args):
    return subprocess.check_output(args)

def show(path):
    return sh("git","show",f"{PROPOSAL_COMMIT}:{path}")

def blob(path):
    return sh("git","rev-parse",f"{PROPOSAL_COMMIT}:{path}").decode().strip()

header=f"""R8 v15-r1 — IG-1 MECHANICAL INTEGRATION SUCCESSOR1 — FRESH MANDATORY EARLY REVIEW

USE ONLY THIS FILE.
Do not use prior conversation history or model recollection.
This is a successor PROPOSAL REVIEW ONLY. No integration has been activated or executed.

EXACT SUCCESSOR PROPOSAL
proposal_id: R8V15R1-IG1-MECHANICAL-INTEGRATION-SUCCESSOR1
exact proposal commit: {PROPOSAL_COMMIT}
proposal blob SHA-1: e7de88a0814e97f960a696458767ce1629846692

PREDECESSOR DISPOSITION
Predecessor proposal commit: 181217d201a628991936042da5d64d98ad9f4bf7
Review 001: CHANGES_REQUIRED
Critical: 0
High: 4
Effect: predecessor activation prohibited; automatic fallback-to-3 activated.

CURRENT CADENCE STATE
Fallback-to-3 remains ACTIVE.
A clean review of this successor would count only as clean post-remediation review 1 of 2 for possible future cadence recovery.
It would NOT restore six-slice cadence automatically.
IG-1 is a separately reviewed phase gate, not low-risk slice batching.

SUCCESSOR PREFLIGHT HISTORY
- failure 001: self-referential forbidden-token text scanner defect; no materialization.
- failure 002: over-broad governance-history literal scanner defect; no materialization.
- retry 3: PASS, run/job 36161185432 / 108157862287.
- selected exact tree entries: 120.
- full changed paths inventoried: 904.
- collisions: 0.
- conflicting collisions: 0.
- activation artifact: absent.
- integration/materialization executed: NO.

REVIEW FOCUS
Adversarially determine whether the four High findings from Review 001 are actually remediated:

D1 — exact reviewed-file allowlist:
- exact per-candidate source commit;
- exact path + mode + type + blob;
- all 904 changed paths visible;
- only 120 selected;
- no runtime path discovery during integration.

D2 — false-green acceptance:
- exact imported test collection;
- S20-S22 expected 20 tests each; every other S8-S46 slice expected 16;
- total imported slice tests expected 636;
- inherited S1-S7 baseline expected 140;
- hard fail on skip/expected-failure/unexpected-success/xfail/not-collected/deselected/count mismatch;
- exact imported tree identity checked before tests.

D3 — integration-only machinery:
- inspect the exact materializer, strict oracle and workflow included below;
- determine whether they are genuinely mechanical/declarative;
- no direct production-validator import/call by integration machinery;
- no monkeypatch/import-hook/cross-slice semantic wiring;
- activation must bind exact proposal blob and exact machinery blobs.

D4 — rejected predecessors/unreviewed descendants:
- only exact reviewed successor source commits may be used;
- S20-S22 rejected predecessors are not materialization sources;
- repaired successors legitimately descend from rejected predecessors;
- exactly one selected original test entry per S20/S21/S22 is byte-identical to its rejected predecessor and is explicitly reaccepted by the reviewed successor lineage;
- any additional identical selected entry hard-fails.

Also review the Review-001 Medium/Low remediations:
- collision stop occurs before first byte materialization;
- tree identity includes mode, not just blob;
- reserved integration-only paths cannot collide with imported paths;
- runtime implementation governance-history file IO is prohibited/detected;
- no commit/push occurs until all 120 entries verify and strict oracle passes.

AUTHORITY BOUNDARY
A favorable review may authorize only USER ELIGIBILITY TO ACTIVATE the exact successor proposal.
It does not itself activate anything.
If later explicitly activated by user, Stage 1 may produce only:
INTEGRATED_IMPLEMENTATION_CANDIDATE_NON_AUTHORITATIVE_PENDING_FRESH_INDEPENDENT_REVIEW

Stage 2 semantic work remains NOT AUTHORIZED.
Runtime qualification, evidence promotion, release, deployment, production, policy, constitutional, root and terminal authority remain false.

REQUIRED OUTPUT — RETURN ONLY A-H

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_SUCCESSOR_IDENTITY
Include proposal ID, exact proposal commit/blob, allowlist blob, inventory blob, materializer blob, oracle blob, workflow blob, preflight green run/job, selected-entry count, inventory count, collision count, and fallback-to-3 state.

C. CRITICAL_FINDINGS

D. HIGH_FINDINGS

E. MEDIUM_LOW_FINDINGS

F. REMEDIATION_AND_PROTOCOL_ASSESSMENT
F1 Review001 D1 exact allowlist
F2 Review001 D2 false-green/test oracle
F3 Review001 D3 integration-only machinery
F4 Review001 D4 rejected predecessor/unreviewed descendant exclusion
F5 tree-entry mode/blob identity
F6 pre-materialization collision/reserved-path handling
F7 governance-history runtime-read boundary
F8 partial materialization/publish boundary
F9 exact activation proposal/review/machinery binding
F10 fresh independent review of exact integrated candidate before Stage 2
F11 semantic/currentness/qualification/evidence-promotion prohibition
F12 fallback-to-3 and recovery accounting
Identify any remaining concrete false-green or silent-authority path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State whether Stage 1 remains non-authoritative, Stage 2 remains separately gated, exact integrated bytes require fresh review, fallback-to-3 remains active, and whether a clean successor review counts as 1 of 2 toward cadence recovery.

H. FINAL_GATE
State exactly:
- IG-1 successor1 proposal may be explicitly activated by user: YES or NO.
- If YES, activation is NOT automatic and must bind exact proposal commit {PROPOSAL_COMMIT}.
- Stage 1 integrated output authority: NONE / non-authoritative pending fresh review.
- Stage 2 semantic integration authorized: NO.
- Six-slice cadence automatically restored: NO.
- Runtime/release/deployment/production/policy/constitutional/root/terminal authority granted: NO.

"""

with TARGET.open("wb") as fp:
    fp.write(header.encode())
    for path,label in FILES:
        b=show(path)
        fp.write(f"\n===== BEGIN {label} =====\npath={path}\nref={PROPOSAL_COMMIT}\ngit_blob_sha1={blob(path)}\nbyte_count={len(b)}\nsha256={hashlib.sha256(b).hexdigest()}\n".encode())
        fp.write(b)
        if not b.endswith(b"\n"): fp.write(b"\n")
        fp.write(f"===== END {label} =====\n".encode())

b=TARGET.read_bytes()
print(TARGET.name,len(b),hashlib.sha256(b).hexdigest())
