#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
CANDIDATE="3b60d8f14851b755f09a35431c620d6ae594a894"
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE1="fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
SLICE2="6a8d0b0e4baa3a9df75dc47f626953b4dde51255"
SLICE3="9b8b519c1f32b675d102b1267511a6a141f39c4a"
EVIDENCE_HEAD="8857d91b6cbd5b8569907a04720123621fbf8db3"
RUN_ID=36113335473
JOB_ID=108001554748
OUT=pathlib.Path("review-packet-slice4")
OUT.mkdir(exist_ok=True)

def sh(args): return subprocess.check_output(args)
def sha(data): return hashlib.sha256(data).hexdigest()
def git_show(ref,path): return sh(["git","show",f"{ref}:{path}"])
def git_blob(ref,path): return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()
def gh_json(endpoint): return json.loads(sh(["gh","api",endpoint]))

def exact_section(ref,path,title):
    data=git_show(ref,path)
    return (
        f"\n===== BEGIN {title}: {ref}:{path} =====\n"
        f"git_blob_sha1={git_blob(ref,path)}\n"
        f"sha256={sha(data)}\n"
        f"byte_count={len(data)}\n"
    ).encode()+data+(b"" if data.endswith(b"\n") else b"\n")+f"===== END {title}: {ref}:{path} =====\n".encode()

def main():
    for ref in [CANDIDATE,FROZEN_SCHEMA,SLICE1,SLICE2,SLICE3,EVIDENCE_HEAD]:
        got=sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()
        assert got==ref,(ref,got)

    run=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}")
    assert run["status"]=="completed" and run["conclusion"]=="success"
    assert run["head_sha"]==CANDIDATE
    jobs=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==JOB_ID]
    assert len(job)==1 and job[0]["conclusion"]=="success"
    raw_log=sh(["gh","run","view",str(RUN_ID),"--repo",REPO,"--log"])

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICE 4 — FRESH BLIND INDEPENDENT REVIEW

Use only these five supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Exact Slice 4 implementation candidate:
{CANDIDATE}

Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Closed dependency candidates:
Slice 3: {SLICE3}
Slice 2: {SLICE2}
Slice 1: {SLICE1}

Slice 4 evidence-only freeze head:
{EVIDENCE_HEAD}

Authoritative exact-candidate run/job:
{RUN_ID} / {JOB_ID}

FILES
1. 01_INSTRUCTIONS.txt — this review contract.
2. 02_EXACT_SLICE4_CANDIDATE.txt — exact preregistration, workflow, validator, frozen harness,
   marker, authorization boundary and preserved RED evidence.
3. 03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt — exact frozen runtime contract,
   normalized authority-read-set/preseal source, closed implementation dependencies and
   inherited acceptance/regression sources used by the final workflow.
4. 04_CONSTRUCTION_EVIDENCE.txt — exact final run/job metadata and raw log, dependency
   immutability diff, construction-green/freeze evidence and preserved RED.
5. 05_SHA256_MANIFEST.txt — exact SHA-256 for files 1-4.

REVIEW SCOPE
Review only bounded local AuthorityReadSet / DecisionPresealContext validation:
- exact frozen field-set parity for AuthorityReadSetEntry, AuthorityReadSet, DPS,
  SemanticHeads and ResolverIdentity;
- non-empty read-set entries and exact per-entry shape;
- generic CanonicalId/Digest opacity plus inherited GCP string validation;
- non-boolean signed-int64 semantic_state_sequence closure;
- effect_class null/non-null sentinel against verifier-owned external_effect_involved context;
- exact equality of DPS authority_read_set_digest to the supplied locally valid read set digest;
- no invented authority_read_set_digest or decision_preseal_digest formula;
- statelessness, non-authority metadata, workflow direct-trigger coverage and dependency immutability.

IMPORTANT NONCLAIMS
Slice 4 does NOT prove or authorize:
- AuthorityReadSet completeness for an actual predicate;
- source/head/value freshness/currentness;
- authority_read_set_digest correctness or recomputation;
- decision_preseal_digest correctness or recomputation;
- active/current RIR membership or resolver qualification;
- lawful derivation of external_effect_involved;
- revocation/runtime/workload state currentness;
- time proof, VerifiedStateSeal, COMMIT_WITH_SEAL or consequential commit recheck;
- runtime qualification, release, deployment, production, policy, or terminal authority.

