#!/usr/bin/env python3
"""IG-1 Successor3 strict structured integration oracle."""
from __future__ import annotations
import argparse
import json
import pathlib
import subprocess
import sys

PROPOSAL_ROOT=pathlib.Path(__file__).resolve().parent.parent
ALLOW=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
BASELINE=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR3-INHERITED-BASELINE-TEST-IDENTITY.json"
CHILD=PROPOSAL_ROOT/"tools"/"r8_v15_r1_ig1_successor3_unittest_child.py"
EXPECTED={str(n):(20 if n in (20,21,22) else 16) for n in range(8,47)}
SENTINEL="__IG1_S3_UNITTEST_RESULT__"

def run(root,*args,check=True):
    p=subprocess.run(args,cwd=root,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"FAIL cwd={root} command={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def index_entry(target,path):
    out=run(target,"git","ls-files","-s","--",path).stdout.strip()
    if not out:
        return None
    meta,name=out.splitlines()[0].split("\t",1)
    mode,blob,stage=meta.split()
    return {"path":name,"mode":mode,"type":"blob","blob":blob,"stage":stage}

def execute_group(target,files,expected,label):
    p=run(target,sys.executable,str(CHILD),str(target),*files,check=False)
    lines=[line for line in p.stdout.splitlines() if line.startswith(SENTINEL)]
    if len(lines)!=1:
        raise SystemExit(f"FAIL {label}: missing or duplicate structured result\n{p.stdout}\n{p.stderr}")
    data=json.loads(lines[0][len(SENTINEL):])
    if p.returncode!=0:
        raise SystemExit(f"FAIL {label}: child return={p.returncode} data={data}\n{p.stdout}\n{p.stderr}")
    if data["testsRun"]!=expected:
        raise SystemExit(f"FAIL {label}: testsRun={data['testsRun']} expected={expected}")
    for key in ("failures","errors","skipped","expectedFailures","unexpectedSuccesses"):
        if data[key]!=0:
            raise SystemExit(f"FAIL {label}: {key}={data[key]}")
    if data["successful"] is not True:
        raise SystemExit(f"FAIL {label}: successful is not true")
    return data["testsRun"]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target",required=True)
    args=ap.parse_args()
    target=pathlib.Path(args.target).resolve()
    allow=json.loads(ALLOW.read_text())
    baseline=json.loads(BASELINE.read_text())

    seen=set()
    for rec in allow["per_candidate"].values():
        for entry in rec["selected_entries"]:
            if entry["path"] in seen:
                raise SystemExit(f"FAIL duplicate imported path {entry['path']}")
            seen.add(entry["path"])
            got=index_entry(target,entry["path"])
            exp={"path":entry["path"],"mode":entry["mode"],"type":"blob","blob":entry["blob"],"stage":"0"}
            if got!=exp:
                raise SystemExit(f"FAIL imported identity {entry['path']}: {got} != {exp}")

    manifest_paths=[entry["path"] for entry in baseline["test_entries"]]
    flat=[path for group in baseline["groups"] for path in group["files"]]
    if sorted(flat)!=sorted(manifest_paths):
        raise SystemExit("FAIL baseline group files do not exactly match baseline identity manifest")
    if len(flat)!=len(set(flat)):
        raise SystemExit("FAIL baseline group file duplicated across groups")
    if sum(group["expected_tests"] for group in baseline["groups"])!=baseline["expected_total_tests"]:
        raise SystemExit("FAIL baseline group expected-test sum mismatch")

    for entry in baseline["test_entries"]:
        got=index_entry(target,entry["path"])
        exp={"path":entry["path"],"mode":entry["mode"],"type":"blob","blob":entry["blob"],"stage":"0"}
        if got!=exp:
            raise SystemExit(f"FAIL inherited baseline identity {entry['path']}: {got} != {exp}")

    reviewed_total=0
    for n in range(8,47):
        files=sorted(
            e["path"] for e in allow["per_candidate"][str(n)]["selected_entries"]
            if e["path"].startswith("governance-runtime/test_") and e["path"].endswith(".py")
        )
        if not files:
            raise SystemExit(f"FAIL no imported tests for slice {n}")
        reviewed_total+=execute_group(target,files,EXPECTED[str(n)],f"slice{n}")
    if reviewed_total!=636:
        raise SystemExit(f"FAIL reviewed slice total {reviewed_total} != 636")

    baseline_total=0
    for group in baseline["groups"]:
        baseline_total+=execute_group(target,group["files"],group["expected_tests"],group["name"])
    if baseline_total!=baseline["expected_total_tests"] or baseline_total!=140:
        raise SystemExit(f"FAIL inherited baseline total {baseline_total} != 140")

    print(json.dumps({
      "status":"IG1_SUCCESSOR3_ORACLE_PASS",
      "reviewed_slice_tests":reviewed_total,
      "inherited_baseline_tests":baseline_total,
      "skips":0,
      "expectedFailures":0,
      "unexpectedSuccesses":0,
      "authority_effect":"NONE"
    },sort_keys=True))

if __name__=="__main__":
    main()
