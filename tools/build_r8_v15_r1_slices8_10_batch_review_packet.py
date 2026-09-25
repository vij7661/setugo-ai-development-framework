#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE7_CLOSURE="5477df994c2cc9db0033742e189b906eb20247c1"
SLICE7="751162ee42c603cb6c84ee12021d16bab6fa626b"

LOOPS = {
    8: {
        "candidate":"fa94f8dd96bc54515baabf3f34ed37d25f41f6db",
        "evidence_head":"be2a88bb85a59f253fbadbfcf400dbff2f15f064",
        "run":36121677646,
        "job":108028378950,
        "red_run":36121507503,
        "validator":"governance-runtime/r8_v15_r1_effect_state_validator.py",
        "test":"governance-runtime/test_r8_v15_r1_implementation_slice8.py",
        "workflow":".github/workflows/r8-v15-r1-implementation-slice8.yml",
        "scope":"Local EffectStateRecord validation",
    },
    9: {
        "candidate":"9d82c3f095fa08e81808d7e0d4c4b0a0a26556ea",
        "evidence_head":"ec2862c0cf1bfbd0cefc08537e6359495d6c842f",
        "run":36121983437,
        "job":108029364363,
        "red_run":36121849545,
        "validator":"governance-runtime/r8_v15_r1_evidence_record_validator.py",
        "test":"governance-runtime/test_r8_v15_r1_implementation_slice9.py",
        "workflow":".github/workflows/r8-v15-r1-implementation-slice9.yml",
        "scope":"Local EvidenceRecord validation",
    },
    10: {
        "candidate":"33d112b5e2d3d6bc75fb07f14f6cf55c4d6b19f4",
        "evidence_head":"e964b17d54aac10f90c9ab1206a21e1d6825441e",
        "run":36122429875,
        "job":108030797431,
        "red_run":36122231238,
        "validator":"governance-runtime/r8_v15_r1_review_attestation_validator.py",
        "test":"governance-runtime/test_r8_v15_r1_implementation_slice10.py",
        "workflow":".github/workflows/r8-v15-r1-implementation-slice10.yml",
        "scope":"Local ReviewAttestation validation",
    },
}

OUT=pathlib.Path("review-packet-slices8-10")
OUT.mkdir(exist_ok=True)

def sh(args):
    return subprocess.check_output(args)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git_show(ref,path):
    return sh(["git","show",f"{ref}:{path}"])

def git_blob(ref,path):
    return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()

def gh_json(endpoint):
    return json.loads(sh(["gh","api",endpoint]))

def exact_section(ref,path,title):
    data=git_show(ref,path)
    return (
      f"\n===== BEGIN {title}: {ref}:{path} =====\n"
      f"git_blob_sha1={git_blob(ref,path)}\n"
      f"sha256={sha(data)}\n"
      f"byte_count={len(data)}\n"
    ).encode()+data+(b"" if data.endswith(b"\n") else b"\n")+f"===== END {title}: {ref}:{path} =====\n".encode()

