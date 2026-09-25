#!/usr/bin/env python3
import hashlib, json, os, pathlib, subprocess

REPO=os.environ["GITHUB_REPOSITORY"]
FROZEN="f93ca26975ecb64f0da13779889c75b36140cdfc"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
PRIOR_BATCH="613ad12b29704f44f036e1a275403f58011ae203"
CADENCE="b29619c9307c2a30562a2253f88d052a00bfea6a"

SLICES={
20:{"name":"StableScopeValue","candidate":"053a5c0e70aee45e0e73653d68de3575a83d455c","evidence_head":"3196d46a7ffe61607bd9e78233f69e60055a125f","final_run":36139870458,"final_job":108086775591,"mechanism_run":36139742203,"mechanism_job":108086361775,"red_run":36139491463,"red_job":108085526771,"module":"governance-runtime/r8_v15_r1_stable_scope_value_validator.py"},
21:{"name":"ScopeComponent","candidate":"d3f184380f6cd15582cb3dd6e987895dd895d930","evidence_head":"b1cc3a0b55784b1c373706ab1b8893e5984c537c","final_run":36139874205,"final_job":108086788145,"mechanism_run":36139745395,"mechanism_job":108086371217,"red_run":36139498497,"red_job":108085550099,"module":"governance-runtime/r8_v15_r1_scope_component_validator.py"},
22:{"name":"CanonicalScopeTuple","candidate":"8ecdd17ce80549f87dd15bbe1fc29414272b6253","evidence_head":"99af02c606cdb13b7ae7cb4742d1d3cee010319f","final_run":36139879061,"final_job":108086803813,"mechanism_run":36139748833,"mechanism_job":108086383008,"red_run":36139507939,"red_job":108085579848,"module":"governance-runtime/r8_v15_r1_canonical_scope_tuple_validator.py"},
23:{"name":"ScopeComponentName","candidate":"e80783edea482605eb15ddaded6c8ef8aa79303c","evidence_head":"181504d971690852b0143114db8149ae7b3cd86c","final_run":36139882729,"final_job":108086816395,"mechanism_run":36139753047,"mechanism_job":108086397696,"red_run":36139515373,"red_job":108085604888,"module":"governance-runtime/r8_v15_r1_scope_component_name_validator.py"},
24:{"name":"ANYScopePermission","candidate":"49ad02ca8ccc4f9d6f1b5c78c7ba392184eb2ab4","evidence_head":"75059bfc8272c82ba181769cf7d19da9f13db58f","final_run":36139886780,"final_job":108086829929,"mechanism_run":36139758824,"mechanism_job":108086417748,"red_run":36139523993,"red_job":108085634018,"module":"governance-runtime/r8_v15_r1_any_scope_permission_validator.py"},
25:{"name":"AIMScopePolicyClassRule","candidate":"aa61ee5637daa10f1de9f39d164c610145fe47be","evidence_head":"f81346f279a5137dd39f07a0537bbeeecf0a20b6","final_run":36139890031,"final_job":108086840659,"mechanism_run":36139760592,"mechanism_job":108086423863,"red_run":36139530746,"red_job":108085656867,"module":"governance-runtime/r8_v15_r1_aim_scope_policy_class_rule_validator.py"},
}
OUT=pathlib.Path("review-packet-slices20-25"); OUT.mkdir(exist_ok=True)

def sh(args): return subprocess.check_output(args)
def sha(b): return hashlib.sha256(b).hexdigest()
def show(ref,path): return sh(["git","show",f"{ref}:{path}"])
def blob(ref,path): return sh(["git","rev-parse",f"{ref}:{path}"]).decode().strip()
def gh(endpoint): return json.loads(sh(["gh","api",endpoint]))

def section(ref,path,title):
    b=show(ref,path)
    out=(f"\n===== BEGIN {title}: {ref}:{path} =====\n"
         f"git_blob_sha1={blob(ref,path)}\nsha256={sha(b)}\nbyte_count={len(b)}\n").encode()
    return out+b+(b"" if b.endswith(b"\n") else b"\n")+f"===== END {title}: {ref}:{path} =====\n".encode()

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

def candidate_paths(n,s):
    return [
      f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-PREREGISTRATION.md",
      f".github/workflows/r8-v15-r1-implementation-slice{n}.yml",
      s["module"],
      f"governance-runtime/test_r8_v15_r1_implementation_slice{n}.py",
      f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-MARKER.json",
      f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-FAILURE-001.json",
    ]

