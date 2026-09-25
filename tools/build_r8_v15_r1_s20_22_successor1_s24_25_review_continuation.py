#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess, zipfile

REPO=os.environ["GITHUB_REPOSITORY"]
OUT=pathlib.Path("review-continuation")
OUT.mkdir(exist_ok=True)
TARGET=OUT/"R8-V15-R1-S20-22-SUCCESSOR1-S24-25-REVIEW-CONTINUATION.txt"

FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
PRIOR_BATCH="613ad12b29704f44f036e1a275403f58011ae203"
ADAPTIVE="b29619c9307c2a30562a2253f88d052a00bfea6a"
FALLBACK="0410aae4f783b84542d0d491d3d1bb6003ad4216"
ORIGINAL_ARTIFACT_ID=10866841324
ORIGINAL_ARTIFACT_SHA256="7ee251f3deed7cc97c80fe16ee22e76a2d307362770dcf020da565ce3ed0e934"

REPAIRS={
20:{"name":"StableScopeValue","candidate":"eee3dee24243fe79c86f0d587fcbf42df932fb39","evidence":"b5cdda48ed21d729ee6e38eae2cb248bdb137cb7","rejected":"053a5c0e70aee45e0e73653d68de3575a83d455c","red_run":36143159757,"red_job":108097654409,"green_run":36143339090,"green_job":108098256325,"final_run":36143559782,"final_job":108098990692,"module":"governance-runtime/r8_v15_r1_stable_scope_value_validator.py"},
21:{"name":"ScopeComponent","candidate":"799921c4e31df9b1140a21c3a1f182dceaaa3f6d","evidence":"6035cc0e411c02f57fe1bd2219ab1597c2ebc2aa","rejected":"d3f184380f6cd15582cb3dd6e987895dd895d930","red_run":36143165437,"red_job":108097673751,"green_run":36143373609,"green_job":108098372384,"final_run":36143568257,"final_job":108099019395,"module":"governance-runtime/r8_v15_r1_scope_component_validator.py"},
22:{"name":"CanonicalScopeTuple","candidate":"7adab4471a17612d50eaf3fae48feb50884f5fcd","evidence":"48f3eed1a52681d83fe4ae485b6ce1bb7f5cacfd","rejected":"8ecdd17ce80549f87dd15bbe1fc29414272b6253","red_run":36143170972,"red_job":108097693607,"green_run":36143381547,"green_job":108098396879,"final_run":36143579385,"final_job":108099056786,"module":"governance-runtime/r8_v15_r1_canonical_scope_tuple_validator.py"},
}
EVIDENCE_ONLY={
24:{"name":"ANYScopePermission","candidate":"49ad02ca8ccc4f9d6f1b5c78c7ba392184eb2ab4","evidence":"75059bfc8272c82ba181769cf7d19da9f13db58f","red_run":36139523993,"red_job":108085634018,"green_run":36139758824,"green_job":108086417748,"final_run":36139886780,"final_job":108086829929},
25:{"name":"AIMScopePolicyClassRule","candidate":"aa61ee5637daa10f1de9f39d164c610145fe47be","evidence":"f81346f279a5137dd39f07a0537bbeeecf0a20b6","red_run":36139530746,"red_job":108085656867,"green_run":36139760592,"green_job":108086423863,"final_run":36139890031,"final_job":108086840659},
}

def sh(args):
    return subprocess.check_output(args)
def sha(b): return hashlib.sha256(b).hexdigest()
def gh(endpoint): return json.loads(sh(["gh","api",endpoint]))
def show(ref,path): return sh(["git","show",f"{ref}:{path}"])
def blob(ref,path): return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()

def add_file(fp,ref,path,label):
    b=show(ref,path)
    fp.write(f"\n===== BEGIN {label} =====\nref={ref}\npath={path}\ngit_blob_sha1={blob(ref,path)}\nsha256={sha(b)}\nbyte_count={len(b)}\n".encode())
    fp.write(b)
    if not b.endswith(b"\n"): fp.write(b"\n")
    fp.write(f"===== END {label} =====\n".encode())