def run_and_job(loop):
    cfg=LOOPS[loop]
    run=gh_json(f"repos/{REPO}/actions/runs/{cfg['run']}")
    assert run["status"]=="completed" and run["conclusion"]=="success"
    assert run["head_sha"]==cfg["candidate"], (loop, run["head_sha"])
    jobs=gh_json(f"repos/{REPO}/actions/runs/{cfg['run']}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==cfg["job"]]
    assert len(job)==1 and job[0]["conclusion"]=="success"
    red=gh_json(f"repos/{REPO}/actions/runs/{cfg['red_run']}")
    assert red["status"]=="completed" and red["conclusion"]=="failure"
    log=sh(["gh","run","view",str(cfg["run"]),"--repo",REPO,"--log"])
    return run,job[0],red,log

def main():
    refs=[FROZEN_SCHEMA,SLICE7_CLOSURE,SLICE7]
    for cfg in LOOPS.values():
        refs.extend([cfg["candidate"],cfg["evidence_head"]])
    for ref in refs:
        got=sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()
        assert got==ref,(ref,got)

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICES 8-10 — FRESH BLIND THREE-LOOP BATCH REVIEW

This is the fresh independent review after the user-directed three-loop construction batch.
Use only these seven supplied files. Do not use prior conversations, prior reviewer findings,
prior adjudications, or model recollection.

COMMON CLOSED BASELINE
Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Closed Slice 7 implementation candidate:
{SLICE7}

Closed Slice 7 evidence/closure head:
{SLICE7_CLOSURE}

LOOP 1 / SLICE 8
Scope: {LOOPS[8]['scope']}
Exact candidate: {LOOPS[8]['candidate']}
Evidence head: {LOOPS[8]['evidence_head']}
Final run/job: {LOOPS[8]['run']} / {LOOPS[8]['job']}
Preserved preregistered RED run: {LOOPS[8]['red_run']}

LOOP 2 / SLICE 9
Scope: {LOOPS[9]['scope']}
Exact candidate: {LOOPS[9]['candidate']}
Evidence head: {LOOPS[9]['evidence_head']}
Final run/job: {LOOPS[9]['run']} / {LOOPS[9]['job']}
Preserved preregistered RED run: {LOOPS[9]['red_run']}

LOOP 3 / SLICE 10
Scope: {LOOPS[10]['scope']}
Exact candidate: {LOOPS[10]['candidate']}
Evidence head: {LOOPS[10]['evidence_head']}
Final run/job: {LOOPS[10]['run']} / {LOOPS[10]['job']}
Preserved preregistered RED run: {LOOPS[10]['red_run']}

CRITICAL BATCH RULE
Slices 8, 9, and 10 are independent descendants of the same closed Slice 7 baseline.
Do NOT treat Slice 8 as authority/dependency for Slice 9, or Slice 9 as authority/dependency
for Slice 10. Do NOT review a synthetic merged candidate. Judge each exact candidate at its
own SHA, then give one combined batch disposition.

FILES
1. 01_INSTRUCTIONS.txt
2. 02_EXACT_SLICE8_CANDIDATE.txt
3. 03_EXACT_SLICE9_CANDIDATE.txt
4. 04_EXACT_SLICE10_CANDIDATE.txt
5. 05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt
6. 06_BATCH_CONSTRUCTION_EVIDENCE.txt
7. 07_SHA256_MANIFEST.txt

SLICE 8 REVIEW SCOPE
Review only local EffectStateRecord structure and binding to a supplied locally valid
EffectIntent:
- exact frozen field shape and state enum;
- nullable executor/reconciliation fields;
- SUCCEEDED_RECONCILED requires both executor_identity_digest and
  reconciliation_evidence_digest non-null/non-empty;
- effect_intent_id/idempotency_key equality to supplied locally valid EffectIntent;
- no state-transition legality, executor qualification, provider success,
  reconciliation truth, compensation correctness, or runtime authority is claimed.

SLICE 9 REVIEW SCOPE
Review only local EvidenceRecord structure:
- exact frozen field shape;
- list-only/non-empty input_object_ids/input_object_digests;
- opaque non-empty GCP-valid strings;
- Sequence closure;
- do NOT invent equal-length, uniqueness, sorting or positional-pairing rules absent from schema;
- x-validator invariants about evidence-class upgrade, temporal revocation and mandatory
  evidence/promotion remain explicit NONCLAIMS.

SLICE 10 REVIEW SCOPE
Review only local ReviewAttestation structure:
- exact top-level and nested review-dimension field shape;
- list-only/non-empty review_dimension_results;
- result enum PASS/FAIL/UNAVAILABLE;
- opaque non-empty GCP-valid strings;
- duplicate dimension IDs remain structural-only unless frozen otherwise;
- all-PASS results MUST NOT self-grant review-gate closure;
- reviewer independence, signature validity, attestation digest correctness, review-gate
  closure and promotion remain explicit NONCLAIMS.

SHARED REVIEW POSTURE
- assume false-green until evidenced otherwise;
- inspect exact code/tests/raw logs, not PASS labels;
- independently check each candidate diff against closed Slice 7;
- check frozen-schema and closed Slice 1-7 implementation immutability;
- examine bool/string/list/mapping confusion, missing/extra fields, GCP-invalid Unicode,
  enum substitutions, nullable-field edge cases, opaque-digest overvalidation,
  state poisoning, exception-to-success paths and hidden authority grants;
- distinguish structural acceptance from authority/runtime truth;
- construction green does not itself close any independent-review gate.

REQUIRED RESPONSE — RETURN ONLY SECTIONS A-H

A. OVERALL_DISPOSITION
Choose exactly one for the three-loop batch:
BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_BATCH_IDENTITY
Repeat frozen baseline plus all three exact candidate/evidence-head/run/job identities and
packet hashes used.

C. CRITICAL_FINDINGS
Concrete findings only. Identify affected slice(s).

D. HIGH_FINDINGS
Concrete findings only. Identify affected slice(s).

E. MEDIUM_LOW_FINDINGS
Concrete findings only. Identify affected slice(s).

F. THREE_LOOP_ACCEPTANCE_ASSESSMENT
F1. Slice 8 — assess I8-01 through I8-16.
F2. Slice 9 — assess I9-01 through I9-16.
F3. Slice 10 — assess I10-01 through I10-16.
Identify false-green or untested local paths separately per slice.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what each bounded local construction proves and does not prove.
State whether each of Slices 8, 9, and 10 may be independently adjudicated.
Do not grant runtime qualification, evidence promotion, review-gate closure, release,
deployment, production, policy or terminal authority.

H. FINAL_GATES
For each exact candidate, state YES/NO/INSUFFICIENT_EVIDENCE on whether its own fresh
independent-review gate may close:
- Slice 8 {LOOPS[8]['candidate']}
- Slice 9 {LOOPS[9]['candidate']}
- Slice 10 {LOOPS[10]['candidate']}

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    for loop,filename in [(8,"02_EXACT_SLICE8_CANDIDATE.txt"),(9,"03_EXACT_SLICE9_CANDIDATE.txt"),(10,"04_EXACT_SLICE10_CANDIDATE.txt")]:
        cfg=LOOPS[loop]
        candidate_paths=[
            f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{loop}-PREREGISTRATION.md",
            cfg["workflow"],
            cfg["validator"],
            cfg["test"],
            f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{loop}-MARKER.json",
            f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{loop}-CONSTRUCTION-FAILURE-001.json",
        ]
        with (OUT/filename).open("wb") as fp:
            fp.write(f"R8 v15-r1 Slice {loop} exact candidate bytes\n".encode())
            fp.write(sh(["git","show","--no-patch","--format=fuller",cfg["candidate"]]))
            fp.write(b"\n===== DIFF FROM CLOSED SLICE 7 CANDIDATE =====\n")
            fp.write(sh(["git","diff","--name-status",SLICE7,cfg["candidate"]]))
            for path in candidate_paths:
                fp.write(exact_section(cfg["candidate"],path,f"SLICE {loop} CANDIDATE FILE"))

    shared_paths=[
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN_SCHEMA,"schemas/governance-r8/v15-r1/schema-provenance-source-map.json"),
      (FROZEN_SCHEMA,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V7.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V8.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V9.md"),
      (FROZEN_SCHEMA,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V10.md"),
      (SLICE7,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (SLICE7,"governance-runtime/r8_v15_r1_effect_intent_validator.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice7.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice6.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice5.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice4.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice3.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice2.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice1.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py"),
      (SLICE7,"governance-runtime/test_r8_v15_r1_post_freeze_regression.py"),
    ]
    with (OUT/"05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 shared frozen contracts, governing sources and closed Slice 7 baseline.\n")
        for ref,path in shared_paths:
            fp.write(exact_section(ref,path,"SHARED FROZEN CONTRACT / SOURCE / BASELINE"))

    with (OUT/"06_BATCH_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slices 8-10 three-loop batch exact construction evidence\n")
        for loop in (8,9,10):
            cfg=LOOPS[loop]
            run,job,red,log=run_and_job(loop)
            fp.write(f"\n######## SLICE {loop} ########\n".encode())
            fp.write(b"\n===== FINAL GREEN RUN METADATA =====\n")
            fp.write((json.dumps(run,indent=2)+"\n").encode())
            fp.write(b"\n===== FINAL GREEN JOB METADATA =====\n")
            fp.write((json.dumps(job,indent=2)+"\n").encode())
            fp.write(b"\n===== FINAL GREEN RAW LOG =====\n")
            fp.write(log)
            if not log.endswith(b"\n"): fp.write(b"\n")
            fp.write(b"\n===== PRESERVED RED RUN METADATA =====\n")
            fp.write((json.dumps(red,indent=2)+"\n").encode())
            fp.write(b"\n===== CLOSED BASELINE IMMUTABILITY DIFF =====\n")
            immut=sh([
                "git","diff","--name-status",SLICE7,cfg["candidate"],"--",
                "schemas/governance-r8/v15-r1",
                "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
                "governance-runtime/r8_v15_r1_state_roots.py",
                "governance-runtime/r8_v15_r1_stc_validator.py",
                "governance-runtime/r8_v15_r1_preseal_validator.py",
                "governance-runtime/r8_v15_r1_timeproof_validator.py",
                "governance-runtime/r8_v15_r1_seal_validator.py",
                "governance-runtime/r8_v15_r1_effect_intent_validator.py",
            ])
            fp.write(immut if immut else b"(none)\n")
            for path in [
                f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{loop}-CONSTRUCTION-GREEN.json",
                f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{loop}-FREEZE.json",
                f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{loop}-CONSTRUCTION-FAILURE-001.json",
            ]:
                fp.write(exact_section(cfg["evidence_head"],path,f"SLICE {loop} EVIDENCE"))

        fp.write(exact_section(
            sh(["git","rev-parse","HEAD"]).decode().strip(),
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICES8-10-THREE-LOOP-BATCH-REVIEW-HANDOFF.json",
            "BATCH REVIEW HANDOFF"
        ))

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt",
      "02_EXACT_SLICE8_CANDIDATE.txt",
      "03_EXACT_SLICE9_CANDIDATE.txt",
      "04_EXACT_SLICE10_CANDIDATE.txt",
      "05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt",
      "06_BATCH_CONSTRUCTION_EVIDENCE.txt",
    ]]
    manifest=[
      "R8 v15-r1 Slices 8-10 three-loop fresh blind batch review packet SHA-256 manifest",
      f"frozen_schema={FROZEN_SCHEMA}",
      f"slice7_closed_candidate={SLICE7}",
      f"slice7_closure_head={SLICE7_CLOSURE}",
      f"slice8_candidate={LOOPS[8]['candidate']}",
      f"slice8_evidence_head={LOOPS[8]['evidence_head']}",
      f"slice8_run={LOOPS[8]['run']}",
      f"slice8_job={LOOPS[8]['job']}",
      f"slice9_candidate={LOOPS[9]['candidate']}",
      f"slice9_evidence_head={LOOPS[9]['evidence_head']}",
      f"slice9_run={LOOPS[9]['run']}",
      f"slice9_job={LOOPS[9]['job']}",
      f"slice10_candidate={LOOPS[10]['candidate']}",
      f"slice10_evidence_head={LOOPS[10]['evidence_head']}",
      f"slice10_run={LOOPS[10]['run']}",
      f"slice10_job={LOOPS[10]['job']}",
      "",
    ]
    for p in files:
        manifest.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"07_SHA256_MANIFEST.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8")

    print("BATCH_PACKET_OK")
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__":
    main()
