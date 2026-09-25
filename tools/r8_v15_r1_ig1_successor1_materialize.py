#!/usr/bin/env python3
"""IG-1 successor1 mechanical materializer.

This program is intentionally non-semantic. It copies only independently reviewed
Git tree entries listed in the frozen allowlist, verifies exact path/mode/blob
identity before and after checkout, and invokes the separate integration oracle.
"""
from __future__ import annotations
import argparse, json, pathlib, re, subprocess, sys

ROOT=pathlib.Path(__file__).resolve().parent.parent
ALLOW=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
INVENTORY=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-FULL-CHANGE-INVENTORY.json"
SUMMARY=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json"
ORACLE=ROOT/"governance-runtime"/"test_r8_v15_r1_ig1_integration_oracle.py"
ACTIVATION=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-ACTIVATION.json"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
REJECTED={"20":"053a5c0e70aee45e0e73653d68de3575a83d455c","21":"d3f184380f6cd15582cb3dd6e987895dd895d930","22":"8ecdd17ce80549f87dd15bbe1fc29414272b6253"}
REACCEPTED_IDENTICAL={
 "20":{"governance-runtime/test_r8_v15_r1_implementation_slice20.py"},
 "21":{"governance-runtime/test_r8_v15_r1_implementation_slice21.py"},
 "22":{"governance-runtime/test_r8_v15_r1_implementation_slice22.py"},
}
RESERVED={
 "tools/r8_v15_r1_ig1_successor1_materialize.py",
 "governance-runtime/test_r8_v15_r1_ig1_integration_oracle.py",
 ".github/workflows/r8-v15-r1-ig1-successor1-materialize.yml",
 "governance-r8/R8-V15-R1-IG1-SUCCESSOR1-INTEGRATED-CANDIDATE-MANIFEST.json",
}

