#!/usr/bin/env python3
import hashlib, pathlib, subprocess

BUNDLE_COMMIT="a39270edfd237640166472cc0041baae704a72b7"
PROPOSAL_COMMIT="c4d00fcd2f52ba77f4ee90a1aa9b6c62c0a7c317"
OUT=pathlib.Path("ig1-successor3-review"); OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-IG1-SUCCESSOR3-EARLY-REVIEW-PACKET.txt"

FILES=[
("governance-r8/R8-V15-R1-INTEGRATION-GATE1-SUCCESSOR3-PROPOSAL.json","SUCCESSOR3 PROPOSAL CONTRACT"),
("governance-r8/R8-V15-R1-INTEGRATION-GATE1-SUCCESSOR2-INDEPENDENT-REVIEW-003.txt","SUCCESSOR2 REVIEW 003"),
("governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-FALLBACK-004.json","ACTIVE FALLBACK-TO-3"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-ACTIVATION-GATE-BINDING.json","SUCCESSOR3 ACTIVATION GATE BINDING"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json","EXACT 120-ENTRY REVIEWED ALLOWLIST"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-FULL-CHANGE-INVENTORY.json","FULL 904-PATH INVENTORY"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json","COLLISION SUMMARY"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INHERITED-BASELINE-TEST-IDENTITY.json","EXACT BASELINE IDENTITIES AND GROUP COUNTS"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-PROPOSAL-PREFLIGHT-FAILURE-001.json","PRESERVED SUCCESSOR3 PREFLIGHT FAILURE"),
("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-PROPOSAL-PREFLIGHT-GREEN-001.json","SUCCESSOR3 PREFLIGHT GREEN"),
("tools/r8_v15_r1_ig1_successor3_materialize.py","EXACT SUCCESSOR3 MATERIALIZER"),
("governance-runtime/test_r8_v15_r1_ig1_successor3_integration_oracle.py","EXACT SUCCESSOR3 STRUCTURED ORACLE"),
("tools/r8_v15_r1_ig1_successor3_unittest_child.py","EXACT STRUCTURED UNITTEST CHILD"),
(".github/workflows/r8-v15-r1-ig1-successor3-core.yml","EXACT REUSABLE CORE WORKFLOW"),
(".github/workflows/r8-v15-r1-ig1-successor3-activation-gate.yml","EXACT POST-FREEZE ACTIVATION GATE"),
]

def sh(*args): return subprocess.check_output(args)
def show(path): return sh("git","show",f"{BUNDLE_COMMIT}:{path}")
def blob(path): return sh("git","rev-parse",f"{BUNDLE_COMMIT}:{path}").decode().strip()