def add_run(fp,run_id,job_id,label,expected_head=None,expected_conclusion=None):
    run=gh(f"repos/{REPO}/actions/runs/{run_id}")
    jobs=gh(f"repos/{REPO}/actions/runs/{run_id}/jobs")["jobs"]
    job=[j for j in jobs if j["id"]==job_id][0]
    if expected_head is not None:
        assert run["head_sha"]==expected_head,(label,run["head_sha"],expected_head)
    if expected_conclusion is not None:
        assert run["conclusion"]==expected_conclusion,(label,run["conclusion"],expected_conclusion)
    log=sh(["gh","run","view",str(run_id),"--repo",REPO,"--log"])
    fp.write(f"\n===== BEGIN {label} METADATA =====\n".encode())
    fp.write(json.dumps({"run_id":run_id,"job_id":job_id,"head_sha":run["head_sha"],"head_branch":run["head_branch"],"status":run["status"],"conclusion":run["conclusion"],"created_at":run["created_at"],"updated_at":run["updated_at"],"job_name":job["name"],"job_conclusion":job["conclusion"]},indent=2).encode())
    fp.write(b"\n===== RAW LOG (verbatim from gh run view --log) =====\n")
    fp.write(log)
    if not log.endswith(b"\n"): fp.write(b"\n")
    fp.write(f"===== END {label} =====\n".encode())

