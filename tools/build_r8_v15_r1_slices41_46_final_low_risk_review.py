#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
OUT=pathlib.Path("review-compact-s41-46"); OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-SLICES41-46-FINAL-LOW-RISK-COMPACT-REVIEW.txt"

FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
PRIOR_BATCH="37dae48c9c537487ff80ca93f92dd13300feff53"
RESTORED="dfdeceb297b0eefe54d3a47edc3ae16a6f624ded"

SLICES={
41:{"name":"Schema Freeze Traceability Exact Freeze","candidate":"cea8e0925e715d5735d33b6522521c3abca8c87b","evidence":"cea0eaa592bd556595ad61fdf8dfa672b9fb1fa5","red_run":36155920057,"red_job":108140301526,"green_run":36156242299,"green_job":108141365449,"final_run":36156407902,"final_job":108141903031,"module":"governance-runtime/r8_v15_r1_freeze_traceability_exact_validator.py"},
42:{"name":"Schema Provenance Source Map Exact Freeze","candidate":"0a4ada53a74dc09f064b4a753fc0629fe64a9a07","evidence":"94d770eda988a1eb75bdab83b85dd4aaca5daafe","red_run":36155930678,"red_job":108140337575,"green_run":36156247477,"green_job":108141381863,"final_run":36156411019,"final_job":108141914694,"module":"governance-runtime/r8_v15_r1_provenance_source_map_exact_validator.py"},
43:{"name":"SRTT-4 RuleRegistry Structural Closure","candidate":"308a06c55de52ec2e59c350aa119733ff7cc6b3b","evidence":"e415b5f6ef46f58096251508c3aed577b6b9933a","red_run":36155940475,"red_job":108140370669,"green_run":36156253941,"green_job":108141405193,"final_run":36156417754,"final_job":108141936377,"module":"governance-runtime/r8_v15_r1_srtt4_rule_registry_validator.py"},
44:{"name":"SRTT-4 TotalTable Structural Domain Closure","candidate":"c1d95441292d2051fbb50b03af8d79093818d0ff","evidence":"57a30889da03eacbe54bb76d35e3801397a6a08b","red_run":36155951795,"red_job":108140410019,"green_run":36156258929,"green_job":108141420344,"final_run":36156421442,"final_job":108141948153,"module":"governance-runtime/r8_v15_r1_srtt4_total_table_validator.py"},
45:{"name":"Schema Freeze Validator Contract Exact Freeze","candidate":"e04913f7973d135f00ecafe6c5b6ea580305e55c","evidence":"bd4cd913809db53a11ca4fbff630504d837b9711","red_run":36155970302,"red_job":108140472886,"green_run":36156293464,"green_job":108141528173,"final_run":36156426183,"final_job":108141961370,"module":"governance-runtime/r8_v15_r1_freeze_validator_contract_exact_validator.py"},
46:{"name":"Frozen Concrete Instance Family Exact Freeze","candidate":"237b2e3216378ad75e8c54b1a44cb1b0b245002f","evidence":"c21680ae1b34e2498f5d25d4817fc017d6997309","red_run":36155984779,"red_job":108140520783,"green_run":36156298442,"green_job":108141544182,"final_run":36156435286,"final_job":108141994029,"module":"governance-runtime/r8_v15_r1_frozen_instance_family_exact_validator.py"},
}
FULL_FROZEN_FILES=[
"schemas/governance-r8/v15-r1/schema-freeze-traceability.json",
"schemas/governance-r8/v15-r1/schema-provenance-source-map.json",
"schemas/governance-r8/v15-r1/srtt-4-rule-registry.schema.json",
"schemas/governance-r8/v15-r1/srtt-4-total-table.schema.json",
"schemas/governance-r8/v15-r1/schema-freeze-validator-contract.json",
"schemas/governance-r8/v15-r1/review-presentation-schema.json",
"schemas/governance-r8/v15-r1/gcp-rvm-2.json",
"schemas/governance-r8/v15-r1/case-proof-contracts.json",
"schemas/governance-r8/v15-r1/schema-provenance-generator-binding.json",
]
LARGE_FROZEN="schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json"

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

def add_large_summary(fp):
    b=show(FROZEN,LARGE_FROZEN)
    obj=json.loads(b)
    summary={
      "ref":FROZEN,
      "path":LARGE_FROZEN,
      "git_blob_sha1":blob(FROZEN,LARGE_FROZEN),
      "raw_sha256":sha(b),
      "byte_count":len(b),
      "top_level_keys":list(obj.keys()),
      "top_level_value_summary":{
        k:(len(v) if isinstance(v,(list,dict)) else v if isinstance(v,(str,int,bool)) or v is None else type(v).__name__)
        for k,v in obj.items()
      },
      "transport_note":"Full 2.45 MB artifact intentionally omitted from this compact review packet. Slice46 tests exact semantic JSON equality against the immutable frozen repository artifact; I46-16 independently requires the entire schemas/governance-r8/v15-r1 tree remain unchanged from the closed Slice7 baseline."
    }
    fp.write(b"\n===== BEGIN LARGE FROZEN ARTIFACT IDENTITY SUMMARY =====\n")
    fp.write(json.dumps(summary,indent=2,ensure_ascii=False).encode())
    fp.write(b"\n===== END LARGE FROZEN ARTIFACT IDENTITY SUMMARY =====\n")

