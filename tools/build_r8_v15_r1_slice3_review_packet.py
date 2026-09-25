#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
CANDIDATE = "9b8b519c1f32b675d102b1267511a6a141f39c4a"
FROZEN_SCHEMA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE1 = "fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
SLICE2 = "6a8d0b0e4baa3a9df75dc47f626953b4dde51255"
EVIDENCE_HEAD = "bf81c062b4afafa33eca7148091893910e49129a"
RUN_ID = 36111540428
JOB_ID = 107995892189
OUT = pathlib.Path("review-packet-slice3")
OUT.mkdir(exist_ok=True)

def sh(args):
    return subprocess.check_output(args)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git_show(ref, path):
    return sh(["git","show",f"{ref}:{path}"])

def git_blob(ref,path):
    return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()

def exact_section(ref,path,title):
    data=git_show(ref,path)
    return (
      f"\n===== BEGIN {title}: {ref}:{path} =====\n"
      f"git_blob_sha1={git_blob(ref,path)}\n"
      f"sha256={sha(data)}\n"
      f"byte_count={len(data)}\n"
    ).encode()+data+(b"" if data.endswith(b"\n") else b"\n")+f"===== END {title}: {ref}:{path} =====\n".encode()

def gh_json(endpoint):
    return json.loads(sh(["gh","api",endpoint]))

def main():
    for ref in [CANDIDATE,FROZEN_SCHEMA,SLICE1,SLICE2,EVIDENCE_HEAD]:
        got=sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()
        assert got==ref,(ref,got)

    run=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}")
    assert run["status"]=="completed" and run["conclusion"]=="success"
    assert run["head_sha"]==CANDIDATE
    jobs=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==JOB_ID]
    assert len(job)==1 and job[0]["conclusion"]=="success"
    raw_log=sh(["gh","run","view",str(RUN_ID),"--repo",REPO,"--log"])

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICE 3 — FRESH BLIND INDEPENDENT REVIEW

Use only these five supplied files. Do not use prior conversation history, prior reviewer
outcomes, adjudications, or model recollection.

Exact Slice 3 implementation candidate:
{CANDIDATE}

Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Closed Slice 2 dependency candidate:
{SLICE2}

Closed Slice 1 dependency candidate:
{SLICE1}

Slice 3 evidence-only freeze head:
{EVIDENCE_HEAD}

Authoritative exact-candidate run/job:
{RUN_ID} / {JOB_ID}

FILES
1. 01_INSTRUCTIONS.txt — this review contract.
2. 02_EXACT_SLICE3_CANDIDATE.txt — exact preregistration, workflow, validator, frozen harness,
   marker, authorization boundary and preserved RED evidence.
3. 03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt — exact frozen runtime contract, GCP vectors,
   governing v11 STC/root source, normalized v15 detail appendix, and exact closed Slice 1/2
   dependency modules/tests needed to inspect local behavior.
4. 04_CONSTRUCTION_EVIDENCE.txt — exact final run/job metadata and raw log, exact dependency
   immutability diff, construction-green and freeze records.
5. 05_SHA256_MANIFEST.txt — exact SHA-256 for files 1-4.

REVIEW SCOPE
Review only bounded local StateTransferCertificate structure/cross-field validation:
- exact frozen STC and SemanticHeads required-field parity;
- LAS/GGS conditional null/non-null rules;
- GGS nested GGSGenesisStateRoot validation and mapped-field equality;
- Sequence/nullability/type handling, including bool/int confusion;
- generic CanonicalId/Digest opacity/non-empty behavior plus inherited GCP string rules;
- SHA-256 lexical enforcement only for LAS/GGS state_root_digest;
- no invented stc_digest formula;
- direct Slice 2 GGS verify regression before dependency use;
- statelessness and non-authority result metadata;
- workflow direct-path coverage and frozen dependency immutability.