A locally valid preseal still has authority effect NONE.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact code/tests/logs, not PASS labels;
- try mapping/list confusion, bool/int confusion, empty arrays, extra/missing fields,
  malformed nested SemanticHeads/ResolverIdentity, non-NFC/noncharacter values, opaque digest
  overvalidation, caller-controlled effect-context weakening, read-set digest mismatch,
  mutation/state poisoning, exception-to-success paths and hidden authority grants;
- specifically check that external_effect_involved is verifier context, not derived from candidate DPS;
- do not demand digest recomputation where the frozen source does not define a formula.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact Slice 4 candidate, frozen schema and closed dependency candidates, run/job,
and packet hashes used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I4_01_TO_I4_16_ASSESSMENT
Assess every frozen I4 case and identify false-green or untested local paths.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what positive bounded Slice 4 construction proves and does not prove.
State whether bounded Slice 4 construction may be adjudicated.
Do not grant runtime qualification or downstream authority.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 4 independent-review gate.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    candidate_paths=[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice4.yml",
      "governance-runtime/r8_v15_r1_preseal_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice4.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"02_EXACT_SLICE4_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 4 exact candidate bytes\n")
        fp.write(sh(["git","show","--no-patch","--format=fuller",CANDIDATE]))
        fp.write(b"\n===== DIFF FROM CLOSED SLICE 3 CANDIDATE =====\n")
        fp.write(sh(["git","diff","--name-status",SLICE3,CANDIDATE]))
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE,path,"SLICE 4 CANDIDATE FILE"))

    dependency_paths=[
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/gcp-rvm-2.json"),
      (FROZEN_SCHEMA,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V13.md"),
      (SLICE1,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (SLICE2,"governance-runtime/r8_v15_r1_state_roots.py"),
      (SLICE3,"governance-runtime/r8_v15_r1_stc_validator.py"),
      (SLICE3,"governance-runtime/test_r8_v15_r1_implementation_slice3.py"),
      (SLICE2,"governance-runtime/test_r8_v15_r1_implementation_slice2.py"),
      (SLICE1,"governance-runtime/test_r8_v15_r1_implementation_slice1.py"),
      (SLICE1,"governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py"),
      (SLICE1,"governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py"),
      (SLICE1,"governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py"),
      (SLICE1,"governance-runtime/test_r8_v15_r1_post_freeze_regression.py"),
    ]
    with (OUT/"03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt").open("wb") as fp:
        fp.write(b"Exact frozen contracts, governing source and closed dependencies.\n")
        for ref,path in dependency_paths:
            fp.write(exact_section(ref,path,"FROZEN CONTRACT / GOVERNING SOURCE / DEPENDENCY"))

    evidence_paths=[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE4-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"04_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 4 exact construction evidence\n")
        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run,indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0],indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(raw_log)
        if not raw_log.endswith(b"\n"): fp.write(b"\n")
        fp.write(b"\n===== CLOSED DEPENDENCY IMMUTABILITY DIFF =====\n")
        immut=sh([
          "git","diff","--name-status",SLICE3,CANDIDATE,"--",
          "schemas/governance-r8/v15-r1",
          "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py",
          "governance-runtime/r8_v15_r1_stc_validator.py",
        ])
        fp.write(immut if immut else b"(none)\n")
        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD,path,"SLICE 4 EVIDENCE"))

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt",
      "02_EXACT_SLICE4_CANDIDATE.txt",
      "03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt",
      "04_CONSTRUCTION_EVIDENCE.txt",
    ]]
    manifest=[
      "R8 v15-r1 Slice 4 fresh blind review packet SHA-256 manifest",
      f"candidate={CANDIDATE}",
      f"frozen_schema={FROZEN_SCHEMA}",
      f"slice3_candidate={SLICE3}",
      f"slice2_candidate={SLICE2}",
      f"slice1_candidate={SLICE1}",
      f"run={RUN_ID}",
      f"job={JOB_ID}",
      "",
    ]
    for p in files: manifest.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"05_SHA256_MANIFEST.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8")

    print(f"candidate={CANDIDATE}")
    for p in sorted(OUT.iterdir()):
        if p.is_file(): print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__":
    main()
