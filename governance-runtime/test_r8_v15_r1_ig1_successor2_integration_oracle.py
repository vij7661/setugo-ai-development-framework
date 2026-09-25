#!/usr/bin/env python3
"""IG-1 Successor2 strict integration oracle.

Runs byte-reviewed slice tests and exact-base inherited tests in isolated child
processes and consumes structured unittest TestResult JSON rather than prose markers.
"""
from __future__ import annotations
import argparse, json, pathlib, subprocess, sys

PROPOSAL_ROOT=pathlib.Path(__file__).resolve().parent.parent
ALLOW=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
BASELINE=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR2-INHERITED-BASELINE-TEST-IDENTITY.json"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
EXPECTED={str(n):(20 if n in (20,21,22) else 16) for n in range(8,47)}
SENTINEL="__IG1_UNITTEST_RESULT__"
CHILD=r'''
import json, pathlib, sys, unittest
root=pathlib.Path(sys.argv[1]).resolve()
files=sys.argv[2:]
sys.path.insert(0,str(root/"governance-runtime"))
mods=[pathlib.Path(f).stem for f in files]
suite=unittest.defaultTestLoader.loadTestsFromNames(mods)
res=unittest.TextTestRunner(verbosity=2).run(suite)
data={
 "testsRun":res.testsRun,
 "failures":len(res.failures),
 "errors":len(res.errors),
 "skipped":len(getattr(res,"skipped",[])),
 "expectedFailures":len(getattr(res,"expectedFailures",[])),
 "unexpectedSuccesses":len(getattr(res,"unexpectedSuccesses",[])),
 "successful":res.wasSuccessful()
}
print("__IG1_UNITTEST_RESULT__"+json.dumps(data,sort_keys=True))
sys.exit(0 if data["successful"] and not any(data[k] for k in ("failures","errors","skipped","expectedFailures","unexpectedSuccesses")) else 1)
'''

def run(root,*args,check=True):
    p=subprocess.run(args,cwd=root,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"FAIL cwd={root} command={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def index_entry(target,path):
    out=run(target,"git","ls-files","-s","--",path).stdout.strip()
    if not out:return None
    meta,name=out.splitlines()[0].split("\t",1); mode,blob,stage=meta.split()
    return {"path":name,"mode":mode,"type":"blob","blob":blob,"stage":stage}

def execute_group(target,files,expected,label):
    p=run(target,sys.executable,"-c",CHILD,str(target),*files,check=False)
    lines=[x for x in (p.stdout+"\n"+p.stderr).splitlines() if x.startswith(SENTINEL)]
    if len(lines)!=1: raise SystemExit(f"FAIL {label}: missing/duplicate structured result\n{p.stdout}\n{p.stderr}")
    data=json.loads(lines[0][len(SENTINEL):])
    if p.returncode!=0: raise SystemExit(f"FAIL {label}: child return {p.returncode} result={data}\n{p.stdout}\n{p.stderr}")
    if data["testsRun"]!=expected: raise SystemExit(f"FAIL {label}: testsRun {data['testsRun']} != {expected}")
    for k in ("failures","errors","skipped","expectedFailures","unexpectedSuccesses"):
        if data[k]!=0: raise SystemExit(f"FAIL {label}: {k}={data[k]}")
    if data["successful"] is not True: raise SystemExit(f"FAIL {label}: successful false")
    return data["testsRun"]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--target",required=True); args=ap.parse_args()
    target=pathlib.Path(args.target).resolve()
    allow=json.loads(ALLOW.read_text()); baseline=json.loads(BASELINE.read_text())
    # Imported reviewed entries exact identity.
    seen=set()
    for rec in allow["per_candidate"].values():
        for e in rec["selected_entries"]:
            if e["path"] in seen: raise SystemExit(f"FAIL duplicate imported path {e['path']}")
            seen.add(e["path"])
            got=index_entry(target,e["path"])
            exp={"path":e["path"],"mode":e["mode"],"type":"blob","blob":e["blob"],"stage":"0"}
            if got!=exp: raise SystemExit(f"FAIL imported identity {e['path']}: {got} != {exp}")
    # Inherited tests exact identity against Slice7 base.
    for e in baseline["test_entries"]:
        got=index_entry(target,e["path"])
        exp={"path":e["path"],"mode":e["mode"],"type":"blob","blob":e["blob"],"stage":"0"}
        if got!=exp: raise SystemExit(f"FAIL inherited baseline identity {e['path']}: {got} != {exp}")
    # S8-S46 exact reviewed suites.
    total=0
    for n in range(8,47):
        files=sorted(e["path"] for e in allow["per_candidate"][str(n)]["selected_entries"] if e["path"].startswith("governance-runtime/test_") and e["path"].endswith(".py"))
        if not files: raise SystemExit(f"FAIL no imported tests for slice {n}")
        total+=execute_group(target,files,EXPECTED[str(n)],f"slice{n}")
    if total!=636: raise SystemExit(f"FAIL reviewed slice total {total} != 636")
    # S1-S7 baseline in same subprocess partitioning as reviewed construction workflows.
    groups=[
      ["governance-runtime/test_r8_v15_r1_implementation_slice7.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice6.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice5.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice4.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice3.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice2.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice1.py","governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py","governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py","governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py","governance-runtime/test_r8_v15_r1_post_freeze_regression.py"],
    ]
    baseline_total=0
    for i,files in enumerate(groups,1):
        # exact per-group count need not be rediscovered: byte identities are exact;
        # structured result guarantees zero bypasses, and exact aggregate remains 140.
        p=run(target,sys.executable,"-c",CHILD,str(target),*files,check=False)
        lines=[x for x in (p.stdout+"\n"+p.stderr).splitlines() if x.startswith(SENTINEL)]
        if len(lines)!=1: raise SystemExit(f"FAIL baseline group{i} result")
        data=json.loads(lines[0][len(SENTINEL):])
        if p.returncode!=0 or data["successful"] is not True: raise SystemExit(f"FAIL baseline group{i}: {data}")
        for k in ("failures","errors","skipped","expectedFailures","unexpectedSuccesses"):
            if data[k]!=0: raise SystemExit(f"FAIL baseline group{i}: {k}={data[k]}")
        baseline_total+=data["testsRun"]
    if baseline_total!=140: raise SystemExit(f"FAIL inherited baseline total {baseline_total} != 140")
    print(json.dumps({"status":"IG1_SUCCESSOR2_ORACLE_PASS","reviewed_slice_tests":636,"inherited_baseline_tests":140,"skipped":0,"expectedFailures":0,"unexpectedSuccesses":0,"authority_effect":"NONE"},sort_keys=True))

if __name__=="__main__": main()
