#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, pathlib, subprocess

CANDIDATE="4984f06a4420b76ad1ad475751aebda04a2d2c5c"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
TREE="5a34e0d7db3e750dd5b0f722ccecc8014be189ef"
MANIFEST_PATH="governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INTEGRATED-CANDIDATE-MANIFEST.json"
MANIFEST_BLOB="a78add847f6d4ba8914a66ee00d89422fbaa47f2"
OUT=pathlib.Path("ig1-successor3-stage1-review")
OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-IG1-SUCCESSOR3-STAGE1-CANDIDATE-REVIEW-PACKET.txt"

STATIC_FILES=[
 ("governance-r8/R8-V15-R1-INTEGRATION-GATE1-SUCCESSOR3-INDEPENDENT-REVIEW-004.txt","PRE-ACTIVATION REVIEW 004"),
 ("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-ACTIVATION.json","EXPLICIT STAGE1 ACTIVATION"),
 ("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-STAGE1-EXECUTION-EVIDENCE.json","STAGE1 EXECUTION EVIDENCE"),
 ("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-STAGE1-LOG-EXTRACT.txt","SELECTED RAW EXECUTION LOG EXTRACT"),
 ("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json","EXACT 120-ENTRY REVIEWED ALLOWLIST"),
 ("governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INHERITED-BASELINE-TEST-IDENTITY.json","EXACT INHERITED BASELINE IDENTITIES/GROUPS"),
]
def sh(*args):
    return subprocess.check_output(args)
def text_at(rev,path):
    return sh("git","show",f"{rev}:{path}")
def blob_at(rev,path):
    return sh("git","rev-parse",f"{rev}:{path}").decode().strip()
def tree_entry(rev,path):
    out=sh("git","ls-tree",rev,"--",path).decode().rstrip("\n")
    if not out:return None
    meta,name=out.split("\t",1); mode,typ,blob=meta.split()
    return {"path":name,"mode":mode,"type":typ,"blob":blob}

allow=json.loads(pathlib.Path("governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json").read_text())
expected={}
slice_for={}
for n,rec in allow["per_candidate"].items():
    for e in rec["selected_entries"]:
        expected[e["path"]]={k:e[k] for k in ("path","mode","type","blob")}
        slice_for[e["path"]]=int(n)
actual_paths=sh("git","diff","--name-only",BASE,CANDIDATE).decode().splitlines()
if len(actual_paths)!=121:
    raise SystemExit(f"changed path count {len(actual_paths)} != 121")
matrix=[]
for path in sorted(actual_paths):
    actual=tree_entry(CANDIDATE,path)
    if path==MANIFEST_PATH:
        matrix.append({"path":path,"source":"candidate_manifest","actual":actual,"expected_manifest_blob":MANIFEST_BLOB,"match":actual and actual["blob"]==MANIFEST_BLOB})
    else:
        exp=expected.get(path)
        matrix.append({"path":path,"source_slice":slice_for.get(path),"actual":actual,"expected":exp,"match":actual==exp})
if not all(x["match"] for x in matrix):
    raise SystemExit("candidate tree matrix mismatch")
if set(actual_paths)!=(set(expected)|{MANIFEST_PATH}):
    raise SystemExit("candidate changed path set differs from allowlist+manifest")

# Static direct-import scan across reviewed implementation modules in exact candidate.
selected_impl=sorted(p for p in expected if p.startswith("governance-runtime/r8_v15_r1_") and p.endswith(".py") and "/test_" not in p)
edges=[]
for path in selected_impl:
    src=text_at(CANDIDATE,path).decode()
    tree=ast.parse(src,filename=path)
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for a in node.names:
                if a.name.startswith("r8_v15_r1_"):
                    edges.append({"from":path,"kind":"import","to":a.name})
        elif isinstance(node,ast.ImportFrom):
            mod=node.module or ""
            if mod.startswith("r8_v15_r1_"):
                edges.append({"from":path,"kind":"from","to":mod})
edges=sorted(edges,key=lambda x:(x["from"],x["to"],x["kind"]))

