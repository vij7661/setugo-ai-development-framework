#!/usr/bin/env python3
import base64
import hashlib
import json
import os
import pathlib
import subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
BASE="5477df994c2cc9db0033742e189b906eb20247c1"
FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"

LOOPS=[
 {
  "slice":"8","candidate":"fa94f8dd96bc54515baabf3f34ed37d25f41f6db",
  "evidence_head":"be2a88bb85a59f253fbadbfcf400dbff2f15f064",
  "run":36121677646,"job":108028378950,"red_run":36121507503,"red_job":108027844694,
  "subject":"EffectStateRecord local validation",
  "paths":[
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-PREREGISTRATION.md",
   ".github/workflows/r8-v15-r1-implementation-slice8.yml",
   "governance-runtime/r8_v15_r1_effect_state_validator.py",
   "governance-runtime/test_r8_v15_r1_implementation_slice8.py",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-MARKER.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-CONSTRUCTION-FAILURE-001.json",
  ],
  "evidence_paths":[
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-CONSTRUCTION-GREEN.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-FREEZE.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE8-CONSTRUCTION-FAILURE-001.json",
  ],
 },
 {
  "slice":"9","candidate":"9d82c3f095fa08e81808d7e0d4c4b0a0a26556ea",
  "evidence_head":"ec2862c0cf1bfbd0cefc08537e6359495d6c842f",
  "run":36121983437,"job":108029364363,"red_run":36121849545,"red_job":108028937278,
  "subject":"EvidenceRecord local validation",
  "paths":[
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-PREREGISTRATION.md",
   ".github/workflows/r8-v15-r1-implementation-slice9.yml",
   "governance-runtime/r8_v15_r1_evidence_record_validator.py",
   "governance-runtime/test_r8_v15_r1_implementation_slice9.py",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-MARKER.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-CONSTRUCTION-FAILURE-001.json",
  ],
  "evidence_paths":[
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-CONSTRUCTION-GREEN.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-FREEZE.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE9-CONSTRUCTION-FAILURE-001.json",
  ],
 },
 {
  "slice":"10","candidate":"33d112b5e2d3d6bc75fb07f14f6cf55c4d6b19f4",
  "evidence_head":"e964b17d54aac10f90c9ab1206a21e1d6825441e",
  "run":36122429875,"job":108030797431,"red_run":36122231238,"red_job":108030145937,
  "subject":"ReviewAttestation local validation",
  "paths":[
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-PREREGISTRATION.md",
   ".github/workflows/r8-v15-r1-implementation-slice10.yml",
   "governance-runtime/r8_v15_r1_review_attestation_validator.py",
   "governance-runtime/test_r8_v15_r1_implementation_slice10.py",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-MARKER.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-CONSTRUCTION-FAILURE-001.json",
  ],
  "evidence_paths":[
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-CONSTRUCTION-GREEN.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-FREEZE.json",
   "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE10-CONSTRUCTION-FAILURE-001.json",
  ],
 },
]

OUT=pathlib.Path("review-packet-three-loop")
OUT.mkdir(exist_ok=True)

def sh(args):
    return subprocess.check_output(args)

def gh_json(endpoint):
    return json.loads(sh(["gh","api",endpoint]))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fetch_bytes(ref,path):
    obj=gh_json(f"repos/{REPO}/contents/{path}?ref={ref}")
    if obj.get("type")!="file" or obj.get("encoding")!="base64":
        raise RuntimeError(f"unsupported content response for {ref}:{path}")
    return base64.b64decode(obj["content"])

def section(ref,path,title):
    data=fetch_bytes(ref,path)
    return (
      f"\n===== BEGIN {title}: {ref}:{path} =====\n"
      f"sha256={sha(data)}\n"
      f"byte_count={len(data)}\n"
    ).encode()+data+(b"" if data.endswith(b"\n") else b"\n")+f"===== END {title}: {ref}:{path} =====\n".encode()

