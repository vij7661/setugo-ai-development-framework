#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
CANDIDATE="a972ddcee333aff063858727739986fe2fd8088d"
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE1="fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
SLICE2="6a8d0b0e4baa3a9df75dc47f626953b4dde51255"
SLICE3="9b8b519c1f32b675d102b1267511a6a141f39c4a"
SLICE4="3b60d8f14851b755f09a35431c620d6ae594a894"
SLICE5="403e40502e9d51740e89ef352b5611711439661e"
EVIDENCE_HEAD="a95a83a08b904d410e9316900043c05aca530b03"
RUN_ID=36116853988
JOB_ID=108012874732
OUT=pathlib.Path("review-packet-slice6")
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
    for ref in [CANDIDATE,FROZEN_SCHEMA,SLICE1,SLICE2,SLICE3,SLICE4,SLICE5,EVIDENCE_HEAD]:
        got=sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()
        assert got==ref,(ref,got)

    run=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}")
    assert run["status"]=="completed" and run["conclusion"]=="success"
    assert run["head_sha"]==CANDIDATE
    jobs=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==JOB_ID]
    assert len(job)==1 and job[0]["conclusion"]=="success"
    raw_log=sh(["gh","run","view",str(RUN_ID),"--repo",REPO,"--log"])

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICE 6 — FRESH BLIND INDEPENDENT REVIEW

Use only these five supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Exact Slice 6 implementation candidate:
{CANDIDATE}

Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Closed dependency candidates:
Slice 5: {SLICE5}
Slice 4: {SLICE4}
Slice 3: {SLICE3}
Slice 2: {SLICE2}
Slice 1: {SLICE1}

Slice 6 evidence-only freeze head:
{EVIDENCE_HEAD}

Authoritative exact-candidate run/job:
{RUN_ID} / {JOB_ID}

FILES
1. 01_INSTRUCTIONS.txt — this review contract.
2. 02_EXACT_SLICE6_CANDIDATE.txt — exact preregistration, workflow, validator, frozen harness,
   marker, authorization boundary and preserved RED evidence.
3. 03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt — exact frozen runtime contract,
   NORM-033 and R8V12-I029/I030 + V12-025..027 source semantics, exact closed Slice 5/4/1
   runtime dependencies and inherited acceptance/regression sources used by the final workflow.
4. 04_CONSTRUCTION_EVIDENCE.txt — exact final run/job metadata and raw log, dependency
   immutability diff, construction-green/freeze records and preserved RED.
5. 05_SHA256_MANIFEST.txt — exact SHA-256 for files 1-4.

REVIEW SCOPE
Review only bounded local VerifiedStateSeal structure and cross-object binding:
- exact required-field parity;
- opaque non-empty GCP-valid Digest fields;
- non-boolean signed-int64 semantic_state_sequence closure;
- exact SemanticHeads structure;
- closed Slice 4 DecisionPresealContext/AuthorityReadSet local revalidation;
- closed Slice 5 QualifiedTimeProof local revalidation;
- exact decision_preseal_digest, time_proof_digest and authority_read_set_digest binding;
- exact semantic sequence equality across seal/preseal/time proof effective_sequence;
- exact semantic_heads equality across seal/preseal;
- standalone seal revocation_head equality with bound SemanticHeads revocation_head;
- seal_digest remains opaque/unverified;
- explicit non-authority/current-state/commit metadata;
- statelessness, direct workflow trigger coverage and dependency immutability.

IMPORTANT NONCLAIMS
Slice 6 does NOT prove or authorize:
- seal_digest cryptographic correctness;
- qualified time authority, nonce consumption, source status/independence/freshness/signatures;
- current LAS semantic heads/currentness;
- current revocation/runtime/workload state;
- consequential current-head recheck or STATE_CHANGED protection;
- COMMIT_WITH_SEAL authority;
- effect intent commit;
- runtime qualification, release, deployment, production, policy or terminal authority.

A locally valid seal binding remains authority effect NONE.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact code/tests/logs rather than PASS labels;
- test top-level and nested shape confusion, bool/int confusion, opaque digest overvalidation,
  semantic-head mapping equality, standalone revocation-head disagreement, malformed supplied
  preseal/read-set/time-proof inputs, sequence divergence between preseal/time/seal,
  exception-to-success paths, state poisoning and hidden authority grants;
- specifically check whether every equality enforced by Slice 6 is supported by the frozen
  source basis and whether the implementation accidentally claims seal verification/currentness;
- do not demand live COMMIT_WITH_SEAL evidence as if this local validator claims it.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact Slice 6 candidate, frozen schema, closed dependency candidates, run/job,
and packet hashes used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I6_01_TO_I6_16_ASSESSMENT
Assess every frozen I6 case and identify false-green or untested local paths.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what positive bounded Slice 6 construction proves and does not prove.
State whether bounded Slice 6 construction may be adjudicated.
Do not grant verified seal authority, current-state authority, runtime qualification or downstream authority.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 6 independent-review gate.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    candidate_paths=[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice6.yml",
      "governance-runtime/r8_v15_r1_seal_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice6.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"02_EXACT_SLICE6_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 6 exact candidate bytes\n")
        fp.write(sh(["git","show","--no-patch","--format=fuller",CANDIDATE]))
        fp.write(b"\n===== DIFF FROM CLOSED SLICE 5 CANDIDATE =====\n")
        fp.write(sh(["git","diff","--name-status",SLICE5,CANDIDATE]))
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE,path,"SLICE 6 CANDIDATE FILE"))

    dependency_paths=[
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN_SCHEMA,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V12.md"),
      (SLICE1,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (SLICE4,"governance-runtime/r8_v15_r1_preseal_validator.py"),
      (SLICE5,"governance-runtime/r8_v15_r1_timeproof_validator.py"),
      (SLICE5,"governance-runtime/test_r8_v15_r1_implementation_slice5.py"),
      (SLICE4,"governance-runtime/test_r8_v15_r1_implementation_slice4.py"),
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
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE6-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"04_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 6 exact construction evidence\n")
        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run,indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0],indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(raw_log)
        if not raw_log.endswith(b"\n"): fp.write(b"\n")
        fp.write(b"\n===== CLOSED DEPENDENCY IMMUTABILITY DIFF =====\n")
        immut=sh([
          "git","diff","--name-status",SLICE5,CANDIDATE,"--",
          "schemas/governance-r8/v15-r1",
          "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py",
          "governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py",
          "governance-runtime/r8_v15_r1_timeproof_validator.py",
        ])
        fp.write(immut if immut else b"(none)\n")
        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD,path,"SLICE 6 EVIDENCE"))

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt",
      "02_EXACT_SLICE6_CANDIDATE.txt",
      "03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt",
      "04_CONSTRUCTION_EVIDENCE.txt",
    ]]
    manifest=[
      "R8 v15-r1 Slice 6 fresh blind review packet SHA-256 manifest",
      f"candidate={CANDIDATE}",
      f"frozen_schema={FROZEN_SCHEMA}",
      f"slice5_candidate={SLICE5}",
      f"slice4_candidate={SLICE4}",
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
