#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BATCH_ANCHOR="0441370a1d9f2d80a75926839294eb5fba32faaf"
SLICES={
  14:{
    "candidate":"5c0e6e47d7b4e23f0be0b9137e1d67f3ab73b88b",
    "evidence_head":"062868cbd6fb744f11b981ae95d459a530c43a9b",
    "final_run":36132624964,"final_job":108063174078,
    "mechanism_run":36132571407,"mechanism_job":108062990412,
    "red_run":36132480254,"red_job":108062710836,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice14.yml",
      "governance-runtime/r8_v15_r1_rcs_vector_result_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice14.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-CONSTRUCTION-FAILURE-001.json"
    ],
    "evidence_paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE14-CONSTRUCTION-FAILURE-001.json"
    ]
  },
  15:{
    "candidate":"1dcccf04e8c05f8acae145fa63c140d44e68d882",
    "evidence_head":"2215321c1f5ca408cd2eb327e53dabbbc14852ea",
    "final_run":36133071805,"final_job":108064603054,
    "mechanism_run":36133009022,"mechanism_job":108064397273,
    "red_run":36132791973,"red_job":108063707502,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice15.yml",
      "governance-runtime/r8_v15_r1_rcs_aggregate_result_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice15.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-CONSTRUCTION-FAILURE-001.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-CI-TRIGGER-GAP-001.json"
    ],
    "evidence_paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-CONSTRUCTION-FAILURE-001.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE15-CI-TRIGGER-GAP-001.json"
    ]
  },
  16:{
    "candidate":"d9a935a0e418e70a0f63904c98547ff4590d8f72",
    "evidence_head":"d5ab8805aa82420e4bc0f33934bf4c0e8fae0106",
    "final_run":36133429217,"final_job":108065756277,
    "mechanism_run":36133373722,"mechanism_job":108065584636,
    "red_run":36133275744,"red_job":108065268935,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice16.yml",
      "governance-runtime/r8_v15_r1_rcs_evidence_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice16.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-CONSTRUCTION-FAILURE-001.json"
    ],
    "evidence_paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE16-CONSTRUCTION-FAILURE-001.json"
    ]
  }
}
OUT=pathlib.Path("review-packet-slices14-16"); OUT.mkdir(exist_ok=True)

def sh(args): return subprocess.check_output(args)
def sha(b): return hashlib.sha256(b).hexdigest()
def show(ref,path): return sh(["git","show",f"{ref}:{path}"])
def blob(ref,path): return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()
def gh(endpoint): return json.loads(sh(["gh","api",endpoint]))

def section(ref,path,title):
    b=show(ref,path)
    return (
      f"\n===== BEGIN {title}: {ref}:{path} =====\n"
      f"git_blob_sha1={blob(ref,path)}\nsha256={sha(b)}\nbyte_count={len(b)}\n"
    ).encode()+b+(b"" if b.endswith(b"\n") else b"\n")+f"===== END {title}: {ref}:{path} =====\n".encode()

