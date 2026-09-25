#!/usr/bin/env python3
"""IG-1 integration-specific strict acceptance oracle.

No production validator function is called directly here. Reviewed slice tests run
in isolated subprocesses. The oracle enforces exact collection counts, zero
skip/expected-failure/unexpected-success markers, exact imported tree identities,
and inherited Slice1-7 baseline success.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
ALLOW=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
EXPECTED={str(n):(20 if n in (20,21,22) else 16) for n in range(8,47)}
FORBIDDEN_OUTPUT=("skipped=","expected failure","unexpected success"," xfail"," xfailed"," not collected","deselected")
FORBIDDEN_HARNESS_TOKENS=("unittest.mock","mock.patch","monkeypatch","sys.modules","meta_path","path_hooks")

def run(*args,check=True):
    p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"FAIL command={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def index_entry(path):
    out=run("git","ls-files","-s","--",path).stdout.strip()
    if not out: return None
    meta,name=out.splitlines()[0].split("\t",1); mode,blob,stage=meta.split()
    return {"path":name,"mode":mode,"blob":blob,"stage":stage}

def test_files_for_slice(allow,n):
    return sorted(e["path"] for e in allow["per_candidate"][n]["selected_entries"] if e["path"].startswith("governance-runtime/test_") and e["path"].endswith(".py"))

def assert_harness_declarative():
    for path in ("tools/r8_v15_r1_ig1_successor1_materialize.py","governance-runtime/test_r8_v15_r1_ig1_integration_oracle.py"):
        text=(ROOT/path).read_text()
        for tok in FORBIDDEN_HARNESS_TOKENS:
            if tok in text: raise SystemExit(f"FAIL forbidden integration-harness token {tok!r} in {path}")

def assert_import_identities(allow):
    seen=set()
    for n,rec in allow["per_candidate"].items():
        for e in rec["selected_entries"]:
            if e["path"] in seen: raise SystemExit(f"FAIL duplicate imported path {e['path']}")
            seen.add(e["path"])
            got=index_entry(e["path"])
            expected={"path":e["path"],"mode":e["mode"],"blob":e["blob"],"stage":"0"}
            if got!=expected: raise SystemExit(f"FAIL imported identity mismatch {e['path']}: {got} != {expected}")

def run_slice_tests(allow,n):
    files=test_files_for_slice(allow,n)
    if not files: raise SystemExit(f"FAIL no imported tests for slice {n}")
    mods=[pathlib.Path(f).stem for f in files]
    p=run(sys.executable,"-m","unittest","-v",*mods,check=False)
    output=(p.stdout+"\n"+p.stderr).lower()
    if p.returncode!=0: raise SystemExit(f"FAIL slice {n} tests\n{p.stdout}\n{p.stderr}")
    matches=re.findall(r"ran\s+(\d+)\s+tests?",output)
    if not matches: raise SystemExit(f"FAIL slice {n} no exact collection count")
    ran=int(matches[-1])
    if ran!=EXPECTED[n]: raise SystemExit(f"FAIL slice {n} collected {ran}, expected {EXPECTED[n]}")
    for marker in FORBIDDEN_OUTPUT:
        if marker in output: raise SystemExit(f"FAIL slice {n} forbidden bypass marker {marker!r}")
    return ran

def run_baseline():
    groups=[
      ["governance-runtime/test_r8_v15_r1_implementation_slice7.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice6.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice5.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice4.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice3.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice2.py"],
      ["governance-runtime/test_r8_v15_r1_implementation_slice1.py","governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py","governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py","governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py","governance-runtime/test_r8_v15_r1_post_freeze_regression.py"],
    ]
    total=0
    for files in groups:
        mods=[pathlib.Path(f).stem for f in files]
        p=run(sys.executable,"-m","unittest","-v",*mods,check=False)
        out=(p.stdout+"\n"+p.stderr).lower()
        if p.returncode!=0: raise SystemExit(f"FAIL inherited baseline\n{p.stdout}\n{p.stderr}")
        ms=re.findall(r"ran\s+(\d+)\s+tests?",out)
        if not ms: raise SystemExit("FAIL inherited baseline missing count")
        for marker in FORBIDDEN_OUTPUT:
            if marker in out: raise SystemExit(f"FAIL inherited baseline bypass marker {marker!r}")
        total+=int(ms[-1])
    if total!=140: raise SystemExit(f"FAIL inherited baseline total {total}, expected 140")
    return total

def main():
    sys.path.insert(0,str(ROOT/"governance-runtime"))
    allow=json.loads(ALLOW.read_text())
    assert_harness_declarative()
    assert_import_identities(allow)
    slice_total=sum(run_slice_tests(allow,str(n)) for n in range(8,47))
    expected_total=sum(EXPECTED.values())
    if slice_total!=expected_total: raise SystemExit(f"FAIL imported slice total {slice_total}, expected {expected_total}")
    baseline=run_baseline()
    print(json.dumps({"status":"IG1_INTEGRATION_ORACLE_PASS","slice_tests":slice_total,"inherited_baseline_tests":baseline,"skips":0,"expected_failures":0,"unexpected_successes":0,"authority_effect":"NONE"},sort_keys=True))

if __name__=="__main__": main()