IMPORTANT NONCLAIMS
This Slice 3 does NOT verify or authorize:
- ROTATION_PREPARE certificate validity or matching a lawful committed barrier;
- barrier reservation/currentness/abort semantics;
- old/new quorum signatures or voting state;
- STC_COMMIT uniqueness, STC equivocation, ENTER_JOINT, or ACTIVATE;
- whether GGS semantic_state_binding_required was lawfully derived from the governed operation;
- whether LAS semantic heads are the lawful coherent barrier-B snapshot;
- runtime qualification, release, deployment, production, policy, or terminal authority.

A locally valid STC may still have authority effect NONE.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact code/tests/logs, not status labels;
- try wrong-system conditional combinations, null confusion, bool/int confusion, nested-root aliasing,
  stale/mismatched mapped fields, malformed SHA root digests, empty/non-NFC/noncharacter strings,
  extra/missing fields, mutation/state poisoning, exception-to-success paths, and any hidden authority grant;
- do not demand runtime/quorum/certificate evidence as if this bounded local validator claims it;
  report such gaps only if the implementation improperly claims those properties.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact Slice 3 candidate, frozen schema, Slice 2 and Slice 1 dependency candidates,
run/job, and packet hashes used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I3_01_TO_I3_16_ASSESSMENT
Assess every frozen I3 case and identify false-green or untested local paths.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what a positive bounded Slice 3 construction proves and does not prove.
State whether bounded Slice 3 construction may be adjudicated.
Do not grant runtime qualification or downstream authority.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 3 independent-review gate.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    candidate_paths=[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice3.yml",
      "governance-runtime/r8_v15_r1_stc_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice3.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"02_EXACT_SLICE3_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 3 exact candidate bytes\n")
        fp.write(sh(["git","show","--no-patch","--format=fuller",CANDIDATE]))
        fp.write(b"\n===== DIFF FROM CLOSED SLICE 2 CANDIDATE =====\n")
        fp.write(sh(["git","diff","--name-status",SLICE2,CANDIDATE]))
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE,path,"SLICE 3 CANDIDATE FILE"))

    dep_paths=[
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/gcp-rvm-2.json"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V11.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-V15-NORMALIZED-DETAIL-APPENDIX.md"),
      (SLICE1,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (SLICE2,"governance-runtime/r8_v15_r1_state_roots.py"),
      (SLICE2,"governance-runtime/test_r8_v15_r1_implementation_slice2.py"),
    ]
    with (OUT/"03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt").open("wb") as fp:
        fp.write(b"Exact frozen contracts, governing source, and closed dependencies.\n")
        for ref,path in dep_paths:
            fp.write(exact_section(ref,path,"FROZEN CONTRACT / GOVERNING SOURCE / DEPENDENCY"))

    evidence_paths=[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE3-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"04_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 3 exact construction evidence\n")
        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run,indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0],indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(raw_log)
        if not raw_log.endswith(b"\n"): fp.write(b"\n")
        fp.write(b"\n===== DEPENDENCY IMMUTABILITY DIFF =====\n")
        immut=sh([
          "git","diff","--name-status",SLICE2,CANDIDATE,"--",
          "schemas/governance-r8/v15-r1",
          "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py",
        ])
        fp.write(immut if immut else b"(none)\n")
        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD,path,"SLICE 3 EVIDENCE"))

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt",
      "02_EXACT_SLICE3_CANDIDATE.txt",
      "03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt",
      "04_CONSTRUCTION_EVIDENCE.txt",
    ]]
    manifest=[
      "R8 v15-r1 Slice 3 fresh blind review packet SHA-256 manifest",
      f"candidate={CANDIDATE}",
      f"frozen_schema={FROZEN_SCHEMA}",
      f"slice2_candidate={SLICE2}",
      f"slice1_candidate={SLICE1}",
      f"run={RUN_ID}",
      f"job={JOB_ID}",
      "",
    ]
    for p in files:
        manifest.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"05_SHA256_MANIFEST.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8")

    print(f"candidate={CANDIDATE}")
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__":
    main()
