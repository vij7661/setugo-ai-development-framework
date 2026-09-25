#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BATCH_ANCHOR="fa69cd70113c043a285646d0b1bfaef94caa0c69"
SLICES={
  17:{
    "candidate":"2717f6127a4d2a76a7d7efafe5e79fe83cc32c53",
    "evidence_head":"f987da522eac67268f01ddd0e99fcef826f25af7",
    "final_run":36135627354,"final_job":108072886412,
    "mechanism_run":36135576764,"mechanism_job":108072724304,
    "red_run":36135490554,"red_job":108072441996,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice17.yml",
      "governance-runtime/r8_v15_r1_semantic_entry_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice17.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-CONSTRUCTION-FAILURE-001.json"
    ],
    "evidence_paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE17-CONSTRUCTION-FAILURE-001.json"
    ]
  },
  18:{
    "candidate":"9a7d60691fa80b1b5da52dbd5120e899eeefbfe6",
    "evidence_head":"4ce6500cd57db824bfe513decc34391eb48592cb",
    "final_run":36135936005,"final_job":108073888191,
    "mechanism_run":36135882980,"mechanism_job":108073717236,
    "red_run":36135804708,"red_job":108073466799,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice18.yml",
      "governance-runtime/r8_v15_r1_semantic_lineage_mapping_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice18.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-CONSTRUCTION-FAILURE-001.json"
    ],
    "evidence_paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE18-CONSTRUCTION-FAILURE-001.json"
    ]
  },
  19:{
    "candidate":"6d591e8ce8a881411929a887d7152603a4af0e49",
    "evidence_head":"b64c36061eed399cdc28ef7ed0e136f555c7a07a",
    "final_run":36136273176,"final_job":108074991131,
    "mechanism_run":36136220758,"mechanism_job":108074821574,
    "red_run":36136138749,"red_job":108074552132,
    "paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-PREREGISTRATION.md",
      ".github/workflows/r8-v15-r1-implementation-slice19.yml",
      "governance-runtime/r8_v15_r1_aiep_runtime_profile_validator.py",
      "governance-runtime/test_r8_v15_r1_implementation_slice19.py",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-MARKER.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-CONSTRUCTION-FAILURE-001.json"
    ],
    "evidence_paths":[
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-CONSTRUCTION-GREEN.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-FREEZE.json",
      "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE19-CONSTRUCTION-FAILURE-001.json"
    ]
  }
}
OUT=pathlib.Path("review-packet-slices17-19"); OUT.mkdir(exist_ok=True)

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

    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICES 17–19 — FRESH BLIND THREE-LOOP BATCH REVIEW

Use only the seven supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Common frozen schema: {FROZEN}
Common closed implementation baseline (Slice 7): {BASELINE}
Governance-only Slices 14–16 closure anchor: {BATCH_ANCHOR}

Slice 17 — SemanticEntry local structural validator
candidate: {SLICES[17]["candidate"]}
evidence head: {SLICES[17]["evidence_head"]}
final run/job: {SLICES[17]["final_run"]} / {SLICES[17]["final_job"]}
mechanism GREEN run/job: {SLICES[17]["mechanism_run"]} / {SLICES[17]["mechanism_job"]}
preserved RED run/job: {SLICES[17]["red_run"]} / {SLICES[17]["red_job"]}

Slice 18 — SemanticLineageMapping local structural validator
candidate: {SLICES[18]["candidate"]}
evidence head: {SLICES[18]["evidence_head"]}
final run/job: {SLICES[18]["final_run"]} / {SLICES[18]["final_job"]}
mechanism GREEN run/job: {SLICES[18]["mechanism_run"]} / {SLICES[18]["mechanism_job"]}
preserved RED run/job: {SLICES[18]["red_run"]} / {SLICES[18]["red_job"]}

Slice 19 — AIEPRuntimeProfile local structural validator
candidate: {SLICES[19]["candidate"]}
evidence head: {SLICES[19]["evidence_head"]}
final run/job: {SLICES[19]["final_run"]} / {SLICES[19]["final_job"]}
mechanism GREEN run/job: {SLICES[19]["mechanism_run"]} / {SLICES[19]["mechanism_job"]}
preserved RED run/job: {SLICES[19]["red_run"]} / {SLICES[19]["red_job"]}

FILES
1. 01_INSTRUCTIONS.txt
2. 02_EXACT_SLICE17_CANDIDATE.txt
3. 03_EXACT_SLICE18_CANDIDATE.txt
4. 04_EXACT_SLICE19_CANDIDATE.txt
5. 05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt
6. 06_BATCH_CONSTRUCTION_EVIDENCE.txt — raw final GREEN, mechanism GREEN and RED logs.
7. 07_SHA256_MANIFEST.txt

