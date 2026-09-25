#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
OUT=pathlib.Path("review-compact-s35-40"); OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-SLICES35-40-COMPOSITE-COMPACT-REVIEW.txt"

FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
PRIOR_BATCH="09fd9c34077b7e1a5a5cad48d76278117845e704"
RESTORED="dfdeceb297b0eefe54d3a47edc3ae16a6f624ded"

SLICES={
35:{"name":"SPM-1 Provenance Family","candidate":"fd8f410be0cf6e0a45cd5b67942e462278d360e2","evidence":"1cbac39fa9e5b95bdddd3396b6037e261e1b3534","red_run":36153369345,"red_job":108131887252,"green_run":36153850837,"green_job":108133486395,"final_run":36153974973,"final_job":108133902772,"module":"governance-runtime/r8_v15_r1_spm1_provenance_family_validator.py","schemas":["schemas/governance-r8/v15-r1/schema-provenance-manifest.schema.json"]},
36:{"name":"Case + Guard Registry Family","candidate":"07a62458e36adb02b621ecf0fb6761c6cbb6c376","evidence":"aeb4a77638709c0ebfe88aa5f6a36b2d13cc0a55","red_run":36153379931,"red_job":108131921988,"green_run":36153855902,"green_job":108133502477,"final_run":36153980863,"final_job":108133922180,"module":"governance-runtime/r8_v15_r1_case_guard_registry_family_validator.py","schemas":["schemas/governance-r8/v15-r1/case-registry.schema.json","schemas/governance-r8/v15-r1/guard-registry.schema.json"]},
37:{"name":"Guard-Omission Evidence + Manifest Family","candidate":"3b16bd2ea3c00eb1f1d2acedf1c3375d2f0eeb2e","evidence":"fc3759211c8b00a828239e1234a1cb1bb3e8204d","red_run":36153391284,"red_job":108131960432,"green_run":36153861534,"green_job":108133521184,"final_run":36153984211,"final_job":108133932410,"module":"governance-runtime/r8_v15_r1_guard_omission_family_validator.py","schemas":["schemas/governance-r8/v15-r1/guard-omission-source-evidence.schema.json","schemas/governance-r8/v15-r1/guard-omission-manifest.schema.json"]},
38:{"name":"GCP-RVM-2 Family","candidate":"9d5e9af3a643297b5b4074d8be42904a6fa6098d","evidence":"0758c8c2edebd671e4d5955aeddc9f0816a75cb3","red_run":36153425750,"red_job":108132079288,"green_run":36153865966,"green_job":108133535686,"final_run":36153990845,"final_job":108133954716,"module":"governance-runtime/r8_v15_r1_gcp_rvm2_family_validator.py","schemas":["schemas/governance-r8/v15-r1/gcp-rvm-2.schema.json"]},
39:{"name":"CaseProofContracts Family","candidate":"43d43aa48571c905cb4d43e202f891ab853e8d5a","evidence":"38c83c7f5daa249535780a38b5a3bb4c39e9b800","red_run":36153436593,"red_job":108132116522,"green_run":36153870167,"green_job":108133549007,"final_run":36153995616,"final_job":108133969856,"module":"governance-runtime/r8_v15_r1_case_proof_contracts_family_validator.py","schemas":["schemas/governance-r8/v15-r1/case-proof-contracts.schema.json"]},
40:{"name":"SPG-1 Binding Family","candidate":"46e373bc50aee6d1d05aeba01a8d42037a743128","evidence":"fddfaf7333bd158decf79b9602ec2d485e352b7d","red_run":36153446356,"red_job":108132150475,"green_run":36153876349,"green_job":108133569127,"final_run":36154001041,"final_job":108133991886,"module":"governance-runtime/r8_v15_r1_spg1_binding_family_validator.py","schemas":["schemas/governance-r8/v15-r1/schema-provenance-generator.schema.json"]},
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

    header=f"""R8 v15-r1 — SLICES 35-40 COMPOSITE COMPACT FRESH INDEPENDENT REVIEW

Use only this single file. Do not use prior chat history or model recollection.

COMMON IDENTITY
Frozen schema: {FROZEN}
Closed implementation baseline Slice 7: {BASELINE}
Closed Slices 29-34 governance anchor: {PRIOR_BATCH}
Restored adaptive six-slice cadence anchor: {RESTORED}
Active maximum unreviewed low-risk slices: 6

COMPOSITE-SLICE POLICY
These slices deliberately group related nested definitions sharing one structural risk boundary to
reduce administrative slice count. Each family has separate invariant groups in its acceptance
harness. Grouping grants no dependency authority.

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
REVIEW SCOPE
S35 SPM-1: validate complete manifest family structurally. Explicitly DO NOT infer source_ref
referential integrity, artifact/entry-count correspondence, generator qualification truth,
final-freeze eligibility, source authority, or provenance semantic correctness.

S36 Case+Guard registries: validate both registry schemas structurally. Regex \d semantics are
implemented with ASCII [0-9], not Python Unicode-digit widening. Schema does not declare root-array
uniqueItems, so duplicate case/guard records remain structurally allowed. Do not infer registry
identity closure or cross-registry case references.

S37 Guard-Omission family: validate source-evidence and omission-manifest structures. Declared true
set-equality/membership booleans are accepted as declarations only; source digests, source excerpts,
set equality, membership and reverification are NOT recomputed.

S38 GCP-RVM-2: validate vector manifest/nested structures only. Positive/rejection vectors are not
executed; expected SHA-256 values are syntax-checked but not recomputed. ASCII digit semantics are
used for frozen \d patterns.

S39 CaseProofContracts: validate root, exact FP0..FP6 legend, controls and 156 contract structures.
Schema does not declare contracts/controls uniqueItems, so duplicates remain structurally allowed.
Do not infer G001-G156 closure, cross-registry match, evidence sufficiency, or freeze readiness.

S40 SPG-1: validate generator binding and RuntimeManifest structures only. QUALIFIED declarations
are not treated as attestation/qualification proof; null runtime/attestation digests remain allowed
where the frozen schema permits them. No final-freeze or signing authority is inferred.

EARLY-REVIEW SCREEN
No currentness decision, cryptographic trust verification, digest recomputation, evidence promotion,
external effect, attestation verification, cross-registry authority decision, review authority,
or cross-slice dependency authority is claimed.

CADENCE RULE
A new Critical/High finding or CHANGES_REQUIRED resets future low-risk batching to 3. Otherwise the
restored six-slice cadence remains active. Review evidence itself grants no authority.

Return only:
A. OVERALL_DISPOSITION — BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_BATCH_IDENTITY — common anchors, all six candidates/evidence/run IDs, packet hash supplied by user
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. SIX_COMPOSITE_ACCEPTANCE_ASSESSMENT
  F1 Slice35 I35-01..I35-16
  F2 Slice36 I36-01..I36-16
  F3 Slice37 I37-01..I37-16
  F4 Slice38 I38-01..I38-16
  F5 Slice39 I39-01..I39-16
  F6 Slice40 I40-01..I40-16
G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY — include early-review screen, composite-slice assessment and cadence status
H. FINAL_GATES — YES/NO for each exact candidate and whether six-slice cadence remains active
"""
    with TARGET.open("wb") as fp:
        fp.write(header.encode())
        add_file(fp,RESTORED,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-RESTORATION-001.json","RESTORED CADENCE GOVERNANCE")
        add_file(fp,PRIOR_BATCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH29-34-CLOSURE.json","PRIOR BATCH CLOSURE / COMPOSITE POLICY")

        seen=set()
        for n,s in SLICES.items():
            for path in s["schemas"]:
                if path not in seen:
                    add_file(fp,FROZEN,path,f"FROZEN SCHEMA {path}")
                    seen.add(path)

        for n,s in SLICES.items():
            fp.write(f"\n################ SLICE {n} — {s['name']} ################\n".encode())
            for path,label in [
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-PREREGISTRATION.md","PREREGISTRATION"),
              (s["module"],"VALIDATOR"),
              (f"governance-runtime/test_r8_v15_r1_implementation_slice{n}.py","FROZEN COMPOSITE ACCEPTANCE TESTS"),
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
