#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
CANDIDATE="403e40502e9d51740e89ef352b5611711439661e"
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE1="fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
SLICE2="6a8d0b0e4baa3a9df75dc47f626953b4dde51255"
SLICE3="9b8b519c1f32b675d102b1267511a6a141f39c4a"
SLICE4="3b60d8f14851b755f09a35431c620d6ae594a894"
EVIDENCE_HEAD="59a97cb7dae51c427adf8cb5f5c9868b7a71c050"
RUN_ID=36115137350
JOB_ID=108007336356
OUT=pathlib.Path("review-packet-slice5")
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
    for ref in [CANDIDATE,FROZEN_SCHEMA,SLICE1,SLICE2,SLICE3,SLICE4,EVIDENCE_HEAD]:
        got=sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()
        assert got==ref,(ref,got)

    run=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}")
    assert run["status"]=="completed" and run["conclusion"]=="success"
    assert run["head_sha"]==CANDIDATE
    jobs=gh_json(f"repos/{REPO}/actions/runs/{RUN_ID}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==JOB_ID]
    assert len(job)==1 and job[0]["conclusion"]=="success"
    raw_log=sh(["gh","run","view",str(RUN_ID),"--repo",REPO,"--log"])

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICE 5 — FRESH BLIND INDEPENDENT REVIEW

Use only these five supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Exact Slice 5 implementation candidate:
{CANDIDATE}

Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Closed dependency candidates:
Slice 4: {SLICE4}
Slice 3: {SLICE3}
Slice 2: {SLICE2}
Slice 1: {SLICE1}

Slice 5 evidence-only freeze head:
{EVIDENCE_HEAD}

Authoritative exact-candidate run/job:
{RUN_ID} / {JOB_ID}

FILES
1. 01_INSTRUCTIONS.txt — this review contract.
2. 02_EXACT_SLICE5_CANDIDATE.txt — exact preregistration, workflow, validator, frozen harness,
   marker, authorization boundary and preserved RED evidence.
3. 03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt — exact frozen runtime contract,
   NORM-032 and inherited time/nonce source semantics, exact closed Slice 4/Slice 1 runtime
   dependencies and inherited acceptance sources executed by the final workflow.
4. 04_CONSTRUCTION_EVIDENCE.txt — exact final run/job metadata and raw log, dependency
   immutability diff, construction-green/freeze records and preserved RED.
5. 05_SHA256_MANIFEST.txt — exact SHA-256 for files 1-4.

REVIEW SCOPE
Review only bounded local QualifiedTimeProof / TimeSourceAttestation validation:
- exact required-field parity;
- source_attestations exact JSON-array semantics represented as Python list only;
- cardinality 2..3;
- exact TimeSourceAttestation shape;
- nonce exact 64 ASCII hex characters, with upper/lower case accepted as frozen;
- effective_sequence non-boolean signed-int64 non-negative closure;
- generic CanonicalId/Digest opacity plus inherited GCP string validity;
- closed Slice 4 DecisionPresealContext local revalidation;
- exact equality of time-proof decision_preseal_digest with supplied DPS decision_preseal_digest;
- no invented time_proof_digest algorithm;
- duplicate source IDs remain structural-only and do not self-prove source independence;
- explicit non-authority metadata, statelessness, workflow direct-trigger coverage and dependency immutability.

IMPORTANT NONCLAIMS
Slice 5 does NOT prove or authorize:
- NonceLedger state or single-use nonce consumption;
- source ACTIVE status at effective sequence;
- time-source registry membership or independence;
- attestation signature/MAC validity;
- freshness or replay-window validity;
- qualified time availability;
- local clock correctness;
- time_proof_digest cryptographic correctness;
- VerifiedStateSeal correctness;
- COMMIT_WITH_SEAL/current-head recheck;
- runtime qualification, release, deployment, production, policy or terminal authority.

A locally valid QualifiedTimeProof remains authority effect NONE.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact code/tests/logs, not PASS labels;
- test list-vs-tuple behavior, array cardinality, duplicate source IDs, extra/missing fields,
  nonce Unicode/non-ASCII edge cases, bool/int confusion, opaque-digest overvalidation,
  malformed supplied DPS/read-set/effect context, GCP-invalid strings, digest mismatch,
  mutation/state poisoning, exception-to-success paths and hidden authority grants;
- specifically check that duplicate sources are not misrepresented as independent and that
  no local result claims nonce consumption/source status/freshness/signature verification;
- do not demand runtime time-source authority evidence as if this bounded local validator claims it.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact Slice 5 candidate, frozen schema and closed dependency candidates, run/job,
and packet hashes used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I5_01_TO_I5_16_ASSESSMENT
Assess every frozen I5 case and identify false-green or untested local paths.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what positive bounded Slice 5 construction proves and does not prove.
State whether bounded Slice 5 construction may be adjudicated.
Do not grant qualified time, runtime qualification or downstream authority.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 5 independent-review gate.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    candidate_paths=[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice5.yml",
      "governance-runtime/r8_v15_r1_timeproof_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice5.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"02_EXACT_SLICE5_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 5 exact candidate bytes\n")
        fp.write(sh(["git","show","--no-patch","--format=fuller",CANDIDATE]))
        fp.write(b"\n===== DIFF FROM CLOSED SLICE 4 CANDIDATE =====\n")
        fp.write(sh(["git","diff","--name-status",SLICE4,CANDIDATE]))
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE,path,"SLICE 5 CANDIDATE FILE"))

    dependency_paths=[
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/gcp-rvm-2.json"),
      (FROZEN_SCHEMA,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V6.md"),
      (SLICE1,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (SLICE4,"governance-runtime/r8_v15_r1_preseal_validator.py"),
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
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE5-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT/"04_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 5 exact construction evidence\n")
        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run,indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0],indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(raw_log)
        if not raw_log.endswith(b"\n"): fp.write(b"\n")
        fp.write(b"\n===== CLOSED DEPENDENCY IMMUTABILITY DIFF =====\n")
        immut=sh([
          "git","diff","--name-status",SLICE4,CANDIDATE,"--",
          "schemas/governance-r8/v15-r1",
          "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py",
          "governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py",
        ])
        fp.write(immut if immut else b"(none)\n")
        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD,path,"SLICE 5 EVIDENCE"))

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt",
      "02_EXACT_SLICE5_CANDIDATE.txt",
      "03_FROZEN_CONTRACTS_SOURCES_DEPENDENCIES.txt",
      "04_CONSTRUCTION_EVIDENCE.txt",
    ]]
    manifest=[
      "R8 v15-r1 Slice 5 fresh blind review packet SHA-256 manifest",
      f"candidate={CANDIDATE}",
      f"frozen_schema={FROZEN_SCHEMA}",
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
