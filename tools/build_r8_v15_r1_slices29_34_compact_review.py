#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
OUT=pathlib.Path("review-compact-s29-34"); OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-SLICES29-34-COMPACT-REVIEW.txt"

FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
RESTORED="dfdeceb297b0eefe54d3a47edc3ae16a6f624ded"

SLICES={
29:{"name":"ReviewPresentation FieldRule","candidate":"4c720a215e8d3e99ea236f7a951263a168929813","evidence":"c2f427a23322d53e61fbc2cd82077de8a3e86680","red_run":36148029129,"red_job":108113971414,"green_run":36148331521,"green_job":108114979066,"final_run":36148443444,"final_job":108115352285,"module":"governance-runtime/r8_v15_r1_review_field_rule_validator.py","schema":"schemas/governance-r8/v15-r1/review-presentation-schema.schema.json"},
30:{"name":"ReviewPresentation PacketType","candidate":"113a67da6b11936a48a919410e88469ece20f84b","evidence":"998d4612e8a7645d5dcb993f61a7fc4e03233cfd","red_run":36148036852,"red_job":108113998106,"green_run":36148335758,"green_job":108114992587,"final_run":36148447510,"final_job":108115364879,"module":"governance-runtime/r8_v15_r1_review_packet_type_validator.py","schema":"schemas/governance-r8/v15-r1/review-presentation-schema.schema.json"},
31:{"name":"ReviewPresentationSchema root","candidate":"66595ac25a600daa9c71e63f473d815859945136","evidence":"fae847c4ad4eca7660d021f9f520581166fbcdb9","red_run":36148045750,"red_job":108114030011,"green_run":36148340441,"green_job":108115008183,"final_run":36148452369,"final_job":108115379688,"module":"governance-runtime/r8_v15_r1_review_presentation_schema_validator.py","schema":"schemas/governance-r8/v15-r1/review-presentation-schema.schema.json"},
32:{"name":"BSP-5 Grammar Freeze","candidate":"5fa171b732e58e2eb1a75d755ae25b18f4ac3fff","evidence":"0208d8eda0adeabb29a5cfc94ff208dcf5d34900","red_run":36148054709,"red_job":108114059044,"green_run":36148346428,"green_job":108115026703,"final_run":36148456866,"final_job":108115393425,"module":"governance-runtime/r8_v15_r1_bsp5_grammar_freeze_validator.py","schema":"schemas/governance-r8/v15-r1/bsp-5-grammar.schema.json"},
33:{"name":"NCG Structured Closure","candidate":"bbf310642e6e106fc2de4375da38bbb6d355c6ad","evidence":"8502d081276b9dd70f14a3c5edd27d2936ec6e7f","red_run":36148064454,"red_job":108114091190,"green_run":36148350323,"green_job":108115039355,"final_run":36148462064,"final_job":108115409205,"module":"governance-runtime/r8_v15_r1_ncg_structured_closure_validator.py","schema":"schemas/governance-r8/v15-r1/ncg-structured-closure.schema.json"},
34:{"name":"SPM SourceRef","candidate":"6b313f9d1a0c7a2712e5773e7844aa19355091e3","evidence":"275215faab01fb08418fb32955d0cd9195fc66ea","red_run":36148073235,"red_job":108114121904,"green_run":36148354516,"green_job":108115054612,"final_run":36148466073,"final_job":108115422510,"module":"governance-runtime/r8_v15_r1_spm_source_ref_validator.py","schema":"schemas/governance-r8/v15-r1/schema-provenance-manifest.schema.json"},
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

def schema_excerpt():
    rps=json.loads(show(FROZEN,"schemas/governance-r8/v15-r1/review-presentation-schema.schema.json"))
    bsp=json.loads(show(FROZEN,"schemas/governance-r8/v15-r1/bsp-5-grammar.schema.json"))
    ncg=json.loads(show(FROZEN,"schemas/governance-r8/v15-r1/ncg-structured-closure.schema.json"))
    spm=json.loads(show(FROZEN,"schemas/governance-r8/v15-r1/schema-provenance-manifest.schema.json"))
    out={
      "ReviewPresentationSchema":{"root":{k:v for k,v in rps.items() if k!="$defs"},"defs":rps["$defs"]},
      "BSP5Grammar":bsp,
      "NCGStructuredClosure":ncg,
      "SPM_SourceRef":spm["$defs"]["SourceRef"]
    }
    return json.dumps(out,indent=2,ensure_ascii=False).encode()

def main():
    refs=[FROZEN,BASELINE,RESTORED]
    for s in SLICES.values(): refs += [s["candidate"],s["evidence"]]
    for ref in refs:
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref
    for n,s in SLICES.items():
        assert gh(f"repos/{REPO}/actions/runs/{s['red_run']}")["conclusion"]=="failure"
        assert gh(f"repos/{REPO}/actions/runs/{s['green_run']}")["conclusion"]=="success"
        fr=gh(f"repos/{REPO}/actions/runs/{s['final_run']}")
        assert fr["conclusion"]=="success" and fr["head_sha"]==s["candidate"]

    header=f"""R8 v15-r1 — SLICES 29-34 COMPACT FRESH INDEPENDENT REVIEW PACKET

Use only this single file. Do not use prior chat history or model recollection.

COMMON IDENTITY
Frozen schema: {FROZEN}
Closed implementation baseline Slice 7: {BASELINE}
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
    header+=f"""
EVIDENCE FORMAT
This compact packet embeds full validators, tests, workflows, preregistration, markers, RED records,
GREEN records and freeze records. For each CI run it supplies exact run/job/head metadata, full raw-log
SHA-256 + byte count, step outcomes, and a focused transcript containing unittest results and failures.

REVIEW SCOPE
Slice 29: FieldRule structure only. No review-materiality/influence decision is made.
Slice 30: PacketType structure only. fields uniqueItems is enforced by full JSON-object equality;
same field_id with a different field object remains structurally allowed because the schema does not
declare field_id uniqueness.
Slice 31: RPS-1 root structure only. packet_types has no uniqueItems constraint, so identical packet
objects remain structurally allowed. No presentation enforcement or reviewer authority is claimed.
Slice 32: exact semantic JSON equality to the frozen BSP-5 const object only. It does not execute the
parser, classification order, residual rule, guard omission rule, or review projection.
Slice 33: NCG structural closure shape/count/declared consts only. It does not recompute graph acyclicity,
topological correctness, endpoint closure, ownership semantics, or authority graph behavior.
Slice 34: SPM SourceRef structure only. commit/blob strings remain opaque; no source existence,
authority, provenance referential integrity, or evidence promotion is inferred.

EARLY-REVIEW SCREEN
No schema mutation, cryptographic trust decision, evidence promotion, reviewer authority decision,
currentness/freshness decision, parser execution, graph semantic execution, external effect, or
cross-slice dependency authority is claimed.

CADENCE RULE
If this review finds a new Critical/High finding or returns CHANGES_REQUIRED, the already-approved
adaptive rule resets future construction to the 3-slice maximum. Otherwise the restored six-slice
cadence remains active. Review evidence itself grants no authority.

Return only:
A. OVERALL_DISPOSITION — BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_BATCH_IDENTITY — common anchors, all six candidates/evidence/run IDs, packet hash supplied by user
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. SIX_LOOP_ACCEPTANCE_ASSESSMENT
  F1 Slice29 I29-01..I29-16
  F2 Slice30 I30-01..I30-16
  F3 Slice31 I31-01..I31-16
  F4 Slice32 I32-01..I32-16
  F5 Slice33 I33-01..I33-16
  F6 Slice34 I34-01..I34-16
G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY — include early-review screen and cadence status
H. FINAL_GATES — YES/NO for each exact candidate and whether six-slice cadence remains active
"""
    with TARGET.open("wb") as fp:
        fp.write(header.encode())
        ex=schema_excerpt()
        fp.write(f"\n===== BEGIN FROZEN SCHEMA EXCERPTS =====\nsha256={sha(ex)}\nbyte_count={len(ex)}\n".encode())
        fp.write(ex); fp.write(b"\n===== END FROZEN SCHEMA EXCERPTS =====\n")
        add_file(fp,RESTORED,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-RESTORATION-001.json","RESTORED CADENCE GOVERNANCE")

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
