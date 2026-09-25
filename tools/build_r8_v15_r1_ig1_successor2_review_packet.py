#!/usr/bin/env python3
import hashlib, pathlib, subprocess

PROPOSAL_COMMIT="f4b33737ff67970d1d125745aa82cf1f9d22a67b"
OUT=pathlib.Path("ig1-successor2-review"); OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-IG1-SUCCESSOR2-EARLY-REVIEW-PACKET.txt"

FILES=[
("governance-r8/R8-V15-R1-INTEGRATION-GATE1-SUCCESSOR2-PROPOSAL.json","SUCCESSOR2 PROPOSAL"),
("governance-r8/R8-V15-R1-INTEGRATION-GATE1-SUCCESSOR1-INDEPENDENT-REVIEW-002.txt","SUCCESSOR1 REVIEW 002"),
("governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-FALLBACK-003.json","ACTIVE FALLBACK-TO-3"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json","EXACT 120-ENTRY REVIEWED ALLOWLIST"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-FULL-CHANGE-INVENTORY.json","FULL 904-PATH INVENTORY"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json","COLLISION/PREFLIGHT SUMMARY"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR2-INHERITED-BASELINE-TEST-IDENTITY.json","EXACT S1-S7 BASELINE TEST IDENTITIES"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR2-PROPOSAL-PREFLIGHT-FAILURE-001.json","PRESERVED SUCCESSOR2 PREFLIGHT FAILURE"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR2-PROPOSAL-PREFLIGHT-GREEN-001.json","SUCCESSOR2 PREFLIGHT GREEN"),
("tools/r8_v15_r1_ig1_successor2_materialize.py","EXACT SUCCESSOR2 MATERIALIZER"),
("governance-runtime/test_r8_v15_r1_ig1_successor2_integration_oracle.py","EXACT SUCCESSOR2 STRUCTURED ORACLE"),
(".github/workflows/r8-v15-r1-ig1-successor2-materialize.yml","EXACT SUCCESSOR2 MATERIALIZATION WORKFLOW"),
]

def sh(*args): return subprocess.check_output(args)
def show(path): return sh("git","show",f"{PROPOSAL_COMMIT}:{path}")
def blob(path): return sh("git","rev-parse",f"{PROPOSAL_COMMIT}:{path}").decode().strip()

