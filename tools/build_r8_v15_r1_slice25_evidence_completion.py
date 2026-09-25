#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
OUT=pathlib.Path("slice25-evidence")
OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-SLICE25-EVIDENCE-COMPLETION.txt"

CANDIDATE="aa61ee5637daa10f1de9f39d164c610145fe47be"
FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
FALLBACK="0410aae4f783b84542d0d491d3d1bb6003ad4216"

RUNS=[
 ("PRESERVED_RED",36139530746,108085656867,"9ba5e12620a6e6fd50e607dbfe7f6ca9be728bdd","failure"),
 ("MECHANISM_GREEN",36139760592,108086423863,"f37ecaf9e0b839ae326fda2de3a7dbeb688f6cf7","success"),
 ("EXACT_CANDIDATE_GREEN",36139890031,108086840659,CANDIDATE,"success"),
]

def sh(args):
    return subprocess.check_output(args)
def gh(endpoint):
    return json.loads(sh(["gh","api",endpoint]))
def sha(b):
    return hashlib.sha256(b).hexdigest()
def show(ref,path):
    return sh(["git","show",f"{ref}:{path}"])
def blob(ref,path):
    return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()

def add_file(fp,ref,path,label):
    b=show(ref,path)
    fp.write(f"\n===== BEGIN {label} =====\nref={ref}\npath={path}\ngit_blob_sha1={blob(ref,path)}\nsha256={sha(b)}\nbyte_count={len(b)}\n".encode())
    fp.write(b)
    if not b.endswith(b"\n"): fp.write(b"\n")
    fp.write(f"===== END {label} =====\n".encode())

def add_run(fp,label,run_id,job_id,expected_head,expected_conclusion):
    run=gh(f"repos/{REPO}/actions/runs/{run_id}")
    jobs=gh(f"repos/{REPO}/actions/runs/{run_id}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==job_id][0]
    assert run["status"]=="completed"
    assert run["conclusion"]==expected_conclusion
    assert run["head_sha"]==expected_head
    assert job["conclusion"]==expected_conclusion
    log=sh(["gh","run","view",str(run_id),"--repo",REPO,"--log"])
    fp.write(f"\n===== BEGIN SLICE25 {label} =====\n".encode())
    meta={
      "run_id":run_id,
      "job_id":job_id,
      "head_sha":run["head_sha"],
      "head_branch":run["head_branch"],
      "status":run["status"],
      "conclusion":run["conclusion"],
      "created_at":run["created_at"],
      "updated_at":run["updated_at"],
      "job_name":job["name"],
      "job_conclusion":job["conclusion"],
      "raw_log_sha256":sha(log),
      "raw_log_byte_count":len(log),
    }
    fp.write(json.dumps(meta,indent=2).encode())
    fp.write(b"\n===== RAW LOG START =====\n")
    fp.write(log)
    if not log.endswith(b"\n"): fp.write(b"\n")
    fp.write(b"===== RAW LOG END =====\n")
    fp.write(f"===== END SLICE25 {label} =====\n".encode())

def main():
    for ref in (CANDIDATE,FROZEN,BASELINE,FALLBACK):
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref

    header=f"""R8 v15-r1 — SLICE 25 EVIDENCE COMPLETION ONLY

Purpose: cure the remaining INSUFFICIENT_EVIDENCE condition from independent review 002.
No Slice 25 code, candidate, test, workflow, or semantics changed.

COMMON IDENTITY
Frozen schema: {FROZEN}
Closed implementation baseline Slice 7: {BASELINE}
Active fallback-to-3 governance anchor: {FALLBACK}

SLICE 25
Exact candidate: {CANDIDATE}
Preserved RED: 36139530746 / 108085656867 / head 9ba5e12620a6e6fd50e607dbfe7f6ca9be728bdd
Mechanism GREEN: 36139760592 / 108086423863 / head f37ecaf9e0b839ae326fda2de3a7dbeb688f6cf7
Exact-candidate GREEN: 36139890031 / 108086840659 / head {CANDIDATE}

Expected execution evidence:
- preserved RED: 16 tests, 15 mechanism-absent failures and I25-16 pass;
- mechanism GREEN: Slice25 16/16 plus inherited baseline 140/140 = 156/156 PASS;
- exact-candidate GREEN: Slice25 16/16 plus inherited baseline 140/140 = 156/156 PASS.

REVIEW TASK
This is evidence completion only. Reassess only the previously open Slice 25 gate.
Confirm:
1. preserved RED is complete and consistent with mechanism absence;
2. mechanism GREEN is complete and successful;
3. exact-candidate GREEN is complete, successful, and bound to {CANDIDATE};
4. unchanged validator/test/workflow identities are present;
5. no authority is granted beyond bounded structural implementation construction.

Return only:
A. OVERALL_DISPOSITION — BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_IDENTITY
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. SLICE25_EVIDENCE_ASSESSMENT
G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
H. FINAL_GATE — YES/NO for exact candidate {CANDIDATE}

Also state whether this evidence-only review, together with review 002's zero Critical/High findings on the repaired/accepted slices, counts as the first clean post-remediation review toward eventual recovery from 3 to 6. Do not count it if your disposition is not BOUNDED_PASS with zero Critical/High.

No result grants runtime qualification, evidence promotion, release, deployment, production, policy, constitutional, root, or terminal authority.
"""
    with TARGET.open("wb") as fp:
        fp.write(header.encode())
        add_file(fp,CANDIDATE,"governance-runtime/r8_v15_r1_aim_scope_policy_class_rule_validator.py","SLICE25 VALIDATOR")
        add_file(fp,CANDIDATE,"governance-runtime/test_r8_v15_r1_implementation_slice25.py","SLICE25 ACCEPTANCE TESTS")
        add_file(fp,CANDIDATE,".github/workflows/r8-v15-r1-implementation-slice25.yml","SLICE25 WORKFLOW")
        add_file(fp,CANDIDATE,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE25-MARKER.json","SLICE25 EXACT CANDIDATE MARKER")
        for label,run_id,job_id,head,conclusion in RUNS:
            add_run(fp,label,run_id,job_id,head,conclusion)
    b=TARGET.read_bytes()
    print(TARGET.name,len(b),sha(b))

if __name__=="__main__": main()