MANIFEST DESIGN
07_SHA256_MANIFEST.txt intentionally hashes payload files 01–06 only. It does not attempt a
self-hash because a file cannot non-circularly contain its own final SHA-256. The outer GitHub
Actions artifact digest is the independent transport-level binding for the ZIP including the
manifest. Do not treat absence of an internal manifest self-hash as evidence that payload hashes
are missing.

REVIEW SCOPE
Review each slice independently from the common closed baseline. No batch slice may transfer
authority or act as dependency authority for another batch slice.

Slice 17 scope:
- exact SemanticEntry field closure;
- exact CanonicalScopeTuple nested shape and scope-component syntax;
- specificity_score/lifecycle/nullable-string/Sequence syntax;
- frozen x-validator invariants (specificity count, semantic_entry_key digest, ANY permission)
  remain false/unverified;
- no semantic selection/currentness/transition/constitutional authority.

Slice 18 scope:
- exact SemanticLineageMapping field closure;
- exact source/destination CanonicalScopeTuple structure;
- lifecycle/Sequence/string syntax;
- no invented source/destination relation;
- no mapping currentness/effectiveness, transition correctness or constitutional authority.

Slice 19 scope:
- exact AIEPRuntimeProfile field closure;
- exact boolean constants and attestation-state enum;
- approved_channel_ids non-empty list with unique GCP-valid strings;
- declared ATTESTED is not verified attestation;
- UNATTESTED_RUNTIME and ATTESTED both grant no positive runtime/evidence/root/terminal authority locally.

Review posture:
- assume false-green until evidenced otherwise;
- inspect schemas/sources, validators, harnesses and raw GREEN/RED logs;
- test non-Mapping inputs, missing/extra fields, GCP edge cases, bool/int confusion,
  scope-tuple shape, nullable handling, list uniqueness, state poisoning, exception-to-success
  paths, semantic-invariant self-grants and hidden authority grants;
- distinguish local structure from current/authorized/qualified semantics.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_BATCH_IDENTITY
Repeat common baseline plus exact candidates/evidence heads/final+mechanism+RED run/job and packet hashes.

C. CRITICAL_FINDINGS
Concrete findings only, tagged Slice 17 / Slice 18 / Slice 19 / packet.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. THREE_LOOP_ACCEPTANCE_ASSESSMENT
F1 Slice 17 — I17-01..I17-16
F2 Slice 18 — I18-01..I18-16
F3 Slice 19 — I19-01..I19-16
Identify any false-green or untested local path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what each slice proves and does not prove. No slice may transfer authority to
another batch slice. Do not grant semantic selection/transition authority, constitutional authority,
runtime qualification, evidence promotion, release, deployment, production, policy or terminal authority.

H. FINAL_GATES
For each exact candidate state YES/NO whether its independent-review gate may close.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    for idx,n in enumerate((17,18,19),start=2):
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
      (FROZEN,"governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V14.md"),
      (BASELINE,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (BATCH_ANCHOR,"governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH14-16-CLOSURE.json"),
    ]
    with (OUT/"05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt").open("wb") as fp:
        fp.write(b"Shared exact frozen contracts, source basis, canonicalizer and governance-only batch anchor.\n")
        for ref,path in shared: fp.write(section(ref,path,"SHARED FROZEN SOURCE / BASELINE"))

    with (OUT/"06_BATCH_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slices 17-19 exact batch construction evidence\n")
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
      "01_INSTRUCTIONS.txt","02_EXACT_SLICE17_CANDIDATE.txt","03_EXACT_SLICE18_CANDIDATE.txt",
      "04_EXACT_SLICE19_CANDIDATE.txt","05_SHARED_FROZEN_CONTRACTS_AND_BASELINE.txt",
      "06_BATCH_CONSTRUCTION_EVIDENCE.txt"
    ]]
    lines=[
      "R8 v15-r1 Slices 17-19 combined fresh blind review packet SHA-256 manifest",
      "DESIGN: this manifest intentionally hashes payload files 01-06 only; it does not self-hash.",
      "RATIONALE: an internal self-hash would be circular; the outer GitHub artifact digest binds the ZIP including this manifest.",
      ""
    ]
    for p in files: lines.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"07_SHA256_MANIFEST.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    for p in sorted(OUT.iterdir()):
        print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__": main()