header=f"""R8 v15-r1 — IG-1 MECHANICAL INTEGRATION SUCCESSOR2 — FRESH MANDATORY EARLY REVIEW

USE ONLY THIS FILE.
Do not use prior conversation history or model recollection.
This is a successor PROPOSAL REVIEW ONLY. No integration has been activated or executed.

EXACT SUCCESSOR2 PROPOSAL
proposal_id: R8V15R1-IG1-MECHANICAL-INTEGRATION-SUCCESSOR2
exact proposal commit: {PROPOSAL_COMMIT}
proposal blob SHA-1: 6bd95d56ab8319eeea0d28ab79629c2e409e2837

PREDECESSOR SUCCESSOR1 REVIEW
Successor1 proposal commit: b0b7ddd9fb8c4dfe9775990ac27968c85ade75c1
Review 002: CHANGES_REQUIRED
Critical: 0
High: 2
High 1: candidate could inherit unlisted proposal-HEAD changes because target was not constructed from exact Slice7 base.
High 2: inherited S1-S7 baseline test identities were not bound.

CURRENT CADENCE
Fallback-to-3 remains ACTIVE.
A clean Successor2 review would count only as clean post-remediation review 1 of 2.
Six-slice cadence must not auto-restore.

SUCCESSOR2 REMEDIATION SUMMARY
1. Stage1 target is a separate Git worktree created at exact Slice7 base:
   751162ee42c603cb6c84ee12021d16bab6fa626b
2. Proposal branch HEAD is never the integrated candidate base.
3. Before materialization target HEAD must equal the exact base and be clean.
4. Only 120 exact reviewed path+mode+type+blob entries may be checked out.
5. Final staged diff from exact base must equal exactly those 120 paths plus one non-authoritative candidate manifest.
6. Any unstaged tracked or untracked file hard-fails.
7. Workflow uses no broad git-add. Commit/push occurs only after exact-diff checks and strict oracle pass.
8. Eleven inherited S1-S7 test files have exact path+mode+type+blob identities bound to Slice7.
9. Those baseline identities are checked before materialization and again immediately before tests.
10. Reviewed S8-S46 tests use structured unittest TestResult JSON:
    636 exact tests, zero failures/errors/skips/expectedFailures/unexpectedSuccesses.
11. Inherited S1-S7 baseline uses the same structured result:
    140 exact tests, zero failures/errors/skips/expectedFailures/unexpectedSuccesses.
12. Governance-history file-read detection now distinguishes permitted frozen-schema reads under
    schemas/governance-r8/v15-r1 from prohibited governance-history root reads, including receiver-based reads and simple variable propagation.
13. Activation must bind exact proposal commit/blob, machinery blobs and evidence blobs.
14. Stage1 output remains NON_AUTHORITATIVE_PENDING_FRESH_INDEPENDENT_REVIEW.
15. Stage2 semantic integration remains NOT AUTHORIZED.

PROPOSAL PREFLIGHT HISTORY
- Successor2 preflight run 36163117291 / job 108164281614 failed closed because schema reads were initially over-classified as governance-history reads. No materialization occurred.
- Retry 2 run 36163247367 / job 108164711384 PASSED.
- Retry 2 used a separate exact-base worktree and confirmed target remained pristine after preflight.
- Activation artifact remains absent.

REVIEW FOCUS
Adversarially determine whether Review002 High 1 and High 2 are now fully closed, and whether any new false-green path remains.

Pay particular attention to:
- whether the target candidate can contain any path beyond exact Slice7 base + the 120 allowlisted entries + one manifest;
- whether staged-index semantics, worktree cleanliness and commit behavior enforce that claim;
- whether exact baseline test identities can still be bypassed or changed before execution;
- whether structured unittest result accounting closes skip/xfail/not-collected ambiguity;
- whether proposal/evidence/machinery activation binding is complete;
- whether the governance-history read detector is narrowly correct without permitting runtime governance-history dependencies;
- whether proposal machinery can introduce semantic/currentness/qualification/evidence-promotion behavior;
- whether exact integrated bytes still require fresh independent review before Stage2.

AUTHORITY BOUNDARY
A favorable review may establish only eligibility for EXPLICIT USER ACTIVATION of this exact proposal.
It does not activate integration.
Stage1 output, if later activated, has authority effect NONE and remains pending fresh independent review.
Stage2 semantic work remains NOT AUTHORIZED.
Runtime qualification, evidence promotion, release, deployment, production, policy, constitutional, root and terminal authority remain false.

REQUIRED OUTPUT — RETURN ONLY A-H

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_SUCCESSOR_IDENTITY
Include proposal ID; exact proposal commit/blob; allowlist blob; inventory blob; baseline-identity blob; materializer blob; oracle blob; workflow blob; preflight green run/job; 120 selected-entry count; 904 inventory count; collision count; fallback-to-3 state.

C. CRITICAL_FINDINGS

D. HIGH_FINDINGS

E. MEDIUM_LOW_FINDINGS

F. REMEDIATION_AND_PROTOCOL_ASSESSMENT
F1 Review002 High1 exact-base candidate composition
F2 Review002 High2 inherited baseline test identity
F3 exact final diff = 120 allowlisted paths + one manifest
F4 no broad staging/unlisted file inclusion
F5 structured unittest result/no-bypass oracle
F6 proposal/evidence/machinery activation binding
F7 governance-history runtime-read boundary
F8 rejected-predecessor/unreviewed-descendant exclusion
F9 collision/reserved-path handling before materialization
F10 partial materialization/publish boundary
F11 Stage1 non-authority and Stage2 separation
F12 fallback-to-3/recovery accounting
Identify any remaining concrete false-green or silent-authority path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State whether Stage1 remains non-authoritative; Stage2 remains separately gated; exact integrated bytes require fresh review; fallback-to-3 remains active; and a clean Successor2 review counts as 1 of 2 toward cadence recovery.

H. FINAL_GATE
State exactly:
- IG-1 Successor2 proposal may be explicitly activated by user: YES or NO.
- If YES, activation is NOT automatic and must bind exact proposal commit {PROPOSAL_COMMIT}.
- Stage1 integrated output authority: NONE / non-authoritative pending fresh review.
- Stage2 semantic integration authorized: NO.
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