def focused(log:bytes)->bytes:
    text=log.decode("utf-8","replace")
    keep=[]
    terms=("test_i","Ran "," OK","OK","FAILED","MECHANISM_ABSENT","ModuleNotFoundError","Process completed with exit code","Run Slice","Run inherited Slice","##[error]")
    for line in text.splitlines():
        if any(t in line for t in terms): keep.append(line)
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
      "status":run["status"],"conclusion":run["conclusion"],"job_conclusion":job["conclusion"],
      "raw_log_sha256":sha(log),"raw_log_byte_count":len(log),
      "focused_transcript_sha256":sha(focus),"focused_transcript_byte_count":len(focus),
      "steps":[{"name":s["name"],"status":s["status"],"conclusion":s["conclusion"]} for s in job.get("steps",[])]
    }
    fp.write(f"\n===== BEGIN {label} =====\n".encode())
    fp.write(json.dumps(meta,indent=2).encode())
    fp.write(b"\n===== FOCUSED TEST TRANSCRIPT =====\n")
    fp.write(focus)
    fp.write(f"===== END {label} =====\n".encode())

def main():
    refs=[FROZEN,BASELINE,PRIOR_BATCH,RESTORED]
    for s in SLICES.values(): refs += [s["candidate"],s["evidence"]]
    for ref in refs:
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref
    for n,s in SLICES.items():
        assert gh(f"repos/{REPO}/actions/runs/{s['red_run']}")["conclusion"]=="failure"
        assert gh(f"repos/{REPO}/actions/runs/{s['green_run']}")["conclusion"]=="success"
        fr=gh(f"repos/{REPO}/actions/runs/{s['final_run']}")
        assert fr["conclusion"]=="success" and fr["head_sha"]==s["candidate"]

    header=f"""R8 v15-r1 — SLICES 41-46 FINAL LOW-RISK STRUCTURAL BATCH — FRESH INDEPENDENT REVIEW

Use only this single file. Do not use prior chat history or model recollection.

COMMON IDENTITY
Frozen schema: {FROZEN}
Closed implementation baseline Slice 7: {BASELINE}
Closed Slices 35-40 governance anchor: {PRIOR_BATCH}
Restored adaptive six-slice cadence anchor: {RESTORED}
Active maximum unreviewed low-risk slices: 6

EXACT CANDIDATES
"""
    for n,s in SLICES.items():
        header+=f"""Slice {n} — {s['name']}
 candidate: {s['candidate']}
 evidence head: {s['evidence']}
 RED run/job: {s['red_run']} / {s['red_job']}
 mechanism GREEN run/job: {s['green_run']} / {s['green_job']}
 exact-candidate GREEN run/job: {s['final_run']} / {s['final_job']}
"""
    header+="""
SCOPE
S41: semantic JSON equality to frozen traceability artifact only. No mapping/source authority or rule execution.
S42: semantic JSON equality to frozen provenance source-map only. No lineage/source authority or referential proof.
S43: SRTT RuleRegistry structure plus deterministic R01..R11 identity and precedence 1..11 closure. Predicates are not executed.
S44: SRTT TotalTable structure plus row-id 1..2304 closure, exact unique Cartesian input-domain coverage and frozen result-distribution counts. Decisive-rule membership against a current registry and SRTT result/rule recomputation are explicitly NOT performed.
S45: semantic JSON equality to the frozen 45-rule validator contract only. None of SFV-01..45 is executed by this slice.
S46: semantic JSON equality for the remaining frozen concrete instance artifacts. This proves equality to immutable repository artifacts only, not their semantic correctness, provenance, qualification, or final-freeze eligibility.

IMPORTANT TRANSPORT BOUNDARY
The 2.45 MB schema-provenance-manifest-candidate.json is not duplicated verbatim in this compact file.
Its exact Git blob SHA-1, raw SHA-256, byte count and top-level structure summary are included. The
validator reads the frozen file and compares type-sensitive canonical JSON equality; I46-16 requires
the whole schema directory remain byte-identical to the closed Slice7 baseline. Treat this as bounded
identity evidence only, not a semantic/provenance attestation.

EARLY-REVIEW SCREEN
No currentness decision, authority-bearing cryptographic trust decision, semantic SRTT rule execution,
evidence promotion, attestation verification, external effect, review authority, or cross-slice
dependency authority is claimed.

PHASE BOUNDARY
This batch is intended to exhaust the remaining low-risk structural/exact-freeze surface. A PASS
does NOT authorize the next semantic/integration phase. Semantic recomputation/integration must be
separately preregistered and is subject to the mandatory early-review policy.

Return only:
A. OVERALL_DISPOSITION — BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_BATCH_IDENTITY — common anchors, all candidate/evidence/run IDs, packet hash supplied by user
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. SIX_LOOP_ACCEPTANCE_ASSESSMENT
  F1 Slice41 I41-01..I41-16
  F2 Slice42 I42-01..I42-16
  F3 Slice43 I43-01..I43-16
  F4 Slice44 I44-01..I44-16
  F5 Slice45 I45-01..I45-16
  F6 Slice46 I46-01..I46-16
G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY — include early-review screen, whether low-risk structural surface is exhausted, and cadence status
H. FINAL_GATES — YES/NO for each exact candidate; state whether next semantic/integration phase requires fresh early review
"""
    with TARGET.open("wb") as fp:
        fp.write(header.encode())
        add_file(fp,RESTORED,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-RESTORATION-001.json","RESTORED CADENCE GOVERNANCE")
        add_file(fp,PRIOR_BATCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH35-40-CLOSURE.json","PRIOR BATCH CLOSURE")
        for path in FULL_FROZEN_FILES:
            add_file(fp,FROZEN,path,f"FROZEN ARTIFACT {path}")
        add_large_summary(fp)

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