def main():
    # Verify commit objects required for exact git-show evidence.
    refs=[FROZEN,BASELINE,PRIOR_BATCH,ADAPTIVE,FALLBACK]
    for s in REPAIRS.values(): refs += [s["candidate"],s["evidence"],s["rejected"]]
    for s in EVIDENCE_ONLY.values(): refs += [s["candidate"],s["evidence"]]
    for ref in refs:
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref

    # Pull exact canonical manifest bytes from the original GitHub artifact.
    art=gh(f"repos/{REPO}/actions/artifacts/{ORIGINAL_ARTIFACT_ID}")
    assert art["digest"]=="sha256:"+ORIGINAL_ARTIFACT_SHA256
    sh(["bash","-lc",f"gh api repos/{REPO}/actions/artifacts/{ORIGINAL_ARTIFACT_ID}/zip > /tmp/original_packet.zip"])
    zbytes=pathlib.Path("/tmp/original_packet.zip").read_bytes()
    assert sha(zbytes)==ORIGINAL_ARTIFACT_SHA256
    with zipfile.ZipFile("/tmp/original_packet.zip") as z:
        names=set(z.namelist())
        assert "07_SHA256_MANIFEST.txt" in names
        manifest=z.read("07_SHA256_MANIFEST.txt")
        assert sha(manifest)=="c3171cec562057c803d9bf28eac359753777c45bed7440b260940ec2caeab056"

    header=f"""R8 v15-r1 — SINGLE-FILE INDEPENDENT REVIEW CONTINUATION
Purpose: fresh review of repaired Slices 20-22 + evidence completion for Slices 24-25.

This file is self-contained for the requested continuation. Do not rely on the defective
post-review single-file transport bundle. The original GitHub ZIP artifact remains canonical.

COMMON IDENTITIES
Frozen schema: {FROZEN}
Closed implementation baseline Slice 7: {BASELINE}
Prior closed Slices 17-19 governance anchor: {PRIOR_BATCH}
Former adaptive 6-slice cadence anchor: {ADAPTIVE}
Active automatic fallback-to-3 anchor: {FALLBACK}

ORIGINAL CANONICAL PACKET
artifact id: {ORIGINAL_ARTIFACT_ID}
artifact SHA-256: {ORIGINAL_ARTIFACT_SHA256}
canonical 07 manifest SHA-256: c3171cec562057c803d9bf28eac359753777c45bed7440b260940ec2caeab056

PRIOR REVIEW
Overall disposition: CHANGES_REQUIRED.
Critical: none.
High: Slices 20-22 failed to enforce frozen StableScopeValue pattern ^(?!ANY$).+
for values beginning with ECMA line terminators LF, CR, U+2028, U+2029.
Cadence consequence: automatic fallback to maximum 3 unreviewed low-risk slices is ACTIVE.

Slice 23: prior reviewer gate YES; it has been independently closed at
1823aa6dd136c0a8acfc0c5303b109b8e4c1cab0 and is not under re-review here.

REPAIRED SUCCESSORS
Slice 20 successor-1:
  rejected predecessor: {REPAIRS[20]["rejected"]}
  new exact candidate: {REPAIRS[20]["candidate"]}
  evidence head: {REPAIRS[20]["evidence"]}
  repair RED run/job: {REPAIRS[20]["red_run"]} / {REPAIRS[20]["red_job"]}
  repair mechanism GREEN run/job: {REPAIRS[20]["green_run"]} / {REPAIRS[20]["green_job"]}
  exact-candidate GREEN run/job: {REPAIRS[20]["final_run"]} / {REPAIRS[20]["final_job"]}
  final acceptance: 16 original + 4 successor + 140 inherited = 160/160 PASS

Slice 21 successor-1:
  rejected predecessor: {REPAIRS[21]["rejected"]}
  new exact candidate: {REPAIRS[21]["candidate"]}
  evidence head: {REPAIRS[21]["evidence"]}
  repair RED run/job: {REPAIRS[21]["red_run"]} / {REPAIRS[21]["red_job"]}
  repair mechanism GREEN run/job: {REPAIRS[21]["green_run"]} / {REPAIRS[21]["green_job"]}
  exact-candidate GREEN run/job: {REPAIRS[21]["final_run"]} / {REPAIRS[21]["final_job"]}
  final acceptance: 16 original + 4 successor + 140 inherited = 160/160 PASS

Slice 22 successor-1:
  rejected predecessor: {REPAIRS[22]["rejected"]}
  new exact candidate: {REPAIRS[22]["candidate"]}
  evidence head: {REPAIRS[22]["evidence"]}
  repair RED run/job: {REPAIRS[22]["red_run"]} / {REPAIRS[22]["red_job"]}
  repair mechanism GREEN run/job: {REPAIRS[22]["green_run"]} / {REPAIRS[22]["green_job"]}
  exact-candidate GREEN run/job: {REPAIRS[22]["final_run"]} / {REPAIRS[22]["final_job"]}
  final acceptance: 16 original + 4 successor + 140 inherited = 160/160 PASS

EVIDENCE-ONLY CONTINUATION
Slice 24 remains exact candidate {EVIDENCE_ONLY[24]["candidate"]}.
No code changed. This file supplies its complete RED, mechanism GREEN, and exact-candidate GREEN logs.
Slice 25 remains exact candidate {EVIDENCE_ONLY[25]["candidate"]}.
No code changed. This file supplies its complete RED, mechanism GREEN, and exact-candidate GREEN logs.

REVIEW TASK
Use only evidence in this continuation plus the original prior review reproduced below.
For Slices 20-22 determine whether the High pattern false-green is narrowly and completely repaired.
Check exact ECMA semantics: leading LF/CR/U+2028/U+2029 reject on StableScopeValue-derived stable
branches, while later/trailing line terminators remain allowed because the frozen pattern is not
end-anchored; exact ANY semantics must remain correct.
For Slices 24-25 determine whether the prior INSUFFICIENT_EVIDENCE condition is cured by the now
complete raw logs. Do not reinterpret unchanged static code beyond evidence needed for those gates.

Return only:
A. OVERALL_DISPOSITION — BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_IDENTITY — all common anchors, S20-22 successor candidates/evidence/run IDs, S24-25 identities,
   original artifact id/hash, canonical 07 manifest hash, and this continuation file hash.
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. TARGETED_ACCEPTANCE_ASSESSMENT
   F1 Slice20 successor-1 repair
   F2 Slice21 successor-1 repair
   F3 Slice22 successor-1 repair
   F4 Slice24 evidence completion
   F5 Slice25 evidence completion
G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
   State whether fallback-to-3 remains active. One clean review is NOT enough to recover to 6;
   recovery requires two consecutive fresh BOUNDED_PASS reviews with zero Critical/High after remediation.
H. FINAL_GATES
   YES/NO for S20 successor-1, S21 successor-1, S22 successor-1, S24 original candidate, S25 original candidate.
   State whether this counts as the first clean review toward possible future recovery from 3 to 6.

No review result grants runtime qualification, evidence promotion, release, deployment, production,
policy, constitutional, root, or terminal authority.
"""

    with TARGET.open("wb") as fp:
        fp.write(header.encode())

        add_file(fp,FROZEN,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json","FROZEN RUNTIME CONTRACTS")
        add_file(fp,FALLBACK,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-FALLBACK-001.json","ACTIVE FALLBACK GOVERNANCE")

        # Embed exact canonical original 07 bytes.
        fp.write(b"\n===== BEGIN ORIGINAL CANONICAL 07_SHA256_MANIFEST.txt =====\n")
        fp.write(f"sha256={sha(manifest)}\nbyte_count={len(manifest)}\n".encode())
        fp.write(manifest)
        if not manifest.endswith(b"\n"): fp.write(b"\n")
        fp.write(b"===== END ORIGINAL CANONICAL 07_SHA256_MANIFEST.txt =====\n")

        # Prior exact review as preserved on repaired branch.
        add_file(fp,REPAIRS[22]["evidence"],"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICES20-25-INDEPENDENT-REVIEW-001.txt","PRIOR INDEPENDENT REVIEW 001")

        for n,s in REPAIRS.items():
            fp.write(f"\n################ SLICE {n} SUCCESSOR-1 ################\n".encode())
            for path,label in [
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-SUCCESSOR1-REPAIR-PREREGISTRATION.md","REPAIR PREREGISTRATION"),
              (s["module"],"REPAIRED VALIDATOR"),
              (f"governance-runtime/test_r8_v15_r1_implementation_slice{n}.py","ORIGINAL FROZEN ACCEPTANCE TESTS"),
              (f"governance-runtime/test_r8_v15_r1_implementation_slice{n}_successor1.py","SUCCESSOR-1 REPAIR TESTS"),
              (f".github/workflows/r8-v15-r1-implementation-slice{n}.yml","CURRENT WORKFLOW"),
              (f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-SUCCESSOR1-MARKER.json","SUCCESSOR-1 MARKER"),
            ]:
                add_file(fp,s["candidate"],path,f"SLICE {n} {label}")
            add_file(fp,s["evidence"],f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-SUCCESSOR1-REPAIR-RED.json",f"SLICE {n} PRESERVED REPAIR RED RECORD")
            add_file(fp,s["evidence"],f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-SUCCESSOR1-CONSTRUCTION-GREEN.json",f"SLICE {n} SUCCESSOR GREEN RECORD")
            add_file(fp,s["evidence"],f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-SUCCESSOR1-FREEZE.json",f"SLICE {n} SUCCESSOR FREEZE")
            add_run(fp,s["red_run"],s["red_job"],f"SLICE {n} REPAIR RED",expected_conclusion="failure")
            add_run(fp,s["green_run"],s["green_job"],f"SLICE {n} REPAIR MECHANISM GREEN",expected_conclusion="success")
            add_run(fp,s["final_run"],s["final_job"],f"SLICE {n} SUCCESSOR EXACT-CANDIDATE GREEN",expected_head=s["candidate"],expected_conclusion="success")

        for n,s in EVIDENCE_ONLY.items():
            fp.write(f"\n################ SLICE {n} EVIDENCE COMPLETION ONLY ################\n".encode())
            add_file(fp,s["candidate"],f"governance-runtime/test_r8_v15_r1_implementation_slice{n}.py",f"SLICE {n} ORIGINAL ACCEPTANCE TESTS")
            add_file(fp,s["candidate"],f".github/workflows/r8-v15-r1-implementation-slice{n}.yml",f"SLICE {n} ORIGINAL WORKFLOW")
            if n==24:
                add_file(fp,s["candidate"],"governance-runtime/r8_v15_r1_any_scope_permission_validator.py","SLICE 24 VALIDATOR")
            else:
                add_file(fp,s["candidate"],"governance-runtime/r8_v15_r1_aim_scope_policy_class_rule_validator.py","SLICE 25 VALIDATOR")
            add_run(fp,s["red_run"],s["red_job"],f"SLICE {n} ORIGINAL PRESERVED RED",expected_conclusion="failure")
            add_run(fp,s["green_run"],s["green_job"],f"SLICE {n} ORIGINAL MECHANISM GREEN",expected_conclusion="success")
            add_run(fp,s["final_run"],s["final_job"],f"SLICE {n} ORIGINAL EXACT-CANDIDATE GREEN",expected_head=s["candidate"],expected_conclusion="success")

    b=TARGET.read_bytes()
    print(TARGET.name,len(b),sha(b))

if __name__=="__main__": main()
