#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BATCH_ANCHOR="525e5c90d0f16482b75595e854f647ac88eaa761"
SLICES={
  11:{
    "candidate":"4b49613a56c53048cf9531783b09ba71b64539ef",
    "evidence_head":"e432fc8dd4ba59d4212d1792a6d57c1667630ba6",
    "green_run":36126687291,"green_job":108044315351,
    "red_run":36126508455,"red_job":108043745007,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE11-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice11.yml",
      "governance-runtime/r8_v15_r1_resolver_policy_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice11.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE11-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE11-CONSTRUCTION-FAILURE-001.json"
    ]
  },
  12:{
    "candidate":"294c8b0112e1715402325836f1c8f0b58a042e70",
    "evidence_head":"abbfbf06189607056d0848cf40417b58b00b475a",
    "green_run":36127195749,"green_job":108045925273,
    "red_run":36126993234,"red_job":108045290632,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE12-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice12.yml",
      "governance-runtime/r8_v15_r1_rir_record_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice12.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE12-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE12-CONSTRUCTION-FAILURE-001.json"
    ]
  },
  13:{
    "candidate":"4f9c5f6a1a22d61a038ada48bb8ce5ce28af41f0",
    "evidence_head":"264a3cf6412b33bd13704a4110eaa44f1d8c5fde",
    "green_run":36127649764,"green_job":108047357656,
    "red_run":36127475312,"red_job":108046795282,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE13-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice13.yml",
      "governance-runtime/r8_v15_r1_rcs_suite_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice13.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE13-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE13-CONSTRUCTION-FAILURE-001.json"
    ]
  }
}
OUT=pathlib.Path("review-packet-slices11-13"); OUT.mkdir(exist_ok=True)

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
        run=gh(f"repos/{REPO}/actions/runs/{s['green_run']}")
        assert run["status"]=="completed" and run["conclusion"]=="success" and run["head_sha"]==s["candidate"]
        red=gh(f"repos/{REPO}/actions/runs/{s['red_run']}")
        assert red["status"]=="completed" and red["conclusion"]=="failure"

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICES 11–13 — FRESH BLIND THREE-LOOP BATCH REVIEW

Use only the seven supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Common frozen schema: {FROZEN}
Common closed implementation baseline (Slice 7): {BASELINE}
Governance-only Slices 8–10 closure anchor: {BATCH_ANCHOR}

Slice 11 — ResolverPolicyContract local validator
candidate: {SLICES[11]["candidate"]}
evidence head: {SLICES[11]["evidence_head"]}
final run/job: {SLICES[11]["green_run"]} / {SLICES[11]["green_job"]}
preserved RED run/job: {SLICES[11]["red_run"]} / {SLICES[11]["red_job"]}

Slice 12 — ResolverImplementationRegistryRecord local validator
candidate: {SLICES[12]["candidate"]}
evidence head: {SLICES[12]["evidence_head"]}
final run/job: {SLICES[12]["green_run"]} / {SLICES[12]["green_job"]}
preserved RED run/job: {SLICES[12]["red_run"]} / {SLICES[12]["red_job"]}

Slice 13 — ResolverConformanceSuite1 local validator
candidate: {SLICES[13]["candidate"]}
evidence head: {SLICES[13]["evidence_head"]}
final run/job: {SLICES[13]["green_run"]} / {SLICES[13]["green_job"]}
preserved RED run/job: {SLICES[13]["red_run"]} / {SLICES[13]["red_job"]}

FILES
1. 01_INSTRUCTIONS.txt
2. 02_EXACT_SLICE11_CANDIDATE.txt
3. 03_EXACT_SLICE12_CANDIDATE.txt
4. 04_EXACT_SLICE13_CANDIDATE.txt
5. 05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt
6. 06_BATCH_CONSTRUCTION_EVIDENCE.txt — includes raw GREEN and raw RED logs for all three loops.
7. 07_SHA256_MANIFEST.txt

REVIEW SCOPE
Review each slice independently from the common closed baseline. No batch slice may transfer
authority or act as dependency authority for another batch slice.

Slice 11 scope:
- exact ResolverPolicyContract required-field closure;
- non-empty GCP-valid opaque CanonicalId/Digest fields;
- no invented digest algorithm;
- no claim that rule digests are semantically correct/current/constitutional;
- no policy/resolver/runtime authorization.