def run_evidence(run_id,job_id,label):
    run=gh(f"repos/{REPO}/actions/runs/{run_id}")
    jobs=gh(f"repos/{REPO}/actions/runs/{run_id}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==job_id][0]
    log=sh(["gh","run","view",str(run_id),"--repo",REPO,"--log"])
    out=(f"\n===== {label} RUN METADATA =====\n"+json.dumps(run,indent=2)+"\n").encode()
    out+=(f"\n===== {label} JOB METADATA =====\n"+json.dumps(job,indent=2)+"\n").encode()
    out+=f"\n===== {label} RAW LOG =====\n".encode()+log
    if not log.endswith(b"\n"): out+=b"\n"
    return out

def main():
    refs=[FROZEN,BASELINE,BATCH_ANCHOR]+[v["candidate"] for v in SLICES.values()]+[v["evidence_head"] for v in SLICES.values()]
    for ref in refs:
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref
    for n,s in SLICES.items():
        final=gh(f"repos/{REPO}/actions/runs/{s['final_run']}")
        assert final["status"]=="completed" and final["conclusion"]=="success" and final["head_sha"]==s["candidate"]
        mechanism=gh(f"repos/{REPO}/actions/runs/{s['mechanism_run']}")
        assert mechanism["status"]=="completed" and mechanism["conclusion"]=="success"
        red=gh(f"repos/{REPO}/actions/runs/{s['red_run']}")
        assert red["status"]=="completed" and red["conclusion"]=="failure"

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICES 14–16 — FRESH BLIND THREE-LOOP BATCH REVIEW

Use only the seven supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Common frozen schema: {FROZEN}
Common closed implementation baseline (Slice 7): {BASELINE}
Governance-only Slices 11–13 closure anchor: {BATCH_ANCHOR}

Slice 14 — ResolverConformanceVectorResult local validator
candidate: {SLICES[14]["candidate"]}
evidence head: {SLICES[14]["evidence_head"]}
final run/job: {SLICES[14]["final_run"]} / {SLICES[14]["final_job"]}
mechanism GREEN run/job: {SLICES[14]["mechanism_run"]} / {SLICES[14]["mechanism_job"]}
preserved RED run/job: {SLICES[14]["red_run"]} / {SLICES[14]["red_job"]}

Slice 15 — ResolverConformanceAggregateResult local validator
candidate: {SLICES[15]["candidate"]}
evidence head: {SLICES[15]["evidence_head"]}
final run/job: {SLICES[15]["final_run"]} / {SLICES[15]["final_job"]}
mechanism GREEN run/job: {SLICES[15]["mechanism_run"]} / {SLICES[15]["mechanism_job"]}
preserved RED run/job: {SLICES[15]["red_run"]} / {SLICES[15]["red_job"]}
NOTE: Slice 15 also preserves a CI-trigger transport gap: the first mechanism commit
8ad0438b42e4e64a1c27a2058b57304fe5a554bd produced no check suite/status. It is NOT test
evidence and was followed by a semantics-neutral successor mechanism commit
a4bc656c687d73a3673d8ee9c9f2f372447475f0 with fresh GREEN execution.

Slice 16 — ResolverConformanceEvidence local structural validator
candidate: {SLICES[16]["candidate"]}
evidence head: {SLICES[16]["evidence_head"]}
final run/job: {SLICES[16]["final_run"]} / {SLICES[16]["final_job"]}
mechanism GREEN run/job: {SLICES[16]["mechanism_run"]} / {SLICES[16]["mechanism_job"]}
preserved RED run/job: {SLICES[16]["red_run"]} / {SLICES[16]["red_job"]}

FILES
1. 01_INSTRUCTIONS.txt
2. 02_EXACT_SLICE14_CANDIDATE.txt
3. 03_EXACT_SLICE15_CANDIDATE.txt
4. 04_EXACT_SLICE16_CANDIDATE.txt
5. 05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt
6. 06_BATCH_CONSTRUCTION_EVIDENCE.txt — raw final GREEN, mechanism GREEN and RED logs.
7. 07_SHA256_MANIFEST.txt

REVIEW SCOPE
Review each slice independently from the common closed baseline. No batch slice may transfer
authority or act as dependency authority for another batch slice.

Slice 14 scope:
- exact ResolverConformanceVectorResult field closure;
- PASS/FAIL result enum closure;
- non-empty GCP-valid opaque IDs/digests;
- no vector execution, digest correctness, conformance qualification or authority claim.

Slice 15 scope:
- exact ResolverConformanceAggregateResult field closure;
- PASS/FAIL status enum;
- exact frozen integer bounds for vector_count/passed_vector_count with bool rejection;
- opaque aggregate digest;
- no invented passed<=vector_count or status/count relation;
- CI-trigger gap must remain UNAVAILABLE/non-test evidence, not a failed or passed scientific result.

Slice 16 scope:
- exact ResolverConformanceEvidence top-level closure;
- self-contained local structural validation of nested RCS-1 suite, vector-result list,
  vector-digest list and aggregate result without importing unreviewed Slice 14/15 siblings;
- PASS/FAIL/EXPIRED/UNAVAILABLE status closure;
- frozen x-validator semantic invariants remain false/unverified;
- no array/count/status relationship invented beyond frozen JSON schema;
- no freshness/current PASS/resolver qualification/evidence-promotion/authority claim.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact schemas/sources, validators, harnesses, raw GREEN/RED logs and the Slice 15
  trigger-gap record;
- test missing/extra/type/GCP edge cases, bool/int confusion, nested shape enforcement,
  opaque-digest overvalidation, state poisoning, exception-to-success paths and hidden grants;
- distinguish local structural validation from current/authorized/qualified semantics.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_BATCH_IDENTITY
Repeat common baseline plus exact candidates/evidence heads/final+mechanism+RED run/job,
Slice 15 trigger-gap identity, and packet hashes.

C. CRITICAL_FINDINGS
Concrete findings only, tagged Slice 14 / Slice 15 / Slice 16 / packet.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. THREE_LOOP_ACCEPTANCE_ASSESSMENT
F1 Slice 14 — I14-01..I14-16
F2 Slice 15 — I15-01..I15-16
F3 Slice 16 — I16-01..I16-16
Identify any false-green or untested local path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what each slice proves and does not prove. No slice may transfer authority to
another batch slice. Do not grant resolver authorization, conformance qualification/freshness,
runtime qualification, evidence promotion, release, deployment, production, policy or terminal authority.

H. FINAL_GATES
For each exact candidate state YES/NO whether its independent-review gate may close.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    for idx,n in enumerate((14,15,16),start=2):
        s=SLICES[n]
        p=OUT/f"{idx:02d}_EXACT_SLICE{n}_CANDIDATE.txt"
        with p.open("wb") as fp:
            fp.write(f"R8 v15-r1 Slice {n} exact candidate bytes\n".encode())
            fp.write(sh(["git","show","--no-patch","--format=fuller",s["candidate"]]))
            fp.write(b"\n===== DIFF FROM COMMON CLOSED SLICE 7 BASELINE =====\n")
            fp.write(sh(["git","diff","--name-status",BASELINE,s["candidate"]]))
            for path in s["paths"]:
                fp.write(section(s["candidate"],path,f"SLICE {n} CANDIDATE FILE"))
            for evpath in s["evidence_paths"]:
                fp.write(section(s["evidence_head"],evpath,f"SLICE {n} EVIDENCE"))

    shared=[
      (FROZEN,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (FROZEN,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V13.md"),
      (FROZEN,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V14.md"),
      (BASELINE,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (BATCH_ANCHOR,"governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH11-13-CLOSURE.json"),
    ]
    with (OUT/"05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt").open("wb") as fp:
        fp.write(b"Shared exact frozen contracts, source basis, canonicalizer and governance-only batch anchor.\n")
        for ref,path in shared: fp.write(section(ref,path,"SHARED FROZEN SOURCE / BASELINE"))

    with (OUT/"06_BATCH_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slices 14-16 exact batch construction evidence\n")
        for n,s in SLICES.items():
            fp.write(run_evidence(s["final_run"],s["final_job"],f"SLICE {n} FINAL EXACT-CANDIDATE GREEN"))
            fp.write(run_evidence(s["mechanism_run"],s["mechanism_job"],f"SLICE {n} MECHANISM GREEN"))
            fp.write(run_evidence(s["red_run"],s["red_job"],f"SLICE {n} PRESERVED RED"))
            fp.write(b"\n===== CLOSED-BASELINE IMMUTABILITY DIFF =====\n")
            diff=sh(["git","diff","--name-status",BASELINE,s["candidate"],"--",
              "schemas/governance-r8/v15-r1",
              "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
              "governance-runtime/r8_v15_r1_state_roots.py",
              "governance-runtime/r8_v15_r1_stc_validator.py",
              "governance-runtime/r8_v15_r1_preseal_validator.py",
              "governance-runtime/r8_v15_r1_timeproof_validator.py",
              "governance-runtime/r8_v15_r1_seal_validator.py",
              "governance-runtime/r8_v15_r1_effect_intent_validator.py"])
            fp.write(diff if diff else b"(none)\n")

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt","02_EXACT_SLICE14_CANDIDATE.txt","03_EXACT_SLICE15_CANDIDATE.txt",
      "04_EXACT_SLICE16_CANDIDATE.txt","05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt",
      "06_BATCH_CONSTRUCTION_EVIDENCE.txt"
    ]]
    lines=["R8 v15-r1 Slices 14-16 combined fresh blind review packet SHA-256 manifest",""]
    for p in files: lines.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"07_SHA256_MANIFEST.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    for p in sorted(OUT.iterdir()):
        print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__": main()
