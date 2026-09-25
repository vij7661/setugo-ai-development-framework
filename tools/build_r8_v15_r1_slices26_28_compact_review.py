#!/usr/bin/env python3
import hashlib, json, os, pathlib, re, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
OUT=pathlib.Path("review-compact-s26-28"); OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-SLICES26-28-COMPACT-REVIEW.txt"

FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
FALLBACK="0410aae4f783b84542d0d491d3d1bb6003ad4216"
POST="4a401bdf33786b980364784a0c8a19e20acef2df"

SLICES={
26:{"name":"AIMScopePolicy","candidate":"83e0366251e22d9768554e44340e2b81dbf5424a","evidence":"26cd26914a2f48d3c08ac728cdf261fc4c31c60f","red_run":36146228177,"red_job":108107967344,"green_run":36146439277,"green_job":108108666916,"final_run":36146516928,"final_job":108108929336,"module":"governance-runtime/r8_v15_r1_aim_scope_policy_validator.py"},
27:{"name":"ScopeReplacementMapping","candidate":"d5c01df8c03b808ca0382793433e6e910485f09f","evidence":"9820674204c391fbf2ef0eea4cb14166da69a1dc","red_run":36146268040,"red_job":108108092603,"green_run":36146443930,"green_job":108108682963,"final_run":36146537117,"final_job":108108996436,"module":"governance-runtime/r8_v15_r1_scope_replacement_mapping_validator.py"},
28:{"name":"ScopeReplacementOutsideTableInput","candidate":"bc17d15d4f0939945576d364dec6ee761c96d8d5","evidence":"73e43c477b3d4b8cd9428a7b876f7df8cdb4ca91","red_run":36146283886,"red_job":108108143245,"green_run":36146447644,"green_job":108108695527,"final_run":36146553993,"final_job":108109054565,"module":"governance-runtime/r8_v15_r1_scope_replacement_outside_table_input_validator.py"},
}

def sh(args): return subprocess.check_output(args)
def gh(endpoint): return json.loads(sh(["gh","api",endpoint]))
def sha(b): return hashlib.sha256(b).hexdigest()
def show(ref,path): return sh(["git","show",f"{ref}:{path}"])
def blob(ref,path): return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()

def add_file(fp,ref,path,label):
    b=show(ref,path)
    fp.write(f"\n===== BEGIN {label} =====\nref={ref}\npath={path}\ngit_blob_sha1={blob(ref,path)}\nsha256={sha(b)}\nbyte_count={len(b)}\n".encode())
    fp.write(b)
    if not b.endswith(b"\n"): fp.write(b"\n")
    fp.write(f"===== END {label} =====\n".encode())

def focused(log:bytes)->bytes:
    text=log.decode("utf-8","replace")
    keep=[]
    patterns=(
      " test_","test_","Ran "," OK","OK","FAILED","MECHANISM_ABSENT","ModuleNotFoundError",
      "Process completed with exit code","Run Slice","Run inherited Slice","##[error]"
    )
    for line in text.splitlines():
        if any(p in line for p in patterns):
            keep.append(line)
    return ("\n".join(keep)+"\n").encode()