Slice 12 scope:
- exact ResolverImplementationRegistryRecord field closure;
- opaque GCP-valid IDs/digests;
- nullable predecessor;
- activation/retirement Sequence lexical/type closure;
- lifecycle enum closure;
- no invented activation-vs-retirement ordering rule;
- no temporal eligibility/current-registry/tuple-uniqueness/resolver authorization claim.

Slice 13 scope:
- exact ResolverConformanceSuite1 field closure;
- opaque GCP-valid IDs/digests;
- no suite_digest recomputation;
- no generator/harness/runtime/workload identity verification;
- no conformance execution/freshness/resolver qualification claim.

Review posture:
- assume false-green until evidenced otherwise;
- inspect raw bytes, exact schemas/sources, validators, harnesses, GREEN logs and RED logs;
- test missing/extra/type/GCP edge cases, bool/int confusion for sequences, nullable handling,
  opaque-digest overvalidation, state poisoning, exception-to-success paths and hidden authority grants;
- distinguish local object validation from current/active/authorized/qualified runtime semantics.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one for the batch: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_BATCH_IDENTITY
Repeat common baseline plus exact candidates/evidence heads/run+job/RED run+job and packet hashes.

C. CRITICAL_FINDINGS
Concrete findings only, tagged Slice 11 / Slice 12 / Slice 13 / packet.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. THREE_LOOP_ACCEPTANCE_ASSESSMENT
F1 Slice 11 — I11-01..I11-16
F2 Slice 12 — I12-01..I12-16
F3 Slice 13 — I13-01..I13-16
Identify any false-green or untested local path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what each slice proves and does not prove. No slice may transfer authority to
another batch slice. Do not grant resolver authorization, conformance qualification, runtime
qualification, evidence promotion, release, deployment, production, policy or terminal authority.

H. FINAL_GATES
For each exact candidate state YES/NO whether its independent-review gate may close.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    for idx,n in enumerate((11,12,13),start=2):
        s=SLICES[n]
        p=OUT/f"{idx:02d}_EXACT_SLICE{n}_CANDIDATE.txt"
        with p.open("wb") as fp:
            fp.write(f"R8 v15-r1 Slice {n} exact candidate bytes\n".encode())
            fp.write(sh(["git","show","--no-patch","--format=fuller",s["candidate"]]))
            fp.write(b"\n===== DIFF FROM COMMON CLOSED SLICE 7 BASELINE =====\n")
            fp.write(sh(["git","diff","--name-status",BASELINE,s["candidate"]]))
            for path in s["paths"]:
                fp.write(section(s["candidate"],path,f"SLICE {n} CANDIDATE FILE"))
            for evpath in (
              f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-GREEN.json",
              f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-FREEZE.json",
              f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-FAILURE-001.json",
            ):
                fp.write(section(s["evidence_head"],evpath,f"SLICE {n} EVIDENCE"))

    shared=[
      (FROZEN,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (FROZEN,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V12.md"),
      (FROZEN,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V13.md"),
      (FROZEN,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V14.md"),
      (BASELINE,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (BATCH_ANCHOR,"governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH8-10-CLOSURE.json"),
    ]
    with (OUT/"05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt").open("wb") as fp:
        fp.write(b"Shared exact frozen contracts, source basis, canonicalizer and governance-only batch anchor.\n")
        for ref,path in shared: fp.write(section(ref,path,"SHARED FROZEN SOURCE / BASELINE"))

    with (OUT/"06_BATCH_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slices 11-13 exact batch construction evidence\n")
        for n,s in SLICES.items():
            fp.write(run_evidence(s["green_run"],s["green_job"],f"SLICE {n} FINAL GREEN"))
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
      "01_INSTRUCTIONS.txt","02_EXACT_SLICE11_CANDIDATE.txt","03_EXACT_SLICE12_CANDIDATE.txt",
      "04_EXACT_SLICE13_CANDIDATE.txt","05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt",
      "06_BATCH_CONSTRUCTION_EVIDENCE.txt"
    ]]
    lines=["R8 v15-r1 Slices 11-13 combined fresh blind review packet SHA-256 manifest",""]
    for p in files: lines.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"07_SHA256_MANIFEST.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    for p in sorted(OUT.iterdir()):
        print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__": main()