header=f"""R8 v15-r1 — IG-1 MECHANICAL INTEGRATION SUCCESSOR3 — FRESH MANDATORY EARLY REVIEW

USE ONLY THIS FILE.
Do not use prior conversation history or model recollection.
This is a PROPOSAL REVIEW ONLY. No activation artifact exists and no integration has executed.

EXACT PROPOSAL CONTRACT
proposal_id: R8V15R1-IG1-MECHANICAL-INTEGRATION-SUCCESSOR3
proposal contract commit: {PROPOSAL_COMMIT}
proposal contract blob SHA-1: 4f3cab0b33caa19fcb81da3cff53456714de3da3
exact review-bundle commit: {BUNDLE_COMMIT}
activation-gate blob SHA-1: 8a3c9ca39f83e3262a85ae0e5ffb456d61c6d3ac

PREDECESSOR REVIEW 003
Successor2 disposition: CHANGES_REQUIRED
Critical: 0
High: 2
High 1: activation binding not exact/complete.
High 2: governance-history detector traversal/non-open API bypass.
Medium/Low: immediate pre-commit recheck; baseline groups derived from manifest; review artifact binding; stronger AST/dynamic execution prohibition.

SUCCESSOR3 IMPLEMENTED REMEDIATIONS
1. Proposal contract is frozen before activation-gate creation.
2. Activation gate hard-codes exact proposal ID, proposal contract commit/blob/path, exact review path, complete required machinery map and complete required evidence map.
3. Activation top-level, independent_review and explicit_user_approval key sets are exact; missing or extra keys fail.
4. Review path is fixed. HEAD review blob must equal the activation-recorded blob, but disposition is NOT trusted from JSON alone: actual review text is parsed for exact proposal ID/commit, BOUNDED_PASS, clean Critical/High sections and YES final gate.
5. Because a file cannot embed its own exact hash without circularity, the activation gate is explicitly the small validation root-of-trust. Its exact blob is included here and explicit user approval must name that exact gate blob. The gate contains no materialization/semantic logic and only calls the separately exact-hash-bound reusable core after validation. REVIEWER MUST DECIDE WHETHER THIS BOUNDARY IS ACCEPTABLE.
6. Governance-history detection uses path normalization/traversal-first classification and covers open/read_text/read_bytes/readlink/resolve/iterdir/glob/rglob/walk/listdir/scandir plus path '/' traversal.
7. Detector self-tests require rejection of schema-root traversal, literal traversal, listdir, glob and inherited-schema traversal; legitimate schema reads and traversal-free schema-root construction must pass.
8. Final exact staged diff is re-run in the SAME shell step immediately before git commit.
9. Baseline identity manifest contains all 11 test entries plus seven exact groups and exact group counts: 16/16/16/16/16/16/44 = 140, measured on exact Slice7 at run 36164919504.
10. Oracle derives baseline membership and expected counts from that manifest and rejects duplicate/missing group files.
11. Structured child runner replaces python -c dynamic test code.
12. Materializer/oracle/child are checked against explicit import allowlists and forbidden eval/exec/compile/__import__/globals/locals/vars, forbidden dynamic modules, sys.modules, mock/monkeypatch and direct production-validator imports.
13. Exact-base construction, 120 reviewed entries, exact final diff, rejected-predecessor controls and 636+140 structured zero-bypass test expectations remain in force.
14. Stage1 output remains non-authoritative pending fresh review; Stage2 is NOT authorized.
15. Fallback-to-3 remains ACTIVE; this CHANGES_REQUIRED predecessor review reset clean-review recovery to 0/2.

PREFLIGHT
Successor3 first preflight 36165481422 failed closed on a detector false positive while constructing the traversal-free allowed schema root. No materialization.
After narrow classifier repair, retry 36165634225 PASSED. No materialization; exact target remained pristine.

REVIEW FOCUS
Adversarially inspect the actual files below and decide:
- Is activation binding now exact and complete?
- Is the gate root-of-trust/self-hash boundary acceptable, or does it leave a concrete substitution path?
- Can any missing/extra machinery/evidence binding pass?
- Can a fake/replaced review artifact pass despite blob+text parsing?
- Can path traversal, receiver reads, glob/directory enumeration, or simple variable propagation reach governance history?
- Is the immediate pre-commit final-diff check truly adjacent to commit and fail-closed?
- Do baseline groups exactly partition the 11 identities with exact per-group counts?
- Can structured unittest accounting silently skip/not-collect/expected-fail tests?
- Can any prohibited dynamic execution/import/monkeypatch route remain in integration machinery?
- Does reusable core remain the only integration-causing logic and stay exact-hash-bound by the gate?
- Does exact integrated output still require fresh independent review before Stage2?

REQUIRED OUTPUT — RETURN ONLY A-H

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_SUCCESSOR_IDENTITY
Include proposal ID; proposal contract commit/blob; review-bundle commit; activation-gate blob; materializer/oracle/child/core blobs; allowlist/inventory/baseline blobs; preflight green run; 120 selected entries; 904 inventory paths; fallback-to-3 state.

C. CRITICAL_FINDINGS

D. HIGH_FINDINGS

E. MEDIUM_LOW_FINDINGS

F. REMEDIATION_AND_PROTOCOL_ASSESSMENT
F1 Review003 High1 exact activation binding
F2 activation-gate root/self-hash boundary
F3 Review003 High2 normalized governance-history detector
F4 directory/glob/traversal/receiver coverage
F5 immediate pre-commit exact staged-diff verification
F6 baseline manifest group membership/per-group counts
F7 exact review artifact binding and parsing
F8 declarative machinery import/dynamic-execution restrictions
F9 structured zero-bypass 636+140 oracle
F10 exact-base/120-entry composition and rejected predecessor controls
F11 reusable core hash binding and gate/core separation
F12 Stage1 non-authority, Stage2 separation, fallback/recovery
Identify any remaining concrete false-green or silent-authority path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State whether Stage1 remains non-authoritative, Stage2 remains separately gated, exact integrated bytes require fresh review, fallback-to-3 remains active, and whether a clean Successor3 review counts as 1 of 2 toward cadence recovery.

H. FINAL_GATE
State exactly:
- IG-1 Successor3 proposal may be explicitly activated by user: YES or NO.
- If YES, activation is NOT automatic and explicit user approval must bind proposal contract commit {PROPOSAL_COMMIT}, proposal blob 4f3cab0b33caa19fcb81da3cff53456714de3da3, and activation-gate blob 8a3c9ca39f83e3262a85ae0e5ffb456d61c6d3ac.
- Stage1 integrated output authority: NONE / non-authoritative pending fresh review.
- Stage2 semantic integration authorized: NO.
- Six-slice cadence automatically restored: NO.
- Runtime/release/deployment/production/policy/constitutional/root/terminal authority granted: NO.

"""

with TARGET.open("wb") as fp:
    fp.write(header.encode())
    for path,label in FILES:
        b=show(path)
        fp.write(f"\n===== BEGIN {label} =====\npath={path}\nref={BUNDLE_COMMIT}\ngit_blob_sha1={blob(path)}\nbyte_count={len(b)}\nsha256={hashlib.sha256(b).hexdigest()}\n".encode())
        fp.write(b)
        if not b.endswith(b"\n"): fp.write(b"\n")
        fp.write(f"===== END {label} =====\n".encode())

b=TARGET.read_bytes()
print(TARGET.name,len(b),hashlib.sha256(b).hexdigest())