def evidence_paths(n):
    return [
      f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-GREEN.json",
      f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-FREEZE.json",
      f"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE{n}-CONSTRUCTION-FAILURE-001.json",
    ]

def main():
    refs=[FROZEN,BASELINE,PRIOR_BATCH,CADENCE]
    for s in SLICES.values(): refs += [s["candidate"],s["evidence_head"]]
    for ref in refs:
        assert sh(["git","rev-parse",f"{ref}^{{commit}}"]).decode().strip()==ref

    for n,s in SLICES.items():
        final=gh(f"repos/{REPO}/actions/runs/{s['final_run']}")
        assert final["status"]=="completed" and final["conclusion"]=="success" and final["head_sha"]==s["candidate"]
        mech=gh(f"repos/{REPO}/actions/runs/{s['mechanism_run']}")
        assert mech["status"]=="completed" and mech["conclusion"]=="success"
        red=gh(f"repos/{REPO}/actions/runs/{s['red_run']}")
        assert red["status"]=="completed" and red["conclusion"]=="failure"

    identities="\n".join(
      f"Slice {n} — {s['name']}\n"
      f"candidate: {s['candidate']}\n"
      f"evidence head: {s['evidence_head']}\n"
      f"final run/job: {s['final_run']} / {s['final_job']}\n"
      f"mechanism GREEN run/job: {s['mechanism_run']} / {s['mechanism_job']}\n"
      f"preserved RED run/job: {s['red_run']} / {s['red_job']}\n"
      for n,s in SLICES.items()
    )
    instructions=f"""R8 v15-r1 IMPLEMENTATION SLICES 20–25 — FRESH BLIND SIX-SLICE BATCH REVIEW

Use only the seven supplied files. Do not use prior conversation history, prior reviewer
outcomes/adjudications, or model recollection.

Common frozen schema: {FROZEN}
Common closed implementation baseline (Slice 7): {BASELINE}
Prior governance-only Slices 17–19 closure anchor: {PRIOR_BATCH}
Active adaptive review-cadence anchor: {CADENCE}
Active cadence: at most 6 low-risk bounded construction slices before fresh independent review,
with mandatory early-review triggers and automatic fallback rules bound in the activation artifact.

{identities}

FILES
1. 01_INSTRUCTIONS.txt
2. 02_EXACT_SLICES20_21_CANDIDATES.txt
3. 03_EXACT_SLICES22_23_CANDIDATES.txt
4. 04_EXACT_SLICES24_25_CANDIDATES.txt
5. 05_SHARED_FROZEN_CONTRACTS_AND_CADENCE.txt
6. 06_BATCH_CONSTRUCTION_EVIDENCE.txt
7. 07_SHA256_MANIFEST.txt

MANIFEST DESIGN
07_SHA256_MANIFEST.txt intentionally hashes payload files 01–06 only. The outer GitHub Actions
artifact digest independently binds the ZIP including the manifest.

REVIEW SCOPE
Review all six slices independently from the common closed baseline. No unreviewed slice may grant
dependency authority to another.

Slice 20 StableScopeValue: string/minLength/exact-ANY exclusion/GCP syntax only.
Slice 21 ScopeComponent: exact ANY sentinel or stable-value syntax only; no ANY permission.
Slice 22 CanonicalScopeTuple: exact nine-field tuple and component syntax only; no scope matching/relation/currentness.
Slice 23 ScopeComponentName: exact nine-value enum only.
Slice 24 ANYScopePermission: exact fields/list uniqueness/enum/Sequence/lifecycle/string syntax only;
  ACTIVE is not current/effective permission, constitutional evidence is unverified, and anti-broadening
  semantics remain unproven.
Slice 25 AIMScopePolicyClassRule: exact two-field structure, semantic_class syntax and unique component-name
  list only; no policy currentness or permission authority.

ADAPTIVE-CADENCE CHECK
Independently assess whether any slice actually crossed a mandatory early-review trigger despite its
preregistration. If yes, identify it as a governance finding. Do not infer authority from object names.

Review posture:
- assume false-green until evidenced otherwise;
- inspect frozen schema, preregistrations, validators, tests, workflows and raw RED/GREEN logs;
- test non-Mapping values, bool/string confusion, GCP edge cases, enum closure, list uniqueness,
  empty-list behavior where schema permits it, state poisoning, exception-to-success paths,
  sibling dependency imports, hidden currentness and hidden authority grants;
- distinguish structure/syntax from current/effective/authorized/qualified semantics.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_BATCH_IDENTITY
Repeat frozen/baseline/prior-batch/cadence anchors, all six candidate/evidence heads,
all final+mechanism+RED run/job IDs, and packet payload hashes.

C. CRITICAL_FINDINGS
Concrete findings only, tagged Slice 20..25 / packet / cadence.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. SIX_LOOP_ACCEPTANCE_ASSESSMENT
F1 Slice 20 — I20-01..I20-16
F2 Slice 21 — I21-01..I21-16
F3 Slice 22 — I22-01..I22-16
F4 Slice 23 — I23-01..I23-16
F5 Slice 24 — I24-01..I24-16
F6 Slice 25 — I25-01..I25-16
Identify any false-green, untested local path, sibling dependency, or early-review-trigger violation.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what each slice proves and does not prove. State whether the adaptive-cadence
early-review screen remained valid. No slice may transfer authority to another batch slice.
Do not grant semantic selection, scope/permission authority, constitutional authority, runtime
qualification, evidence promotion, release, deployment, production, policy or terminal authority.

H. FINAL_GATES
For each exact candidate state YES/NO whether its independent-review gate may close.
Also state whether the six-slice adaptive cadence may remain active or must fall back to 3 under
the activated fallback rule.

This review is evidence only, not self-authority.
"""
    (OUT/"01_INSTRUCTIONS.txt").write_text(instructions,encoding="utf-8")

    pair_files=[
      ("02_EXACT_SLICES20_21_CANDIDATES.txt",(20,21)),
      ("03_EXACT_SLICES22_23_CANDIDATES.txt",(22,23)),
      ("04_EXACT_SLICES24_25_CANDIDATES.txt",(24,25)),
    ]
    for filename,pair in pair_files:
        with (OUT/filename).open("wb") as fp:
            for n in pair:
                s=SLICES[n]
                fp.write(f"\n######## SLICE {n} — {s['name']} ########\n".encode())
                fp.write(sh(["git","show","--no-patch","--format=fuller",s["candidate"]]))
                fp.write(b"\n===== DIFF FROM COMMON CLOSED SLICE 7 BASELINE =====\n")
                fp.write(sh(["git","diff","--name-status",BASELINE,s["candidate"]]))
                for path in candidate_paths(n,s): fp.write(section(s["candidate"],path,f"SLICE {n} CANDIDATE FILE"))
                for path in evidence_paths(n): fp.write(section(s["evidence_head"],path,f"SLICE {n} EVIDENCE"))

    shared=[
      (FROZEN,"schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
      (FROZEN,"governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
      (BASELINE,"governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
      (PRIOR_BATCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-BATCH17-19-CLOSURE.json"),
      (CADENCE,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-AMENDMENT-PROPOSAL-001.json"),
      (CADENCE,"governance-r8/R8-V15-R1-IMPLEMENTATION-REVIEW-CADENCE-ACTIVATION-001.json"),
    ]
    with (OUT/"05_SHARED_FROZEN_CONTRACTS_AND_CADENCE.txt").open("wb") as fp:
        fp.write(b"Shared frozen contracts, closed baseline, prior governance batch and active cadence.\n")
        for ref,path in shared: fp.write(section(ref,path,"SHARED FROZEN / GOVERNANCE SOURCE"))

    with (OUT/"06_BATCH_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slices 20-25 exact six-slice batch construction evidence\n")
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

    payloads=[OUT/f for f in [
      "01_INSTRUCTIONS.txt","02_EXACT_SLICES20_21_CANDIDATES.txt","03_EXACT_SLICES22_23_CANDIDATES.txt",
      "04_EXACT_SLICES24_25_CANDIDATES.txt","05_SHARED_FROZEN_CONTRACTS_AND_CADENCE.txt",
      "06_BATCH_CONSTRUCTION_EVIDENCE.txt"
    ]]
    lines=[
      "R8 v15-r1 Slices 20-25 combined fresh blind six-slice review packet SHA-256 manifest",
      "DESIGN: this manifest intentionally hashes payload files 01-06 only; it does not self-hash.",
      "RATIONALE: outer GitHub Actions artifact digest binds the ZIP including this manifest.",
      ""
    ]
    for p in payloads: lines.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT/"07_SHA256_MANIFEST.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    for p in sorted(OUT.iterdir()): print(p.name,p.stat().st_size,sha(p.read_bytes()))

if __name__=="__main__": main()