def run_bundle(item):
    run=gh_json(f"repos/{REPO}/actions/runs/{item['run']}")
    if run["status"]!="completed" or run["conclusion"]!="success" or run["head_sha"]!=item["candidate"]:
        raise RuntimeError(f"final run mismatch for Slice {item['slice']}")
    jobs=gh_json(f"repos/{REPO}/actions/runs/{item['run']}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==item["job"]]
    if len(job)!=1 or job[0]["conclusion"]!="success":
        raise RuntimeError(f"final job mismatch for Slice {item['slice']}")
    final_log=sh(["gh","run","view",str(item["run"]),"--repo",REPO,"--log"])
    red=gh_json(f"repos/{REPO}/actions/runs/{item['red_run']}")
    red_jobs=gh_json(f"repos/{REPO}/actions/runs/{item['red_run']}/jobs")["jobs"]
    red_job=[j for j in red_jobs if j["id"]==item["red_job"]]
    if red["status"]!="completed" or red["conclusion"]!="failure" or len(red_job)!=1:
        raise RuntimeError(f"red evidence mismatch for Slice {item['slice']}")
    red_log=sh(["gh","run","view",str(item["red_run"]),"--repo",REPO,"--log"])
    return run,job[0],final_log,red,red_job[0],red_log

def compare_summary(candidate):
    c=gh_json(f"repos/{REPO}/compare/{BASE}...{candidate}")
    return {
      "status":c.get("status"),
      "ahead_by":c.get("ahead_by"),
      "behind_by":c.get("behind_by"),
      "total_commits":c.get("total_commits"),
      "files":[
        {
          "filename":f["filename"],
          "status":f["status"],
          "additions":f.get("additions"),
          "deletions":f.get("deletions"),
          "changes":f.get("changes"),
        } for f in c.get("files",[])
      ],
    }

def main():
    instructions=f"""R8 v15-r1 — THREE-LOOP BATCH FRESH BLIND INDEPENDENT REVIEW

Use only these seven supplied files. Do not use prior conversation history, prior reviewer
outputs/adjudications, or model recollection.

Closed common base:
{BASE}

Frozen executable-schema candidate:
{FROZEN}

Loop 1 / Slice 8 exact candidate:
{LOOPS[0]['candidate']}
Subject: {LOOPS[0]['subject']}
Final run/job: {LOOPS[0]['run']} / {LOOPS[0]['job']}

Loop 2 / Slice 9 exact candidate:
{LOOPS[1]['candidate']}
Subject: {LOOPS[1]['subject']}
Final run/job: {LOOPS[1]['run']} / {LOOPS[1]['job']}

Loop 3 / Slice 10 exact candidate:
{LOOPS[2]['candidate']}
Subject: {LOOPS[2]['subject']}
Final run/job: {LOOPS[2]['run']} / {LOOPS[2]['job']}

IMPORTANT BATCH TOPOLOGY
All three candidates are siblings from the exact same already-closed Slice 7 base.
No candidate depends on another unreviewed batch candidate.
None has been adjudicated closed.
Review each exact candidate separately, then give one batch disposition.

SLICE 8 SCOPE
Local EffectStateRecord structure and binding to a supplied locally valid EffectIntent only.
A state label, including SUCCEEDED_RECONCILED, is NOT proof that an external effect succeeded.
No transition engine, executor qualification, reconciliation verification, compensation authority,
stream append/commit, runtime qualification, or downstream authority is claimed.

SLICE 9 SCOPE
Local EvidenceRecord JSON shape/list/Sequence/GCP validation only.
The frozen semantic invariants—no evidence-class upgrade by rewrapping, temporal producer
revocation, and mandatory/contradictory evidence blocking promotion—remain explicitly unproven.
No evidence promotion or authority is claimed.

SLICE 10 SCOPE
Local ReviewAttestation JSON shape/nested-dimension/result-enum/GCP validation only.
Reviewer independence, signature validity, review-gate closure and promotion remain explicitly
unproven. PASS dimension strings do not self-grant a gate.

REVIEW POSTURE
Assume false-green until proven otherwise. Inspect exact bytes, frozen schema/source, preserved
RED runs, final green runs, compare summaries, and non-authority metadata. Do not accept PASS
labels by themselves. Look for:
- wrong JSON/Python type acceptance;
- missing/extra-field bypass;
- bool/int confusion;
- Unicode/GCP escape paths;
- custom equality/type confusion around enum/state strings;
- nullability/conditional mistakes;
- cross-object mismatch bypass;
- false interpretation of state/result labels as authority;
- evidence/review promotion self-grant;
- mutation/state poisoning;
- hidden dependency changes;
- workflow false-green paths;
- exception-to-success behavior.

Do not demand runtime/external evidence for properties the bounded candidates explicitly do not claim.

RETURN ONLY THESE SECTIONS:

A. OVERALL_BATCH_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE.
Overall BOUNDED_PASS requires all three exact candidates to be independently acceptable for their
bounded construction scopes.

B. EXACT_IDENTITIES
Repeat common base, frozen schema, all three candidates, evidence heads, final run/jobs, and packet hashes.

C. SLICE_8_REVIEW
Give one Slice 8 disposition: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE.
Then Critical / High / Medium-Low findings and I8-01..I8-16 assessment.

D. SLICE_9_REVIEW
Give one Slice 9 disposition and Critical / High / Medium-Low findings and I9-01..I9-16 assessment.

E. SLICE_10_REVIEW
Give one Slice 10 disposition and Critical / High / Medium-Low findings and I10-01..I10-16 assessment.

F. CROSS_LOOP_FINDINGS
Identify only findings caused by the three-loop topology, shared base, evidence transport, or cross-candidate assumptions.
Do not invent authority dependencies between sibling candidates.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what each positive bounded construction proves and what remains unproven.
No result grants runtime qualification, release, deployment, production, policy or terminal authority.

H. FINAL_GATES
State separately whether each exact candidate may close its independent-review gate.
State whether the combined three-loop batch review gate may close.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    for item,filename in zip(LOOPS,["02_SLICE8_EXACT.txt","03_SLICE9_EXACT.txt","04_SLICE10_EXACT.txt"]):
        with (OUT/filename).open("wb") as fp:
            fp.write(f"R8 v15-r1 Slice {item['slice']} exact candidate packet\n".encode())
            commit=gh_json(f"repos/{REPO}/commits/{item['candidate']}")
            fp.write((json.dumps({
                "sha":commit["sha"],
                "commit":commit["commit"],
                "parents":[p["sha"] for p in commit.get("parents",[])],
            },indent=2)+"\n").encode())
            fp.write(b"\n===== COMPARE FROM COMMON CLOSED BASE =====\n")
            fp.write((json.dumps(compare_summary(item["candidate"]),indent=2)+"\n").encode())
            for path in item["paths"]:
                fp.write(section(item["candidate"],path,f"SLICE {item['slice']} EXACT CANDIDATE FILE"))
            for path in item["evidence_paths"]:
                fp.write(section(item["evidence_head"],path,f"SLICE {item['slice']} EVIDENCE"))

    source_paths=[
      "schemas/governance-r8/v15-r1/runtime-contracts.schema.json",
      "governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md",
      "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V3.md",
      "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V7.md",
      "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V8.md",
    ]
    with (OUT/"05_FROZEN_CONTRACTS_AND_SOURCES.txt").open("wb") as fp:
        fp.write(b"Exact frozen schema and governing source material for the three-loop batch.\n")
        for path in source_paths:
            fp.write(section(FROZEN,path,"FROZEN CONTRACT / SOURCE"))

    with (OUT/"06_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 three-loop exact construction evidence\n")
        batch_data=pathlib.Path("governance-r8/R8-V15-R1-IMPLEMENTATION-THREE-LOOP-BATCH-REVIEW.json").read_bytes()
        fp.write(b"\n===== BATCH LINEAGE RECORD =====\n")
        fp.write(batch_data)
        if not batch_data.endswith(b"\n"): fp.write(b"\n")
        for item in LOOPS:
            run,job,final_log,red,red_job,red_log=run_bundle(item)
            fp.write(f"\n===== SLICE {item['slice']} FINAL RUN METADATA =====\n".encode())
            fp.write((json.dumps(run,indent=2)+"\n").encode())
            fp.write(f"\n===== SLICE {item['slice']} FINAL JOB METADATA =====\n".encode())
            fp.write((json.dumps(job,indent=2)+"\n").encode())
            fp.write(f"\n===== SLICE {item['slice']} FINAL RAW LOG =====\n".encode())
            fp.write(final_log)
            if not final_log.endswith(b"\n"): fp.write(b"\n")
            fp.write(f"\n===== SLICE {item['slice']} PRESERVED RED RUN METADATA =====\n".encode())
            fp.write((json.dumps(red,indent=2)+"\n").encode())
            fp.write(f"\n===== SLICE {item['slice']} PRESERVED RED JOB METADATA =====\n".encode())
            fp.write((json.dumps(red_job,indent=2)+"\n").encode())
            fp.write(f"\n===== SLICE {item['slice']} PRESERVED RED RAW LOG =====\n".encode())
            fp.write(red_log)
            if not red_log.endswith(b"\n"): fp.write(b"\n")

    files=[OUT/f for f in [
      "01_INSTRUCTIONS.txt","02_SLICE8_EXACT.txt","03_SLICE9_EXACT.txt","04_SLICE10_EXACT.txt",
      "05_FROZEN_CONTRACTS_AND_SOURCES.txt","06_CONSTRUCTION_EVIDENCE.txt",
    ]]
    manifest=[
      "R8 v15-r1 three-loop batch fresh blind review packet SHA-256 manifest",
      f"common_closed_base={BASE}",
      f"frozen_schema={FROZEN}",
      f"slice8_candidate={LOOPS[0]['candidate']}",
      f"slice9_candidate={LOOPS[1]['candidate']}",
      f"slice10_candidate={LOOPS[2]['candidate']}",
      "",
    ]
    for p in files:
        manifest.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"07_SHA256_MANIFEST.txt").write_text("\n".join(manifest)+"\n",encoding="utf-8")

    for p in sorted(OUT.iterdir()):
        if p.is_file():
            print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__":
    main()
