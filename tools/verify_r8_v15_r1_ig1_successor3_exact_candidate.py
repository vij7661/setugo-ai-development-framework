#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, sys

ROOT=pathlib.Path(__file__).resolve().parent.parent
CANDIDATE="4984f06a4420b76ad1ad475751aebda04a2d2c5c"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
EXPECTED_TREE="5a34e0d7db3e750dd5b0f722ccecc8014be189ef"
EXPECTED_MANIFEST_BLOB="a78add847f6d4ba8914a66ee00d89422fbaa47f2"
MANIFEST="governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INTEGRATED-CANDIDATE-MANIFEST.json"
ALLOW=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
BASELINE=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR3-INHERITED-BASELINE-TEST-IDENTITY.json"
ORACLE=ROOT/"governance-runtime"/"test_r8_v15_r1_ig1_successor3_integration_oracle.py"
EXACT_SOURCE_BLOBS={
 "governance-r8/R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json":"15cbe7947d0f6f872fabd00b2fc5b0d01a894e2b",
 "governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INHERITED-BASELINE-TEST-IDENTITY.json":"761f1e2a60e0ab21d2b7b1dc392f0562b28fb9bd",
 "governance-runtime/test_r8_v15_r1_ig1_successor3_integration_oracle.py":"6cecb7db86a8268a1bcea988986150a24f7f1b69",
 "tools/r8_v15_r1_ig1_successor3_unittest_child.py":"c3c4c029fcd91afb3ee6c4ae82560c87a4a60075",
}

def run(root,*args,check=True):
    p=subprocess.run(args,cwd=root,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"FAIL cwd={root} args={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def tree_entry(root,rev,path):
    out=run(root,"git","ls-tree",rev,"--",path).stdout.rstrip("\n")
    if not out:return None
    meta,name=out.split("\t",1); mode,typ,blob=meta.split()
    return {"path":name,"mode":mode,"type":typ,"blob":blob}

def main():
    # Verify evidence/oracle bytes used for this verification are the same reviewed bytes.
    for path,blob in EXACT_SOURCE_BLOBS.items():
        got=run(ROOT,"git","rev-parse",f"HEAD:{path}").stdout.strip()
        if got!=blob: raise SystemExit(f"FAIL source evidence/oracle drift {path}: {got} != {blob}")

    run(ROOT,"git","cat-file","-e",CANDIDATE+"^{commit}")
    parent=run(ROOT,"git","rev-parse",CANDIDATE+"^").stdout.strip()
    if parent!=BASE: raise SystemExit(f"FAIL candidate parent {parent} != {BASE}")
    tree=run(ROOT,"git","rev-parse",CANDIDATE+"^{tree}").stdout.strip()
    if tree!=EXPECTED_TREE: raise SystemExit(f"FAIL candidate tree {tree} != {EXPECTED_TREE}")
    changed=set(filter(None,run(ROOT,"git","diff","--name-only",BASE,CANDIDATE).stdout.splitlines()))
    allow=json.loads(ALLOW.read_text())
    expected={e["path"] for rec in allow["per_candidate"].values() for e in rec["selected_entries"]}
    expected.add(MANIFEST)
    if changed!=expected or len(changed)!=121:
        raise SystemExit(f"FAIL exact candidate changed set missing={sorted(expected-changed)} extra={sorted(changed-expected)} count={len(changed)}")
    for rec in allow["per_candidate"].values():
        for e in rec["selected_entries"]:
            got=tree_entry(ROOT,CANDIDATE,e["path"])
            exp={k:e[k] for k in ("path","mode","type","blob")}
            if got!=exp: raise SystemExit(f"FAIL candidate imported identity {e['path']}: {got} != {exp}")
    m=tree_entry(ROOT,CANDIDATE,MANIFEST)
    if not m or m["mode"]!="100644" or m["type"]!="blob" or m["blob"]!=EXPECTED_MANIFEST_BLOB:
        raise SystemExit(f"FAIL candidate manifest identity {m}")
    baseline=json.loads(BASELINE.read_text())
    for e in baseline["test_entries"]:
        got=tree_entry(ROOT,CANDIDATE,e["path"])
        exp={k:e[k] for k in ("path","mode","type","blob")}
        if got!=exp: raise SystemExit(f"FAIL baseline identity in candidate {e['path']}: {got} != {exp}")

    target=pathlib.Path(sys.argv[1]).resolve()
    run(ROOT,"git","worktree","add","--detach",str(target),CANDIDATE)
    try:
        status_before=run(target,"git","status","--porcelain=v1").stdout.strip()
        if status_before: raise SystemExit(f"FAIL candidate worktree dirty before oracle: {status_before}")
        p=run(ROOT,sys.executable,str(ORACLE),"--target",str(target),check=False)
        sys.stdout.write(p.stdout); sys.stderr.write(p.stderr)
        if p.returncode: raise SystemExit(f"FAIL exact-candidate strict oracle return={p.returncode}")
        status_after=run(target,"git","status","--porcelain=v1").stdout.strip()
        if status_after: raise SystemExit(f"FAIL candidate worktree changed by oracle: {status_after}")
    finally:
        run(ROOT,"git","worktree","remove","--force",str(target),check=False)

    print(json.dumps({
      "status":"IG1_SUCCESSOR3_EXACT_CANDIDATE_POSTRUN_VERIFY_PASS",
      "candidate":CANDIDATE,
      "parent":BASE,
      "tree":EXPECTED_TREE,
      "changed_paths":121,
      "reviewed_allowlisted_entries":120,
      "manifest_blob":EXPECTED_MANIFEST_BLOB,
      "reviewed_slice_tests":636,
      "inherited_baseline_tests":140,
      "authority_effect":"NONE",
      "stage2_authorized":False
    },sort_keys=True))

if __name__=="__main__":
    main()