def add_run(fp,label,run_id,job_id,expected_head=None,expected_conclusion=None):
    run=gh(f"repos/{REPO}/actions/runs/{run_id}")
    jobs=gh(f"repos/{REPO}/actions/runs/{run_id}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==job_id][0]
    if expected_head is not None: assert run["head_sha"]==expected_head
    if expected_conclusion is not None: assert run["conclusion"]==expected_conclusion
    log=sh(["gh","run","view",str(run_id),"--repo",REPO,"--log"])
    focus=focused(log)
    meta={
      "run_id":run_id,"job_id":job_id,"head_sha":run["head_sha"],"head_branch":run["head_branch"],
      "status":run["status"],"conclusion":run["conclusion"],"job_name":job["name"],"job_conclusion":job["conclusion"],
      "raw_log_sha256":sha(log),"raw_log_byte_count":len(log),
      "focused_transcript_sha256":sha(focus),"focused_transcript_byte_count":len(focus),
      "steps":[{"name":s["name"],"status":s["status"],"conclusion":s["conclusion"]} for s in job.get("steps",[])]
    }
    fp.write(f"\n===== BEGIN {label} =====\n".encode())
    fp.write(json.dumps(meta,indent=2).encode())
    fp.write(b"\n===== FOCUSED TEST TRANSCRIPT DERIVED FROM RAW LOG =====\n")
    fp.write(focus)
    fp.write(f"===== END {label} =====\n".encode())

def schema_excerpt():
    raw=show(FROZEN,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json")
    doc=json.loads(raw)
    defs=doc["$defs"]
    names=["CanonicalId","Digest","Sequence","StableScopeValue","ScopeComponent","CanonicalScopeTuple","ScopeComponentName","AIMScopePolicyClassRule","AIMScopePolicy","ScopeReplacementMapping","ScopeReplacementOutsideTableInput"]
    return json.dumps({n:defs[n] for n in names},indent=2,ensure_ascii=False).encode()

def main():
    refs=[FROZEN,BASELINE,FALLBACK,POST]
    for s in SLICES.values(): refs += [s["candidate"],s["evidence"]]
    for ref in refs:
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref
    for n,s in SLICES.items():
        assert gh(f"repos/{REPO}/actions/runs/{s['red_run']}")["conclusion"]=="failure"
        g=gh(f"repos/{REPO}/actions/runs/{s['green_run']}"); assert g["conclusion"]=="success"
        f=gh(f"repos/{REPO}/actions/runs/{s['final_run']}"); assert f["conclusion"]=="success" and f["head_sha"]==s["candidate"]

    header=f"""R8 v15-r1 — SLICES 26-28 COMPACT FRESH INDEPENDENT REVIEW PACKET

Use only this single file. Do not use prior chat history or model recollection.

COMMON IDENTITY
Frozen schema: {FROZEN}
Closed implementation baseline Slice 7: {BASELINE}
Active fallback-to-3 governance anchor: {FALLBACK}
Post-remediation clean-review state anchor: {POST}
Clean post-remediation review count before this batch: 1 of 2
Active maximum unreviewed low-risk slices: 3

EXACT CANDIDATES
Slice 26 AIMScopePolicy
 candidate: {SLICES[26]["candidate"]}
 evidence head: {SLICES[26]["evidence"]}
 RED run/job: {SLICES[26]["red_run"]} / {SLICES[26]["red_job"]}
 mechanism GREEN run/job: {SLICES[26]["green_run"]} / {SLICES[26]["green_job"]}
 exact-candidate GREEN run/job: {SLICES[26]["final_run"]} / {SLICES[26]["final_job"]}

Slice 27 ScopeReplacementMapping
 candidate: {SLICES[27]["candidate"]}
 evidence head: {SLICES[27]["evidence"]}
 RED run/job: {SLICES[27]["red_run"]} / {SLICES[27]["red_job"]}
 mechanism GREEN run/job: {SLICES[27]["green_run"]} / {SLICES[27]["green_job"]}
 exact-candidate GREEN run/job: {SLICES[27]["final_run"]} / {SLICES[27]["final_job"]}

Slice 28 ScopeReplacementOutsideTableInput
 candidate: {SLICES[28]["candidate"]}
 evidence head: {SLICES[28]["evidence"]}
 RED run/job: {SLICES[28]["red_run"]} / {SLICES[28]["red_job"]}
 mechanism GREEN run/job: {SLICES[28]["green_run"]} / {SLICES[28]["green_job"]}
 exact-candidate GREEN run/job: {SLICES[28]["final_run"]} / {SLICES[28]["final_job"]}

EVIDENCE FORMAT
For size safety this compact packet does not repeat GitHub Actions checkout boilerplate.
For every run it supplies exact run/job/head metadata, full raw-log SHA-256 + byte count,
job-step outcomes, and a deterministic focused transcript containing all unittest result/count,
MECHANISM_ABSENT, failure, and process-outcome lines. Code/tests/workflows are embedded in full.

REVIEW SCOPE
Slice 26: structural AIMScopePolicy only. Nested class-rule syntax and semantic_class uniqueness
are enforced. ACTIVE does not prove current/effective policy. Constitutional evidence and
anti-broadening authority are explicitly unverified.

Slice 27: structural ScopeReplacementMapping only. Both tuples enforce exact ScopeComponent syntax,
including the previously discovered frozen StableScopeValue leading-line-terminator rule.
No object existence, specificity-to-tuple correctness, scope relation, mapping effectiveness,
replacement eligibility, or constitutional amendment authority is inferred.

Slice 28: structural outside-table input only. It validates exact enums/booleans but deliberately
does NOT perform SRTT lookup and does NOT verify NOT_A_REPLACEMENT_BRANCH. If you conclude the
frozen description requires that semantic behavior inside this slice, identify that explicitly
and assess whether the preregistered structural boundary is acceptable or insufficient.

EARLY-REVIEW SCREEN
No slice may grant currentness, semantic selection, scope/replacement authority, constitutional
authority, runtime qualification, evidence promotion, release, deployment, production, policy or
terminal authority. No sibling dependency authority is allowed.

RECOVERY RULE
If and only if this fresh review is BOUNDED_PASS with zero Critical/High findings, it may count as
clean post-remediation review 2 of 2. That satisfies the evidence precondition for possible return
from fallback-3 to the previously approved adaptive 6-slice cadence; the review itself does not
silently change cadence.

Return only:
A. OVERALL_DISPOSITION — BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_BATCH_IDENTITY — anchors, all candidate/evidence/run IDs, packet hash supplied by user
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. THREE_LOOP_ACCEPTANCE_ASSESSMENT
  F1 Slice26 I26-01..I26-16
  F2 Slice27 I27-01..I27-16
  F3 Slice28 I28-01..I28-16
G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY — include early-review screen and cadence recovery status
H. FINAL_GATES — YES/NO for each exact candidate and whether this is clean review 2 of 2

Review evidence does not grant authority.
"""
    with TARGET.open("wb") as fp:
        fp.write(header.encode())
        ex=schema_excerpt()
        fp.write(f"\n===== BEGIN FROZEN SCHEMA EXCERPTS =====\nsha256={sha(ex)}\nbyte_count={len(ex)}\n".encode())
        fp.write(ex); fp.write(b"\n===== END FROZEN SCHEMA EXCERPTS =====\n")
        add_file(fp,FALLBACK,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-FALLBACK-001.json","ACTIVE FALLBACK GOVERNANCE")
        add_file(fp,POST,"governance-r8/R8-V15-R1-POST-REMEDIATION-CLEAN-REVIEW-STATE-001.json","CLEAN REVIEW STATE 1 OF 2")

        for n,s in SLICES.items():
            fp.write(f"\n################ SLICE {n} — {s['name']} ################\n".encode())
            for path,label in [
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-PREREGISTRATION.md","PREREGISTRATION"),
              (s["module"],"VALIDATOR"),
              (f"governance-runtime/test_r8_v15_r1_implementation_slice{n}.py","FROZEN ACCEPTANCE TESTS"),
              (f".github/workflows/r8-v15-r1-implementation-slice{n}.yml","WORKFLOW"),
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-MARKER.json","EXACT CANDIDATE MARKER"),
            ]: add_file(fp,s["candidate"],path,f"SLICE {n} {label}")
            for path,label in [
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-FAILURE-001.json","PRESERVED RED RECORD"),
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-GREEN.json","CONSTRUCTION GREEN RECORD"),
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-FREEZE.json","FREEZE"),
            ]: add_file(fp,s["evidence"],path,f"SLICE {n} {label}")
            add_run(fp,f"SLICE {n} PRESERVED RED",s["red_run"],s["red_job"],expected_conclusion="failure")
            add_run(fp,f"SLICE {n} MECHANISM GREEN",s["green_run"],s["green_job"],expected_conclusion="success")
            add_run(fp,f"SLICE {n} EXACT-CANDIDATE GREEN",s["final_run"],s["final_job"],expected_head=s["candidate"],expected_conclusion="success")

    b=TARGET.read_bytes()
    print(TARGET.name,len(b),sha(b))

if __name__=="__main__": main()