def run(*args,check=True,capture=True,env=None):
    p=subprocess.run(args,cwd=ROOT,text=True,capture_output=capture,env=env)
    if check and p.returncode:
        raise SystemExit(f"FAIL command={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def tree_entry(commit,path):
    out=run("git","ls-tree",commit,"--",path).stdout.rstrip("\n")
    if not out:
        return None
    meta,name=out.split("\t",1); mode,typ,blob=meta.split()
    return {"path":name,"mode":mode,"type":typ,"blob":blob}

def index_entry(path):
    out=run("git","ls-files","-s","--",path).stdout.strip()
    if not out:
        return None
    first=out.splitlines()[0]
    meta,name=first.split("\t",1); mode,blob,stage=meta.split()
    return {"path":name,"mode":mode,"blob":blob,"stage":stage}

def ensure_commit(c):
    if run("git","cat-file","-e",c+"^{commit}",check=False).returncode:
        run("git","fetch","--no-tags","origin",c)
    got=run("git","rev-parse",c+"^{commit}").stdout.strip()
    if got!=c: raise SystemExit(f"FAIL source commit identity {c} -> {got}")

def load_json(path):
    return json.loads(path.read_text())

def static_governance_runtime_read_check(blob,path):
    if not path.startswith("governance-runtime/r8_v15_r1_") or path.startswith("governance-runtime/test_"):
        return
    text=run("git","cat-file","blob",blob).stdout
    if "governance-r8/" in text:
        raise SystemExit(f"FAIL runtime implementation contains governance-history path literal: {path}")

def preflight():
    allow=load_json(ALLOW); summary=load_json(SUMMARY)
    if allow["implementation_tree_base"]!=BASE: raise SystemExit("FAIL allowlist base mismatch")
    if summary["collisions_total"]!=0 or summary["conflicting_collisions_total"]!=0:
        raise SystemExit("FAIL collisions exist before materialization")
    claims={}
    for n,rec in allow["per_candidate"].items():
        source=rec["source_commit"]
        if source!=allow["reviewed_candidates"][n]:
            raise SystemExit(f"FAIL source commit not exact roster candidate slice {n}")
        ensure_commit(source)
        for e in rec["selected_entries"]:
            if e["source_commit"]!=source: raise SystemExit(f"FAIL entry source mismatch {e}")
            if e["path"] in RESERVED: raise SystemExit(f"FAIL imported path collides with reserved IG-1 path {e['path']}")
            current=tree_entry(source,e["path"])
            expected={k:e[k] for k in ("path","mode","type","blob")}
            if current!=expected: raise SystemExit(f"FAIL candidate tree-entry mismatch {n} {e['path']}: {current} != {expected}")
            if e["type"]!="blob": raise SystemExit(f"FAIL non-blob selection {e['path']}")
            static_governance_runtime_read_check(e["blob"],e["path"])
            claims.setdefault(e["path"],[]).append((n,e["mode"],e["blob"]))
    if any(len(v)>1 for v in claims.values()):
        raise SystemExit("FAIL collision detected before choosing/materializing bytes")
    for n,pred in REJECTED.items():
        ensure_commit(pred)
        if run("git","merge-base","--is-ancestor",pred,allow["per_candidate"][n]["source_commit"],check=False).returncode!=0:
            raise SystemExit(f"FAIL expected repaired successor lineage not present for slice {n}")
        identical=set()
        for e in allow["per_candidate"][n]["selected_entries"]:
            pe=tree_entry(pred,e["path"])
            if pe and pe["mode"]==e["mode"] and pe["blob"]==e["blob"]:
                identical.add(e["path"])
        if identical!=REACCEPTED_IDENTICAL[n]:
            raise SystemExit(f"FAIL rejected-predecessor identical-entry set changed for slice {n}: {sorted(identical)}")
    # Frozen schema must be byte-identical to exact frozen candidate at the current tree.
    diff=run("git","diff","--exit-code",FROZEN_SCHEMA,"HEAD","--","schemas/governance-r8/v15-r1",check=False)
    if diff.returncode!=0: raise SystemExit("FAIL frozen schema tree differs from exact frozen candidate")
    return allow

def materialize(allow):
    # All collision/source/tree checks have already completed before this point.
    for n in sorted(allow["per_candidate"],key=int):
        rec=allow["per_candidate"][n]
        source=rec["source_commit"]
        for e in rec["selected_entries"]:
            run("git","checkout",source,"--",e["path"])
    # Verify exact staged path+mode+blob after materialization.
    for n,rec in allow["per_candidate"].items():
        for e in rec["selected_entries"]:
            got=index_entry(e["path"])
            expected={"path":e["path"],"mode":e["mode"],"blob":e["blob"],"stage":"0"}
            if got!=expected: raise SystemExit(f"FAIL post-materialization tree-entry mismatch {e['path']}: {got} != {expected}")

def write_manifest(allow):
    manifest={
      "schema":"r8-v15-r1-ig1-successor1-integrated-candidate-manifest/v1",
      "status":"INTEGRATED_IMPLEMENTATION_CANDIDATE_NON_AUTHORITATIVE_PENDING_FRESH_INDEPENDENT_REVIEW",
      "authority_effect":"NONE",
      "implementation_tree_base":BASE,
      "frozen_schema_candidate":FROZEN_SCHEMA,
      "allowlist_path":str(ALLOW.relative_to(ROOT)),
      "materialized_entry_count":sum(len(v["selected_entries"]) for v in allow["per_candidate"].values()),
      "reviewed_candidate_count":len(allow["per_candidate"]),
      "semantic_execution_performed":False,
      "currentness_decision_performed":False,
      "qualification_performed":False,
      "evidence_promotion_performed":False,
      "cross_slice_dependency_authority_granted":False,
      "runtime_qualification":False,
      "release":False,"deployment":False,"production":False,"policy_authority":False,
      "constitutional_authority":False,"root_authority":False,"terminal_authority":False
    }
    p=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-INTEGRATED-CANDIDATE-MANIFEST.json"
    p.write_text(json.dumps(manifest,indent=2)+"\n")
    run("git","add",str(p.relative_to(ROOT)))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight-only",action="store_true")
    args=ap.parse_args()
    if not ACTIVATION.exists() and not args.preflight_only:
        raise SystemExit("FAIL activation artifact absent")
    allow=preflight()
    if args.preflight_only:
        print("IG1_PREFLIGHT_PASS"); return
    activation=load_json(ACTIVATION)
    if activation.get("status")!="ACTIVE_EXPLICIT_USER_APPROVAL":
        raise SystemExit("FAIL activation status")
    materialize(allow)
    write_manifest(allow)
    # The oracle is an exact proposal-reviewed integration-only harness.
    run(sys.executable,str(ORACLE))
    print("IG1_MATERIALIZATION_AND_ORACLE_PASS")

if __name__=="__main__": main()