manifest=text_at(CANDIDATE,MANIFEST_PATH)
header=f"""R8 v15-r1 — IG-1 SUCCESSOR3 STAGE1 EXACT INTEGRATED CANDIDATE — FRESH INDEPENDENT REVIEW

USE ONLY THIS FILE.
Do not use prior conversation history or model recollection.
This is a FRESH POST-STAGE1 REVIEW of the exact integrated candidate.
It is NOT a Stage2 semantic review.

A. EXACT CANDIDATE IDENTITY
candidate commit: {CANDIDATE}
candidate branch: integration/r8-v15-r1-ig1-successor3-candidate-448739d25dc7
candidate parent: {BASE}
candidate tree: {TREE}
commits above base: 1
changed paths relative to base: 121
reviewed allowlisted entries: 120
candidate manifest path: {MANIFEST_PATH}
candidate manifest blob: {MANIFEST_BLOB}

Pre-activation proposal/review:
proposal ID: R8V15R1-IG1-MECHANICAL-INTEGRATION-SUCCESSOR3
proposal contract commit: c4d00fcd2f52ba77f4ee90a1aa9b6c62c0a7c317
proposal blob: 4f3cab0b33caa19fcb81da3cff53456714de3da3
activation gate blob: 8a3c9ca39f83e3262a85ae0e5ffb456d61c6d3ac
Independent Review 004 blob: 46e2a5ef1a95eb2f098e706da6c09c3652072344

Execution:
activation commit: 448739d25dc775237f9000ccd189d0764a452ae6
activation run: 36167485075
activation gate job: 108178671152
Stage1 job: 108178711127
Stage1 conclusion: SUCCESS
post-run verification run/job: 36167715425 / 108179410259
post-run conclusion: SUCCESS

Strict oracle:
reviewed S8-S46 tests: 636
inherited S1-S7 baseline tests: 140
total: 776
failures/errors/skips/expected failures/unexpected successes: 0

Candidate post-run verification independently re-established:
- exact parent {BASE};
- exact tree {TREE};
- exact changed path set = 120 reviewed entries + one manifest;
- all 120 candidate path/mode/type/blob identities equal reviewed allowlist;
- candidate manifest blob = {MANIFEST_BLOB};
- all 11 inherited baseline identities unchanged;
- strict 636+140 oracle PASS;
- candidate worktree remained unchanged after oracle.

AUTHORITY BOUNDARY
Candidate status is:
INTEGRATED_IMPLEMENTATION_CANDIDATE_NON_AUTHORITATIVE_PENDING_FRESH_INDEPENDENT_REVIEW

Stage1 grants no semantic/currentness/qualification/evidence-promotion/runtime/release/deployment/production/policy/constitutional/root/terminal authority.
Stage2 semantic integration is NOT AUTHORIZED by this packet.

CADENCE
Fallback-to-3 remains ACTIVE.
Pre-activation Review 004 was clean review 1 of 2 after latest remediation.
If THIS fresh candidate review is BOUNDED_PASS with zero Critical/High findings, it may count as clean review 2 of 2, satisfying only the evidence precondition for possible explicit cadence restoration. Restoration remains non-automatic.

REVIEW OBJECTIVE
Determine whether the exact Stage1 candidate may close as a bounded non-authoritative mechanical integration candidate.

Review specifically:
1. exact parent/tree/one-commit identity;
2. exact changed set = 120 reviewed entries + one manifest;
3. exact path/mode/type/blob equality to the reviewed allowlist;
4. unchanged inherited baseline test identities;
5. candidate manifest content and authority boundary;
6. Stage1 activation/execution/post-run evidence;
7. 636+140 zero-bypass oracle evidence;
8. whether colocating the reviewed modules introduces any observable direct r8_v15_r1_* implementation import/dependency edge; see generated scan below;
9. whether any unreviewed content or authority-bearing behavior entered the candidate;
10. whether exact integrated bytes still require a separate semantic gate before Stage2.

Do NOT treat candidate closure as Stage2 authorization.

REQUIRED OUTPUT — RETURN ONLY A-H

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_STAGE1_CANDIDATE_IDENTITY
Include candidate commit, parent, tree, branch, changed-path count, allowlisted-entry count, manifest blob, activation run/jobs, post-run run/job, and test totals.

C. CRITICAL_FINDINGS

D. HIGH_FINDINGS

E. MEDIUM_LOW_FINDINGS

F. STAGE1_CANDIDATE_ASSESSMENT
F1 exact parent/tree/one-commit construction
F2 exact 120+manifest path set
F3 path/mode/type/blob allowlist identity
F4 inherited baseline identity
F5 candidate manifest/non-authority
F6 activation + execution evidence
F7 post-run re-verification + 776-test oracle
F8 direct implementation import/dependency scan
F9 unreviewed-content/silent-authority assessment
F10 Stage2 separation

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State:
- whether exact Stage1 candidate may close only as non-authoritative mechanical integration;
- whether Stage2 remains separately gated and unauthorized;
- whether fallback-to-3 remains active;
- whether a clean result counts as clean review 2 of 2 and only satisfies the evidence precondition for possible explicit cadence restoration.

H. FINAL_GATE
State exactly:
- Exact Stage1 candidate {CANDIDATE} may close as BOUNDED_PASS: YES or NO.
- Clean review 2 of 2 achieved: YES or NO.
- Automatic six-slice cadence restoration: NO.
- Stage2 semantic integration authorized: NO.
- Stage2 semantic-gate preregistration/review may proceed after bounded closure: YES or NO.
- Runtime/release/deployment/production/policy/constitutional/root/terminal authority granted: NO.

"""

with TARGET.open("wb") as fp:
    fp.write(header.encode())
    fp.write(b"\n===== GENERATED EXACT CANDIDATE TREE MATRIX =====\n")
    fp.write((json.dumps(matrix,indent=2)+"\n").encode())
    fp.write(b"===== END GENERATED EXACT CANDIDATE TREE MATRIX =====\n")
    fp.write(b"\n===== GENERATED DIRECT R8 IMPLEMENTATION IMPORT SCAN =====\n")
    fp.write((json.dumps({"selected_implementation_files":len(selected_impl),"direct_r8_import_edges":edges},indent=2)+"\n").encode())
    fp.write(b"===== END GENERATED DIRECT R8 IMPLEMENTATION IMPORT SCAN =====\n")
    fp.write(b"\n===== EXACT CANDIDATE MANIFEST =====\n")
    fp.write(manifest)
    if not manifest.endswith(b"\n"): fp.write(b"\n")
    fp.write(b"===== END EXACT CANDIDATE MANIFEST =====\n")
    for path,label in STATIC_FILES:
        b=pathlib.Path(path).read_bytes()
        blob=blob_at("HEAD",path)
        fp.write(f"\n===== BEGIN {label} =====\npath={path}\ngit_blob_sha1={blob}\nbyte_count={len(b)}\nsha256={hashlib.sha256(b).hexdigest()}\n".encode())
        fp.write(b)
        if not b.endswith(b"\n"): fp.write(b"\n")
        fp.write(f"===== END {label} =====\n".encode())

b=TARGET.read_bytes()
print(TARGET.name,len(b),hashlib.sha256(b).hexdigest())
